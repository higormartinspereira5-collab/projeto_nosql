# Projeto  -  Organização de Jogos (NoSQL)

Este repositório contém o código-fonte e os arquivos de entrega para o projeto final da disciplina de NoSQL. A aplicação consiste em uma API desenvolvida com Python e FastAPI, conectada a um banco de dados MongoDB.

---

## 🚀 Como Executar

1.  **Instalar Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configurar Conexão:**
    Altere a variável `MONGO_URI` nos arquivos `main_api.py` e `popular_banco.py` com a sua connection string do MongoDB Atlas.

3.  **Popular o Banco:**
    ```bash
    python popular_banco.py
    ```

4.  **Iniciar a API:**
    ```bash
    uvicorn main_api:app --reload
    ```
    A documentação interativa estará disponível em `http://127.0.0.1:8000/docs`.

---

## 📦 Arquivos do Projeto

* **`main_api.py`**: Contém o código da API com os endpoints para busca (Entrega 3) e agregações (Entrega 4).
* **`popular_banco.py`**: Script para popular o banco de dados com dados de exemplo (Entrega 2).
* **`requirements.txt`**: Lista de bibliotecas Python necessárias para rodar o projeto.
* **`evidencias.zip`**: Arquivo compactado com os screenshots que comprovam o funcionamento dos endpoints da API.
* **`prints_popular.zip`**: Arquivo compactado com os screenshots que comprovam a inserção de dados no banco.

---

## 🧪 Como Testar a API

Com o servidor da API rodando (após o passo `uvicorn main_api:app --reload`), a forma mais fácil de testar todos os endpoints é através da documentação interativa gerada pelo FastAPI.

Acesse no seu navegador o seguinte endereço:

### **➡️ [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

Nessa página, você poderá clicar em cada endpoint, usar o botão "Try it out" e "Execute" para ver os resultados em tempo real.

---
