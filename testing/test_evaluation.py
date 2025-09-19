import os
import requests
import json
import time
from pathlib import Path

# --- Configurações ---
API_URL = "http://127.0.0.1:8000/analyze-pdf/"
PDF_TEST_DIR = Path(__file__).parent / "pdfs"
RESULTS_DIR = Path(__file__).parent / "results"
# Crie uma pasta 'pdfs' dentro de 'testing' e coloque seus PDFs de teste lá.

# Garante que o diretório de resultados exista
RESULTS_DIR.mkdir(exist_ok=True)

def run_analysis(pdf_path, rag_mode):
    """Função para chamar a API e retornar a resposta e a latência."""
    print(f"  Analisando '{pdf_path.name}' (RAG: {rag_mode})...")
    
    files = {'file': (pdf_path.name, open(pdf_path, 'rb'), 'application/pdf')}
    data = {
        'idade': 35,  # Idade padrão para o teste
        'sexo': 'feminino', # Sexo padrão para o teste
        'rag': rag_mode
    }

    start_time = time.time()
    try:
        response = requests.post(API_URL, files=files, data=data, timeout=90)
        end_time = time.time()
        
        latency = end_time - start_time
        response.raise_for_status()
        
        return response.json(), latency

    except requests.exceptions.RequestException as e:
        print(f"    ERRO na requisição: {e}")
        return {"error": str(e)}, time.time() - start_time


def main():
    """Roda a avaliação para todos os PDFs na pasta de teste."""
    pdf_files = list(PDF_TEST_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"Nenhum PDF encontrado em '{PDF_TEST_DIR}'.")
        print("Por favor, crie a pasta 'testing/pdfs' e adicione seus arquivos de teste.")
        return

    print(f"Iniciando avaliação para {len(pdf_files)} arquivo(s) PDF...")

    for pdf_path in pdf_files:
        print(f"\n--- Processando: {pdf_path.name} ---")
        
        # Executa com RAG
        rag_result, rag_latency = run_analysis(pdf_path, rag_mode=True)
        
        # Executa sem RAG
        no_rag_result, no_rag_latency = run_analysis(pdf_path, rag_mode=False)

        comparison_data = {
            "pdf_file": pdf_path.name,
            "metrics": {
                "latency_with_rag_seconds": round(rag_latency, 2),
                "latency_without_rag_seconds": round(no_rag_latency, 2),
            },
            "output_with_rag": rag_result,
            "output_without_rag": no_rag_result,
        }
        
        result_filename = RESULTS_DIR / f"comparison_{pdf_path.stem}.json"
        with open(result_filename, "w", encoding="utf-8") as f:
            json.dump(comparison_data, f, indent=2, ensure_ascii=False)
            
        print(f"  Resultados salvos em '{result_filename}'")
        print(f"  Latência (Com RAG): {rag_latency:.2f}s | Latência (Sem RAG): {no_rag_latency:.2f}s")

    print("\n--- Avaliação Concluída ---")
    print(f"Todos os resultados foram salvos na pasta '{RESULTS_DIR}'.")
    print("Agora você pode comparar os arquivos JSON gerados para uma análise qualitativa.")


if __name__ == "__main__":
    main()
