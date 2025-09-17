from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import re
from utils.interpretador import interpretar_exame

app = FastAPI(title="MedBot API", version="0.4")

class ExamInput(BaseModel):
    text: str   
    idade: int
    sexo: str 

class ExamResult(BaseModel):
    termo: str
    explanation: str
    question: str

class ExamsOutput(BaseModel):
    results: List[ExamResult]
    disclaimer: str = "Essas informações são apenas educativas. Consulte um profissional de saúde."

@app.get("/")
def root():
    return {"message": "MedBot API rodando com glossário integrado 🚀"}

@app.post("/explain", response_model=ExamsOutput)
def explain_exam(exam: ExamInput):
    """
    Analisa um ou vários exames enviados em texto, separados por ';'.
    """
    results = []
    exames = exam.text.split(";")

    for e in exames:
        try:
            termo, resto = e.split(":", 1)
            match = re.search(r"\d+(?:[.,]\d+)?", resto)
            if not match:
                raise ValueError("valor não encontrado")
            valor = float(match.group(0).replace(",", "."))
        except Exception:
            results.append(
                ExamResult(
                    termo=e.strip(),
                    explanation="Não consegui interpretar este exame. Use o formato: 'Nome: valor unidade'",
                    question="Pergunte ao médico como interpretar este exame."
                )
            )
            continue

        explicacao = interpretar_exame(termo.strip(), valor, exam.idade, exam.sexo)
        results.append(
            ExamResult(
                termo=termo.strip(),
                explanation=explicacao,
                question=f"Pergunte ao seu médico se esse valor de {termo.strip()} exige alguma atenção especial."
            )
        )

    return ExamsOutput(results=results)