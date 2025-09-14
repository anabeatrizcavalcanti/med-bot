from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="MedBot API", version="0.1")

class ExamInput(BaseModel):
    text: str

class ExamOutput(BaseModel):
    explanation: str
    question: str
    disclaimer: str = "Essas informações são apenas educativas. Consulte um profissional de saúde."

@app.get("/")
def root():
    return {"message": "MedBot API está rodando 🚀"}

@app.post("/explain", response_model=ExamOutput)
def explain_exam(exam: ExamInput):
    """
    Endpoint inicial que só retorna placeholders.
    Depois vamos integrar glossário + LLM.
    """
    return ExamOutput(
        explanation=f"Explicação simplificada para: {exam.text}",
        question="Pergunte ao seu médico como interpretar esse resultado."
    )