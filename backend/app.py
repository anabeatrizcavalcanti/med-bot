from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import io
import re

from utils.data_extractor import extract_structured_data
from utils.interpretador import interpretar_exame
from utils.analysis_generator import generate_ai_analysis_rag, generate_ai_analysis_no_rag

app = FastAPI(title="MedBot API - Analisador de Resultados", version="5.0")

origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "MedBot API com Análise de Resultados rodando."}

def merge_related_results(results):
    merged_results = []
    processed_indices = set()
    for i, current_result in enumerate(results):
        if i in processed_indices: continue
        base_name = current_result.get("exame", "")
        if not base_name: continue
        related_indices = [i]
        for j, other_result in enumerate(results):
            other_exam_name = other_result.get("exame", "")
            if not other_exam_name: continue
            if i != j and j not in processed_indices and (base_name in other_exam_name or other_exam_name in base_name):
                related_indices.append(j)
        if len(related_indices) > 1:
            valid_results = [results[k] for k in related_indices if "valor" in results[k] and "unidade" in results[k]]
            if not valid_results: continue
            combined_valor = " / ".join([r.get("valor", "") for r in valid_results])
            combined_unidade = " / ".join([r.get("unidade", "") for r in valid_results])
            base_exam_name = min([r.get("exame", "") for r in valid_results], key=len)
            merged_results.append({"exame": base_exam_name, "valor": combined_valor, "unidade": combined_unidade})
            processed_indices.update(related_indices)
        else:
            merged_results.append(current_result)
            processed_indices.add(i)
    return merged_results

@app.post("/analyze-pdf/")
async def analyze_pdf(
    file: UploadFile = File(...),
    idade: int = Form(...),
    sexo: str = Form(...),
    rag: bool = Form(True) 
):
    try:
        pdf_content = await file.read()
        text = "".join(page.extract_text() or "" for page in PyPDF2.PdfReader(io.BytesIO(pdf_content)).pages)

        structured_data = await extract_structured_data(text)

        analyzed_groups = []
        for group in structured_data.get("grupos", []):
            resultados_do_grupo = group.get("resultados", [])
            merged_results_list = merge_related_results(resultados_do_grupo)
            interpreted_results = []

            for result in merged_results_list:
                exam_name = result.get("exame")
                if not exam_name: continue

                valor_str = str(result.get("valor", "")).strip()
                valor_numerico_str = re.split(r'\s|/', valor_str)[0]
                
                valor_float = None
                try:
                    cleaned_valor = re.sub(r"[^0-9,.]", "", valor_numerico_str).replace(",", ".")
                    if cleaned_valor: valor_float = float(cleaned_valor)
                except (ValueError, TypeError): pass

                interpretacao, status = interpretar_exame(result["exame"], valor_float, idade, sexo)
                
                analise_ia = None
                if status in ["alto", "baixo"]:
                    if rag:
                        analise_ia = await generate_ai_analysis_rag(result["exame"], valor_str, status, interpretacao, idade, sexo)
                    else:
                        analise_ia = await generate_ai_analysis_no_rag(result["exame"], valor_str, status, idade, sexo)
                
                interpreted_results.append({
                    "exame": result["exame"],
                    "valor": valor_str,
                    "unidade": result.get("unidade", ""),
                    "interpretacao": interpretacao,
                    "analise_ia": analise_ia,
                    "status_class": status,
                })
            
            if interpreted_results:
                analyzed_groups.append({
                    "group_name": group.get("grupo", "Grupo Desconhecido"),
                    "results": interpreted_results,
                })

        # Adiciona o modo RAG usado à resposta
        return {"filename": file.filename, "groups": analyzed_groups, "rag_mode_used": rag}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro inesperado no servidor: {str(e)}")