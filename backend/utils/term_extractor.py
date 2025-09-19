import os
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Carrega variáveis de ambiente
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

PROMPT_TEMPLATE = """
Você é um especialista em terminologia médica e sua única tarefa é analisar um texto
extraído de um documento médico. Identifique e liste absolutamente todos os termos
médicos, farmacêuticos e relacionados à saúde presentes no texto.

Sua resposta DEVE SER ESTRITAMENTE um objeto JSON contendo uma única chave "termos",
que é um array de strings. Cada string deve ser um termo médico identificado.
Não inclua explicações, frases introdutórias, ou qualquer outro texto fora do formato JSON especificado.

Texto para análise:
---
{text}
---
"""

async def extract_medical_terms(text: str) -> list[str]:
    if not OPENAI_API_KEY:
        raise ValueError("A chave da API da OpenAI não foi encontrada. Verifique o arquivo .env")

    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um especialista em terminologia médica."},
            {"role": "user", "content": PROMPT_TEMPLATE.format(text=text)},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    content = resp.choices[0].message.content
    data = json.loads(content)
    termos = data.get("termos", [])

    # DEBUG: imprime todos os termos extraídos no console
    print("=== TERMOS EXTRAÍDOS PELO GPT ===")
    for t in termos:
        print(f"- {repr(t)}")
    print("=================================")

    return termos



async def validate_document_context(text: str) -> bool:
    """Classifica se o texto é (SIM) um documento da área da saúde."""
    if not OPENAI_API_KEY:
        return False

    prompt = f"""
    Analise o texto a seguir e determine se ele é um documento da área da saúde
    (como um exame de sangue, laudo, receita, etc.).
    Responda APENAS com "SIM" ou "NÃO".

    Texto:
    ---
    {text[:2000]}
    ---
    """

    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um classificador de documentos médicos."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    answer = resp.choices[0].message.content.strip().upper()
    return "SIM" in answer