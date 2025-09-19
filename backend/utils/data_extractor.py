import os
import json
from openai import AsyncOpenAI

# Carrega a chave da API
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("A variável de ambiente OPENAI_API_KEY não foi encontrada.")
client = AsyncOpenAI(api_key=api_key)

EXTRACTOR_PROMPT = """
Você é um especialista em processar documentos de exames de laboratório. Sua tarefa é ler o texto de um exame e extrair os dados de forma estruturada.

Sua resposta DEVE SER ESTRITAMENTE um objeto JSON contendo uma chave "grupos".
"grupos" deve ser uma lista, onde cada item representa uma seção do exame (ex: "HEMOGRAMA COMPLETO", "PERFIL LIPÍDICO").

Cada item de grupo deve ter duas chaves:
1. "grupo": O nome da seção do exame.
2. "resultados": Uma lista de resultados encontrados nessa seção.

Cada item em "resultados" deve conter:
- "exame": O nome exato do componente do exame (ex: "Hemácias", "Colesterol HDL").
- "valor": O valor numérico ou textual encontrado para o paciente.
- "unidade": A unidade de medida associada ao valor (ex: "milhões/mm³", "g/dL").

IGNORE completamente as colunas de "Valores de referência". Foque apenas nos resultados do paciente.

Texto do Exame:
---
{text}
---
"""

async def extract_structured_data(text: str) -> dict:
    """
    Usa a IA para extrair dados estruturados (grupos, exames, valores, unidades) do texto de um PDF.
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um especialista em extração de dados de exames de laboratório."},
                {"role": "user", "content": EXTRACTOR_PROMPT.format(text=text[:12000])} # Limita o texto
            ],
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        parsed_json = json.loads(content)

        if "grupos" not in parsed_json or not isinstance(parsed_json["grupos"], list):
            return {"grupos": [], "error": "A IA retornou um formato de JSON inesperado."}
            
        return parsed_json

    except Exception as e:
        print(f"Erro ao extrair dados estruturados: {e}")
        return {"grupos": [], "error": f"Falha ao comunicar com a IA para estruturar os dados: {e}"}