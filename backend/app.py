from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import io
import re

from utils.data_extractor import extract_structured_data
from utils.interpretador import interpretar_exame
from utils.analysis_generator import generate_ai_analysis

app = FastAPI(title="MedBot API - Analisador de Resultados", version="4.0")

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
    """Agrupa resultados que são o mesmo exame com unidades diferentes (ex: Basófilos % e /mm³)."""
    merged_results = []
    processed_indices = set()

    for i, current_result in enumerate(results):
        if i in processed_indices:
            continue
        
        base_name = current_result["exame"]
        related_indices = [i]
        
        for j, other_result in enumerate(results):
            if i != j and j not in processed_indices:
                # Se um nome de exame contém o outro, considera-os relacionados
                if base_name in other_result["exame"] or other_result["exame"] in base_name:
                    related_indices.append(j)

        if len(related_indices) > 1:
            # Junta os valores e unidades
            combined_valor = " / ".join([results[k]["valor"] for k in related_indices])
            combined_unidade = " / ".join([results[k]["unidade"] for k in related_indices])
            # Usa o nome mais curto como nome base
            base_exam_name = min([results[k]["exame"] for k in related_indices], key=len)

            merged_results.append({
                "exame": base_exam_name,
                "valor": combined_valor,
                "unidade": combined_unidade
            })
            processed_indices.update(related_indices)
        else:
            merged_results.append(current_result)
            processed_indices.add(i)
            
    return merged_results

@app.post("/analyze-pdf/")
async def analyze_pdf(
    file: UploadFile = File(...),
    idade: int = Form(...),
    sexo: str = Form(...)
):
    try:
        pdf_content = await file.read()
        text = "".join(page.extract_text() or "" for page in PyPDF2.PdfReader(io.BytesIO(pdf_content)).pages)
        if not text.strip():
            raise HTTPException(status_code=400, detail="Não foi possível extrair texto do PDF.")

        structured_data = await extract_structured_data(text)
        if "error" in structured_data or not structured_data.get("grupos"):
            raise HTTPException(status_code=500, detail=structured_data.get("error", "IA não conseguiu estruturar os dados do exame."))

        analyzed_groups = []
        for group in structured_data["grupos"]:
            
            # MUDANÇA: Agrupa resultados antes de interpretar
            merged_results_list = merge_related_results(group["resultados"])
            
            interpreted_results = []
            for result in merged_results_list:
                valor_str = str(result.get("valor", "")).strip()
                # Pega apenas a primeira parte numérica para a análise
                valor_numerico_str = re.split(r'\s|/', valor_str)[0]
                
                valor_float = None
                try:
                    cleaned_valor = re.sub(r"[^0-9,.]", "", valor_numerico_str).replace(",", ".")
                    if cleaned_valor:
                        valor_float = float(cleaned_valor)
                except (ValueError, TypeError):
                    pass # Mantém valor_float como None

                # MUDANÇA: A análise só ocorre se o termo estiver no glossário
                interpretacao, status = interpretar_exame(result["exame"], valor_float, idade, sexo)
                
                analise_ia = None # A análise da IA é opcional
                if status in ["alto", "baixo"]:
                    # Se estiver fora do normal, gera uma análise mais profunda com IA
                    analise_ia = await generate_ai_analysis(result["exame"], valor_str, status, interpretacao)
                
                interpreted_results.append({
                    "exame": result["exame"],
                    "valor": valor_str,
                    "unidade": result.get("unidade", ""),
                    "interpretacao": interpretacao,
                    "analise_ia": analise_ia, # Pode ser None
                    "status_class": status, # pode ser "normal", "alto", "baixo" ou "indeterminado"
                })
            
            analyzed_groups.append({
                "group_name": group["grupo"],
                "results": interpreted_results,
            })

        return {"filename": file.filename, "groups": analyzed_groups}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro inesperado no servidor: {str(e)}")
