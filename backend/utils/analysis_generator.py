import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("A variável de ambiente OPENAI_API_KEY não foi encontrada.")
client = AsyncOpenAI(api_key=api_key)

# Versão 1: Prompt que USA o glossário (RAG)
RAG_PROMPT_TEMPLATE = """
Você é Med-Bot, um assistente médico que analisa um resultado de exame alterado, **usando a 'Interpretação Base' como fonte principal de verdade**.

**Tarefa:** Crie uma análise personalizada para o paciente, em JSON.

- `titulo`: Crie um título curto. Ex: "Hemácias Abaixo do Normal".
- `analise`: Usando seu conhecimento, explique o que o valor `{value}` pode indicar, considerando que o paciente tem `{idade}` anos, é do sexo `{sexo}`, e o resultado está `{status}`.  **Use markdown para negrito (`**palavra**`)** e listas. Comece com um emoji informativo (ex: 🩺, 🩸, 🔬). **NÃO use saudações.**
- `recomendacao`: Sugira qual especialista procurar (ex: Hematologista) e o que fazer. Comece com um emoji de ação (ex: 🧑‍⚕️, 🗓️). Use negrito.
- `alerta`: Uma frase curta enfatizando que isso não é um diagnóstico. Comece com um emoji de alerta (ex: ⚠️).

**Dados do Exame:**
- **Termo:** "{term}"
- **Resultado do Paciente:** "{value}"
- **Status:** "{status}"
- **Idade:** "{idade}"
- **Sexo:** "{sexo}"
- **Interpretação Base (Fonte de Verdade):** "{interpretation}"

Gere o JSON.
"""

async def generate_ai_analysis_rag(term: str, value: str, status: str, interpretation: str, idade: int, sexo: str) -> dict:
    """Gera uma análise com IA usando o glossário (RAG)."""
    prompt = RAG_PROMPT_TEMPLATE.format(
        term=term, value=value, status=status, interpretation=interpretation, idade=idade, sexo=sexo
    )
    try:
        resp = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você cria análises em JSON baseadas estritamente no contexto fornecido."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:
        return {"titulo": "Erro na Análise RAG", "analise": str(e), "recomendacao": "", "alerta": ""}

# Versão 2: Prompt que NÃO usa o glossário (Conhecimento Geral da IA)
NO_RAG_PROMPT_TEMPLATE = """
Você é Med-Bot, um assistente médico que analisa um resultado de exame alterado, **usando seu conhecimento médico geral**.

**Tarefa:** Crie uma análise personalizada para o paciente, em JSON.

- `titulo`: Crie um título curto. Ex: "Hemácias Abaixo do Normal".
- `analise`: Usando seu conhecimento, explique o que o valor `{value}` pode indicar, considerando que o paciente tem `{idade}` anos, é do sexo `{sexo}`, e o resultado está `{status}`.  **Use markdown para negrito (`**palavra**`)** e listas. Comece com um emoji informativo (ex: 🩺, 🩸, 🔬). **NÃO use saudações.**
- `recomendacao`: Sugira qual especialista procurar (ex: Hematologista) e o que fazer. Comece com um emoji de ação (ex: 🧑‍⚕️, 🗓️). Use negrito.
- `alerta`: Uma frase curta enfatizando que isso não é um diagnóstico. Comece com um emoji de alerta (ex: ⚠️).

**Dados do Exame:**
- **Termo:** "{term}"
- **Resultado do Paciente:** "{value}"
- **Status:** "{status}"
- **Idade:** "{idade}"
- **Sexo:** "{sexo}"

Gere o JSON.
"""

async def generate_ai_analysis_no_rag(term: str, value: str, status: str, idade: int, sexo: str) -> dict:
    """Gera uma análise com IA sem usar o glossário."""
    prompt = NO_RAG_PROMPT_TEMPLATE.format(
        term=term, value=value, status=status, idade=idade, sexo=sexo
    )
    try:
        resp = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você cria análises em JSON usando seu conhecimento médico geral."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            response_format={"type": "json_object"},
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:
        return {"titulo": "Erro na Análise Sem RAG", "analise": str(e), "recomendacao": "", "alerta": ""}

