import os
from openai import AsyncOpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

EXPLAINER_PROMPT_TEMPLATE = """
Você é um assistente médico virtual chamado Med-Bot. Sua função é explicar termos de exames de forma
simples, clara e acolhedora para um paciente leigo.

Use APENAS as informações fornecidas no "Contexto do Glossário" abaixo para explicar o termo médico solicitado.
Não adicione informações externas ou que não estejam no contexto.
Comece a explicação de forma direta.

Termo para Explicar: "{term}"

Contexto do Glossário:
---
{context}
---

Explicação Simplificada:
"""

async def generate_explanation_for_term(term: str, context: dict) -> str:
    if not OPENAI_API_KEY:
        return "Erro: Chave de API da OpenAI não configurada."

    context_str = (
        f"Descrição: {context.get('descricao', 'N/A')}\n"
        f"Interpretação Geral: {context.get('interpretacao', 'N/A')}"
    )

    prompt = EXPLAINER_PROMPT_TEMPLATE.format(term=term, context=context_str)

    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um explicador de exames médicos."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        return resp.choices[0].message.content
    except Exception as e:
        print(f"Erro ao gerar explicação (OpenAI) para '{term}': {e}")
        return "Não foi possível gerar uma explicação para este termo."