# Med-Bot: Explicador de Exames Médicos
### Projeto para a disciplina de PLN - 2025.1

O Med-Bot é uma aplicação web projetada para simplificar a compreensão de documentos médicos. A ferramenta permite que o usuário faça o upload de um arquivo de exame em formato PDF, e utilizando a IA da OpenAI (Chat GPT), ela extrai e explica os termos técnicos de forma clara e acessível.

## ✨ Funcionalidades

* **Upload de PDFs:** Interface moderna para enviar documentos de exames de forma segura.
* **Extração de Termos:** Identificação automática de termos médicos relevantes no texto do documento.
* **Explicações com IA (RAG):** Para cada termo identificado, o sistema busca informações em uma base de conhecimento local e usa a IA para gerar uma explicação simplificada e contextualizada.
* **Interface Amigável:** Design limpo e intuitivo para uma experiência de usuário agradável.

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python, FastAPI, OpenAI Chat GPT 4.0 mini, PyPDF2
* **Frontend:** React.js, Lucide-React (Ícones)

## 🚀 Como Rodar o Projeto

Siga os passos abaixo para configurar e executar a aplicação na sua máquina.

### Pré-requisitos

Antes de começar, garanta que você tenha os seguintes programas instalados:
* **Python 3.7+**
* **Node.js e npm**

### Passo 1: Configuração do Backend

1.  Abra um terminal e navegue até a pasta `backend` do projeto:
    ```bash
    cd caminho/para/o/projeto/backend
    ```

2.  Crie um arquivo de ambiente chamado `.env` na raiz da pasta `backend`. Abra este arquivo e adicione sua chave da API da OpenAI:
    ```env
    OPENAI_API_KEY="SUA-CHAVE-DE-API-DA-OPENAI-AQUI"

    Caso a sua chave API não seja reconhecida durante a execução do programa, utilize o comando $export OPENAI_API_KEY="SUA-CHAVE-DE-API-DA-OPENAI-AQUI"
    no mesmo terminal do backend e tente novamente.
    ```

3.  Instale as dependências de Python necessárias:
    ```bash
    pip install -r requirements.txt
    ```

4.  Inicie o servidor do backend:
    ```bash
    uvicorn app:app --reload
    ```
    O backend estará rodando em `http://127.0.0.1:8000`. Deixe este terminal aberto.

### Passo 2: Configuração do Frontend

1.  Abra um **novo terminal**. Não feche o terminal do backend.

2.  Navegue até a pasta `frontend` do projeto:
    ```bash
    cd caminho/para/o/projeto/frontend
    ```

3.  Instale as dependências do Node.js:
    ```bash
    npm install
    npm install lucide-react
    ```

4.  Inicie a aplicação do frontend:
    ```bash
    npm start
    ```

### Passo 3: Acesse a Aplicação

Pronto! A aplicação será aberta automaticamente no seu navegador. Caso não abra, acesse manualmente o seguinte endereço:

**`http://localhost:3000`**

Agora você já pode fazer o upload de um PDF e ver a ferramenta em ação.
