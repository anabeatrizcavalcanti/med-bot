import os
import httpx
import json
from dotenv import load_dotenv
import google.generativeai as genai


# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- MUDANÇA 1: Usar a nova chave de API do Gemini ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- MUDANÇA 2: Usar a URL da API do Gemini ---
# Note o modelo 'gemini-2.0-flash', que é rápido e eficiente para essa tarefa.
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# O prompt continua excelente e não precisa de mudanças.
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
    if not GEMINI_API_KEY:
        raise ValueError("A chave da API do Gemini não foi encontrada. Verifique o arquivo .env")

    # --- MUDANÇA 3: A chave agora é passada no URL como um parâmetro 'key' ---
    request_url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"

    # O cabeçalho é mais simples, apenas o Content-Type.
    headers = {
        "Content-Type": "application/json",
    }

    # --- MUDANÇA 4: O formato do corpo da requisição (payload) é diferente ---
    payload = {
        "contents": [
            {
                "parts": [
                    # O prompt vai dentro da chave "text"
                    {"text": PROMPT_TEMPLATE.format(text=text)}
                ]
            }
        ],
        # Configuração para garantir uma resposta mais consistente e determinística
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json", # Pede explicitamente um JSON!
        }
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # A requisição agora usa a nova URL e não precisa mais da chave no header
            response = await client.post(request_url, headers=headers, json=payload)
            response.raise_for_status()

            response_data = response.json()
            
            # --- MUDANÇA 5: O caminho para extrair o conteúdo da resposta mudou ---
            # A resposta do Gemini vem dentro de 'candidates'
            content_str = response_data["candidates"][0]["content"]["parts"][0]["text"]
            
            content_json = json.loads(content_str)
            
            return content_json.get("termos", [])

        except httpx.HTTPStatusError as e:
            print(f"Erro na API do Gemini: {e.response.text}")
            return {"error": f"Erro na API: {e.response.status_code}", "details": e.response.text}
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            print(f"Erro ao processar a resposta JSON: {e}")
            # Adicionado para depuração: imprime a resposta que causou o erro
            print(f"Resposta recebida: {response_data}")
            return {"error": "A resposta da API não estava no formato esperado."}
        except Exception as e:
            print(f"Um erro inesperado ocorreu: {e}")
            return {"error": "Ocorreu um erro inesperado no servidor."}
        
async def validate_document_context(text: str) -> bool:
    """
    Usa o Gemini para verificar se o texto parece ser de um documento médico.
    Retorna True se for, False caso contrário.
    """
    # Usando um modelo rápido para a tarefa de classificação
    model = genai.GenerativeModel('gemini-2.0-flash')

    # Prompt direto para uma resposta simples (SIM/NÃO)
    prompt = f"""
    Analise o texto a seguir e determine se ele é um documento da área da saúde
    (como um exame de sangue, laudo, receita, etc.).
    Responda APENAS com "SIM" ou "NÃO".

    Texto:
    ---
    {text[:2000]}
    ---
    """ # Limitamos a 2000 caracteres para ser rápido e econômico

    try:
        response = await model.generate_content_async(prompt)
        answer = response.text.strip().upper()
        
        if "SIM" in answer:
            return True
        return False
    except Exception as e:
        print(f"Erro durante a validação do documento: {e}")
        return False # Se houver erro na API, consideramos inválido por segurança
