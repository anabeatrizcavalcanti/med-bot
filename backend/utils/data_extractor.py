import os
import json
import re
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# Carrega a chave da API
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("A variável de ambiente OPENAI_API_KEY não foi encontrada.")
client = AsyncOpenAI(api_key=api_key)

EXTRACTOR_PROMPT = """
Você é um assistente especializado em extrair dados de exames médicos de laudos laboratoriais.

Sua tarefa:
- Ler o texto fornecido de um exame.
- Identificar os diferentes grupos (como Eritrograma, Leucograma, Bioquímica).
- Para cada grupo, extrair os resultados em formato JSON conforme abaixo.

Formato de saída (STRICT JSON, sem explicações fora do JSON):
{
  "grupos": [
    {
      "grupo": "Nome do Grupo",
      "resultados": [
        {
          "exame": "Nome do exame (ex: Hemácias)",
          "valor": "Valor encontrado (número ou texto)",
          "unidade": "Unidade do exame (ex: /mm³, g/dL, %)"
        }
      ]
    }
  ]
}

Regras IMPORTANTES:
- Ignore cabeçalhos de tabela como "Resultado", "Unidade", "Valores de Referência".
- O campo "exame" NUNCA deve ser "Resultado", "Unidade" ou "Valores de Referência".
- Inclua apenas os exames reais com seus valores.
- Não inclua os valores de referência.
- SUA RESPOSTA DEVE SER UM ÚNICO OBJETO JSON VÁLIDO COMEÇANDO COM { E TERMINANDO COM }.
"""

async def extract_structured_data(text: str) -> dict:
    if not api_key:
        raise ValueError("A variável de ambiente OPENAI_API_KEY não foi encontrada.")

    # limitar tamanho se necessário
    truncated_text = text[:12000]

    resp = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Você é um assistente que extrai dados estruturados de exames médicos."},
            {"role": "user", "content": EXTRACTOR_PROMPT + f"\n\nTexto do exame:\n---\n{truncated_text}\n---"},
        ],
        temperature=0,
        response_format={"type": "json_object"}  # força JSON válido
    )

    content = resp.choices[0].message.content.strip()

    import re, json
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
        else:
            raise

    return data
