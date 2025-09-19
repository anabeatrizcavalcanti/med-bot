import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("A variável de ambiente OPENAI_API_KEY não foi encontrada.")
client = AsyncOpenAI(api_key=api_key)

# MUDANÇA: Prompt totalmente refeito para gerar um JSON com formatação e emojis
ANALYSIS_PROMPT_TEMPLATE = """
Você é Med-Bot, um assistente médico virtual que analisa um resultado de exame alterado.

**Tarefa:** Crie uma análise clara e formatada para o paciente. **Sua resposta DEVE ser um objeto JSON** com as seguintes chaves: `titulo`, `analise`, `recomendacao`, `alerta`.

- `titulo`: Crie um título curto e informativo. Ex: "Leucócitos Acima do Normal".
- `analise`: Explique o que o resultado pode indicar. **Use markdown para negrito (`**palavra**`)** e listas. Comece com um emoji informativo (ex: 🩺, 🩸, 🔬). **NÃO use saudações.**
- `recomendacao`: Sugira qual especialista procurar (ex: Hematologista) e o que fazer. Comece com um emoji de ação (ex: 🧑‍⚕️, 🗓️). Use negrito.
- `alerta`: Uma frase curta enfatizando que isso não é um diagnóstico. Comece com um emoji de alerta (ex: ⚠️).

**Dados do Exame:**
- **Termo:** "{term}"
- **Status:** "{status}"
- **Interpretação Base:** "{interpretation}"

Gere o JSON agora.
"""

async def generate_ai_analysis(term: str, value: str, status: str, interpretation: str) -> dict:
    """Gera uma análise com IA em formato JSON estruturado."""
    prompt = ANALYSIS_PROMPT_TEMPLATE.format(term=term, value=value, status=status, interpretation=interpretation)
    try:
        resp = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é Med-Bot, um assistente médico que cria análises em JSON estruturado."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            response_format={"type": "json_object"},
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:
        print(f"Erro ao gerar análise com IA para '{term}': {e}")
        return {
            "titulo": "Erro na Análise",
            "analise": "Não foi possível gerar uma análise detalhada para este resultado.",
            "recomendacao": "Por favor, tente novamente ou consulte um médico.",
            "alerta": "⚠️ Falha na comunicação com o serviço de IA."
        }
