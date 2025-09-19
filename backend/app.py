from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import io
import json
import unicodedata

# Importa as funções, incluindo a nova de validação
from utils.term_extractor import extract_medical_terms, validate_document_context
from utils.rag_explainer import generate_explanation_for_term

# Carrega o glossário em memória quando a aplicação inicia
try:
    with open("data/glossario.json", "r", encoding="utf-8") as f:
        glossario = json.load(f)
except FileNotFoundError:
    glossario = {}
    print("AVISO: Arquivo glossario.json não encontrado.")

def normalize_term(term: str) -> str:
    """
    Normaliza um termo para comparar com o glossário:
    - Converte para minúsculas
    - Remove acentos
    - Remove espaços extras
    """
    if not term:
        return ""
    nfkd = unicodedata.normalize("NFKD", term)
    only_ascii = "".join(c for c in nfkd if not unicodedata.combining(c))
    normalized = only_ascii.lower().strip()

    # Mapeia siglas
    aliases = {
        "vcm": "v.c.m",
        "v.c.m": "v.c.m",
        "hcm": "h.c.m",
        "h.c.m": "h.c.m",
        "chcm": "c.h.c.m",
        "c.h.c.m": "c.h.c.m",
    }

    # Remove espaços extras
    normalized = normalized.replace(" ", "")

    return aliases.get(normalized, normalized)

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
    return {"message": "MedBot API com RAG rodando."}

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

        # --- NOVA LÓGICA DE VALIDAÇÃO DO DOCUMENTO ---
        is_medical = await validate_document_context(text)
        if not is_medical:
            # Se não for médico, retorna um erro 400 (Bad Request)
            raise HTTPException(status_code=400, detail="O documento enviado não parece ser um exame médico ou não se aplica ao contexto.")
        # --- FIM DA NOVA LÓGICA ---

        # ETAPA 2: Extrair a lista de termos médicos com o Gemini
        extracted_terms = await extract_medical_terms(text)
        if "error" in extracted_terms:
            raise HTTPException(status_code=500, detail=extracted_terms)
        
        explanations = []

        # ETAPA 3: RAG (Recuperação + Geração Aumentada)
        for term in extracted_terms:
            normalized = normalize_term(term)
            context = glossario.get(normalized)

            explanation_text = "Nenhuma explicação encontrada no nosso glossário para este termo."

            if context:
                explanation_text = await generate_explanation_for_term(term, context)

            explanations.append({
                "term": term,  # mantém o termo original para exibir ao usuário
                "explanation": explanation_text
            })

        return {"filename": file.filename, "explanations": explanations}

    except HTTPException as http_exc:
        # Garante que as exceções HTTP que nós criamos sejam repassadas corretamente
        raise http_exc
    except Exception as e:
        # Captura outras exceções inesperadas
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro inesperado: {str(e)}")