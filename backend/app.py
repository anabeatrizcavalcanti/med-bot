from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import io
import json

# Importa as funções dos nossos módulos de utils
from utils.term_extractor import extract_medical_terms
from utils.rag_explainer import generate_explanation_for_term

# Carrega o glossário em memória quando a aplicação inicia
try:
    with open("data/glossario.json", "r", encoding="utf-8") as f:
        glossario = json.load(f)
except FileNotFoundError:
    glossario = {}
    print("AVISO: Arquivo glossario.json não encontrado.")


app = FastAPI(title="MedBot API - RAG", version="2.0")

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "MedBot API com RAG rodando 🚀"}

@app.post("/explain-pdf/")
async def explain_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Por favor, envie um arquivo PDF.")

    try:
        # ETAPA 1: Extrair texto do PDF
        pdf_content = await file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        text = "".join(page.extract_text() or "" for page in pdf_reader.pages)

        if not text.strip():
            raise HTTPException(status_code=400, detail="Não foi possível extrair texto do PDF.")

        # ETAPA 2: Extrair a lista de termos médicos com o Gemini
        extracted_terms = await extract_medical_terms(text)
        if "error" in extracted_terms:
            raise HTTPException(status_code=500, detail=extracted_terms)
        
        explanations = []

        # ETAPA 3: RAG (Recuperação + Geração Aumentada)
        for term in extracted_terms:
            # Recuperação (Retrieval): Busca o termo no nosso glossário
            # Normalizamos para minúsculas para uma busca mais flexível
            context = glossario.get(term.lower().strip())
            
            explanation_text = "Nenhuma explicação encontrada no nosso glossário para este termo."
            
            if context:
                # Geração Aumentada (Augmented Generation): Gera a explicação com o Gemini
                explanation_text = await generate_explanation_for_term(term, context)
            
            explanations.append({
                "term": term,
                "explanation": explanation_text
            })

        return {"filename": file.filename, "explanations": explanations}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro inesperado: {str(e)}")