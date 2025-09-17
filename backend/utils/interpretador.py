import json
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLOSSARIO_PATH = os.path.join(BASE_DIR, "data", "glossario.json")

with open(GLOSSARIO_PATH, "r", encoding="utf-8") as f:
    glossario = json.load(f)

def parse_interval(intervalo: str):
    """
    Recebe strings como:
    - '12,0 a 15,8 g/dL'
    - '13.5 - 17.5'
    - '< 100 mg/dL'
    - '> 50'
    - '140.000 a 450.000/mm³'
    Retorna (min, max) floats (ou None se não aplicável).
    """
    intervalo = intervalo.replace(",", ".")
    intervalo = re.sub(r"(?<=\d)\.(?=\d{3})", "", intervalo)

    if "<" in intervalo:
        numeros = re.findall(r"\d+(?:\.\d+)?", intervalo)
        if numeros:
            return None, float(numeros[0])

    if ">" in intervalo:
        numeros = re.findall(r"\d+(?:\.\d+)?", intervalo)
        if numeros:
            return float(numeros[0]), None

    numeros = re.findall(r"\d+(?:\.\d+)?", intervalo)
    if len(numeros) >= 2:
        return float(numeros[0]), float(numeros[1])

    return None, None


def interpretar_exame(termo: str, valor: float, idade: int, sexo: str) -> str:
    """
    Interpreta o exame baseado no glossário, idade e sexo.
    """
    termo_lower = termo.lower()
    if termo_lower not in glossario:
        return f"O termo '{termo}' não foi encontrado no glossário."

    referencias = glossario[termo_lower].get("referencias", {})
    desc = glossario[termo_lower]["descricao"]
    interpretacao = glossario[termo_lower]["interpretacao"]

    ref_sexo = referencias.get(sexo.lower(), {})
    faixa_escolhida = None
    for faixa, limites in ref_sexo.items():
        if "+" in faixa:  # Ex: "70+"
            if idade >= int(faixa.replace("+", "")):
                faixa_escolhida = limites
        elif "-" in faixa:  # Ex: "18-70" ou "1-120"
            ini, fim = faixa.split("-")
            if int(ini) <= idade <= int(fim):
                faixa_escolhida = limites
        elif faixa.isdigit():  # faixa única (ex: "13")
            if idade == int(faixa):
                faixa_escolhida = limites

    if not faixa_escolhida:
        return f"{desc} — valor informado: {valor}. {interpretacao}"

    minimo, maximo = parse_interval(faixa_escolhida)
    if minimo is not None and maximo is not None:
        if valor < minimo:
            status = "abaixo do normal"
        elif valor > maximo:
            status = "acima do normal"
        else:
            status = "dentro do intervalo esperado"
    elif minimo is None and maximo is not None: 
        if valor > maximo:
            status = "acima do normal"
        else:
            status = "dentro do esperado"
    elif minimo is not None and maximo is None:
        if valor < minimo:
            status = "abaixo do normal"
        else:
            status = "dentro do esperado"
    else:
        status = "não foi possível interpretar os limites"

    return f"{desc} — valor informado: {valor} ({status}). {interpretacao}"
