import os
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Configurações do modelo para a geração da explicação
generation_config = {
    "temperature": 0.3,
    "top_p": 1,
    "top_k": 1,
}

# Prompt para a etapa de Geração Aumentada (RAG)
EXPLAINER_PROMPT_TEMPLATE = """
Você é um assistente médico virtual chamado Med-Bot. Sua função é explicar termos de exames de forma
simples, clara e acolhedora para um paciente leigo.

Use APENAS as informações fornecidas no "Contexto do Glossário" abaixo para explicar o termo médico solicitado.
Não adicione informações externas ou que não estejam no contexto.
Comece a explicação de forma direta, sem usar frases como "com base no contexto".

Termo para Explicar: "{term}"

Contexto do Glossário:
---
{context}
---

Explicação Simplificada:
"""

# Inicializa o modelo
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash", # ou outro modelo de sua preferência
    generation_config=generation_config
)

async def generate_explanation_for_term(term: str, context: dict) -> str:
    """
    Usa o Gemini para gerar uma explicação amigável para um termo médico
    baseado no contexto fornecido do glossário (etapa RAG).
    """
    if not GEMINI_API_KEY:
        return "Erro: Chave de API do Gemini não configurada."

    try:
        # Formata o contexto do glossário para incluir no prompt
        context_str = f"Descrição: {context.get('descricao', 'N/A')}\n" \
                      f"Interpretação Geral: {context.get('interpretacao', 'N/A')}"

        prompt = EXPLAINER_PROMPT_TEMPLATE.format(term=term, context=context_str)
        
        response = await model.generate_content_async(prompt)
        
        return response.text

    except Exception as e:
        print(f"Erro ao gerar explicação para o termo '{term}': {e}")
        return "Não foi possível gerar uma explicação para este termo."