# P0 — Ficha de artigo com LLM

## Sobre o projeto

Aplicação em Python que utiliza um Large Language Model (LLM) por meio de sua interface programática (API) para resolver um problema textual pequeno e real.

**Problema:** ao revisar a literatura de detecção de anomalias em séries temporais, é trabalhoso extrair manualmente as informações principais de cada artigo.

**Solução:** o programa recebe o abstract de um artigo e devolve uma ficha estruturada com:

- Método
- Dataset(s)
- Métrica(s)
- Principal resultado

Quando uma informação não está no abstract, a ficha indica "não informado", sem inventar dados.

**Quem usa:** pesquisadores e estudantes que fazem revisão de literatura na área.

**Por que um LLM:** o abstract é texto livre, escrito de formas diferentes em cada artigo. Extrair informações de texto livre é uma tarefa em que um modelo de linguagem funciona melhor do que regras fixas.

## Objetivos

- Identificar e delimitar um problema textual real.
- Desenvolver uma aplicação utilizando Python.
- Integrar um modelo de linguagem por meio de sua interface programática.
- Implementar tratamento de erros e boas práticas de organização.
- Garantir que outra pessoa consiga compreender e executar o projeto.

## Desenvolvimento

O projeto é desenvolvido incrementalmente em três níveis:

- **Básico:** núcleo funcional da aplicação (concluído).
- **Intermediário:** melhoria da organização do código e do tratamento de erros (em andamento).
- **Avançado:** conclusão da aplicação, testes e preparação para execução reproduzível.

## Tecnologias

- Python
- Gemini (Google), acessado pela biblioteca `google-genai`
- `python-dotenv` para carregar a chave de API a partir de um arquivo `.env`

Modelo utilizado: `<ID do modelo>`

## Estrutura do projeto

```
projeto-p0/
├── app.py            # programa principal
├── requirements.txt  # dependências
├── .env.example      # modelo do arquivo de configuração
├── .gitignore
└── README.md
```

## Instalação

1. Clone o repositório:
   ```
   git clone https://github.com/kclanoce/projeto-p0.git
   cd projeto-p0
   ```

2. Crie e ative um ambiente virtual:
   ```
   python -m venv .venv
   .venv\Scripts\activate          # Windows
   source .venv/bin/activate       # Linux/Mac
   ```

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

4. Gere uma chave de API do Gemini em [aistudio.google.com](https://aistudio.google.com).

5. Copie o arquivo `.env.example` para `.env` e coloque sua chave:
   ```
   GEMINI_API_KEY=sua_chave_aqui
   ```
   O arquivo `.env` está no `.gitignore` e **nunca deve ser enviado ao GitHub**.

## Execução

```
python app.py
```

Cole o abstract do artigo no terminal. Para finalizar a entrada, vá para uma linha nova e aperte `Ctrl+Z` e `Enter` (Windows) ou `Ctrl+D` (Linux/Mac). A ficha será exibida na tela.

## Segurança

A chave de API fica apenas no arquivo `.env`, local e ignorado pelo Git. O repositório contém somente o `.env.example`, sem credenciais reais.

## Testes

A ser documentado no nível Avançado (casos de sucesso e de falha).

## Uso de ferramentas de IA

A ser documentado ao final do projeto.
