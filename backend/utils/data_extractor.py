import os
import json
import re
from pathlib import Path
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("A variável de ambiente OPENAI_API_KEY não foi encontrada.")
client = AsyncOpenAI(api_key=api_key)

# Carrega o glossário para guiar a IA
GLOSSARIO_FILE = Path(__file__).resolve().parent.parent / "data" / "glossario.json"
with open(GLOSSARIO_FILE, "r", encoding="utf-8") as f:
    _glossario = json.load(f)

LISTA_TERMOS = list(_glossario.keys())

# Prompt que usa a lista de termos do glossário
EXTRACTOR_PROMPT = f"""
Você é um assistente especializado em extrair dados de exames médicos de laudos laboratoriais.

Sua tarefa:
- Ler o texto fornecido de um exame.
- Identificar os diferentes grupos (como Eritrograma, Leucograma, Bioquímica).
- Para cada grupo, extrair os resultados em formato JSON conforme abaixo.

Formato de saída (STRICT JSON, sem explicações fora do JSON):
{{
  "grupos": [
    {{
      "grupo": "Nome do Grupo",
      "resultados": [
        {{
          "exame": "Nome do exame (deve ser exatamente igual a uma das chaves do glossário fornecido)",
          "valor": "Valor encontrado (número ou texto)",
          "unidade": "Unidade do exame (ex: /mm³, g/dL, %)"
        }}
      ]
    }}
  ]
}}

Regras IMPORTANTES:
- O campo "exame" deve ser escolhido EXCLUSIVAMENTE da lista de termos do glossário abaixo.
- Ignore cabeçalhos de tabela como "Resultado", "Unidade", "Valores de Referência".
- Inclua apenas os exames reais com seus valores.
- Não inclua os valores de referência.
- SUA RESPOSTA DEVE SER UM ÚNICO OBJETO JSON VÁLIDO COMEÇANDO COM {{ E TERMINANDO COM }}.

Glossário disponível (lista de termos válidos):
{LISTA_TERMOS}
"""

async def extract_structured_data(text: str) -> dict:
    if not api_key:
        raise ValueError("A variável de ambiente OPENAI_API_KEY não foi encontrada.")

    # limitar tamanho se necessário
    truncated_text = text[:12000]

    try:
        resp = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um assistente que extrai dados estruturados de exames médicos."},
                {"role": "user", "content": EXTRACTOR_PROMPT + f"\\n\\nTexto do exame:\\n---\\n{truncated_text}\\n---"},
            ],
            temperature=0,
            response_format={"type": "json_object"}  # força JSON válido
        )

        content = resp.choices[0].message.content.strip()
        data = json.loads(content)
        return data

    except json.JSONDecodeError:
        # Tenta corrigir JSON malformado que às vezes vem com ```json ... ```
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError as e:
                 print(f"Erro de JSON mesmo após correção: {e}")
                 raise e
        else:
            print(f"Não foi possível encontrar um objeto JSON na resposta da IA: {content}")
            raise
    except Exception as e:
        print(f"Erro inesperado no data_extractor: {e}")
        raise

