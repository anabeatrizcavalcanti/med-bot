# Guia de Avaliação: Med-Bot com RAG vs. Sem RAG

Este guia explica como usar o script `test_evaluation.py` para comparar a performance do Med-Bot quando ele usa seu glossário (RAG) contra quando ele usa o conhecimento geral da IA.

## 1. Configuração do Ambiente

Antes de rodar o teste, siga estes passos:

**a. Crie a Estrutura de Pastas:**
Dentro da sua pasta `testing`, crie uma subpasta chamada `pdfs`:

backend/
|-- testing/
|   |-- pdfs/         <-- Crie esta pasta
|   |-- test_evaluation.py
|   |-- README_TESTING.md
|-- utils/
|-- ...

**b. Adicione os PDFs de Teste:**
Copie alguns arquivos PDF de exames para dentro da pasta `testing/pdfs/`. Quanto mais variados, melhor.

**c. Instale a Biblioteca Necessária:**
O script de teste precisa da biblioteca `requests` para se comunicar com sua API. Se você ainda não a tem, instale-a:

```bash
pip install requests
```

## 2. Rodando o Teste

**a. Inicie sua API FastAPI:**

Em um terminal, certifique-se de que o seu servidor FastAPI (o app.py) esteja rodando, como você sempre faz:


```bash
uvicorn app:app --reload
```

**b. Execute o Script de Avaliação:**

Em outro terminal, navegue até a pasta raiz do seu backend e execute o script de teste:

```bash
python testing/test_evaluation.py
```

O script irá processar cada PDF, chamando a API nos dois modos (com e sem RAG), e salvará os resultados.

## 3. Analisando os Resultados

Após a execução, uma nova pasta testing/results será criada. Dentro dela, você encontrará um arquivo comparison_NOME_DO_PDF.json para cada PDF que você testou.

Abra esses arquivos. Eles têm a seguinte estrutura:

```bash
{

"pdf_file": "seu_exame.pdf",

"metrics": {

"latency_with_rag_seconds": 5.81,

"latency_without_rag_seconds": 5.23

},

"output_with_rag": { /* Resposta completa da IA com RAG */ },

"output_without_rag": { /* Resposta completa da IA sem RAG */ }

}
```


