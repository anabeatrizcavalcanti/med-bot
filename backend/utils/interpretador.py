import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GLOSSARIO_PATH = os.path.join(BASE_DIR, "..", "data", "glossario.json")

with open(GLOSSARIO_PATH, "r", encoding="utf-8") as f:
    glossario = json.load(f)

def parse_interval(intervalo: str):
    # (Sua função de parse continua a mesma)
    intervalo = intervalo.replace(",", ".")
    intervalo = re.sub(r"(?<=\d)\.(?=\d{3})", "", intervalo)
    numeros = re.findall(r"\d+(?:\.\d+)?", intervalo)
    if "<" in intervalo and numeros: return None, float(numeros[0])
    if ">" in intervalo and numeros: return float(numeros[0]), None
    if len(numeros) >= 2: return float(numeros[0]), float(numeros[1])
    if len(numeros) == 1: return float(numeros[0]), float(numeros[0])
    return None, None

def interpretar_exame(termo: str, valor: float, idade: int, sexo: str) -> tuple[str, str]:
    termo_lower = termo.lower().strip()
    glossario_entry = glossario.get(termo_lower)

    # MUDANÇA: Lógica mais clara para quando o termo não é encontrado
    if not glossario_entry:
        return f"O termo '{termo}' não foi encontrado em nossa base de dados para análise.", "indeterminado"
    
    # Se o valor não for numérico, não podemos interpretar
    if valor is None:
        return glossario_entry.get("descricao", "Descrição não disponível."), "normal"

    desc = glossario_entry.get("descricao", "Descrição não disponível.")
    interpretacao = glossario_entry.get("interpretacao", "")
    referencias = glossario_entry.get("referencias", {})
    ref_sexo = referencias.get(sexo.lower(), referencias.get("geral", {}))
    
    faixa_escolhida = None
    for faixa, limites in ref_sexo.items():
        if "+" in faixa and idade >= int(faixa.replace("+", "")):
            faixa_escolhida = limites
            break
        elif "-" in faixa:
            ini, fim = faixa.split("-")
            if int(ini) <= idade <= int(fim):
                faixa_escolhida = limites
                break
    if not faixa_escolhida and "padrão" in ref_sexo:
        faixa_escolhida = ref_sexo["padrão"]

    if not faixa_escolhida:
        return f"{desc} {interpretacao}", "normal"

    minimo, maximo = parse_interval(faixa_escolhida)
    status_text = "dentro do normal"
    status_code = "normal"

    if minimo is not None and maximo is not None and minimo == maximo:
         if valor != minimo:
            status_text = "diferente do valor de referência"
            status_code = "alto" # Trata como alterado
    elif minimo is not None and valor < minimo:
        status_text = "abaixo do normal"
        status_code = "baixo"
    elif maximo is not None and valor > maximo:
        status_text = "acima do normal"
        status_code = "alto"
        
    resultado_final = f"Seu resultado foi **{valor}**, que está **{status_text}**. (Referência: {faixa_escolhida}). {interpretacao}"
    return resultado_final, status_code
