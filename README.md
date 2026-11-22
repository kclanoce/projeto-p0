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
- **Intermediário:** organização do código em módulos, tratamento de erros, testes simulados e documentação de configuração (concluído).
- **Avançado:** conclusão da aplicação e preparação para execução reproduzível (a fazer).

## Tecnologias

- Python
- Gemini (Google), acessado pela biblioteca `google-genai`
- `python-dotenv` para carregar a configuração a partir de um arquivo `.env`
- `httpx` (instalado junto com `google-genai`), usado para identificar falhas de rede e timeout

Modelo utilizado: `gemini-3.5-flash-lite`

## Estrutura do projeto

```
projeto-p0/
├── app.py            # ponto de entrada: captura a entrada, orquestra as etapas e exibe o resultado
├── config.py         # carregamento e validação da configuração (.env)
├── ficha.py          # validação da entrada, montagem do prompt e checagem da resposta
├── llm.py            # chamada ao Gemini e tradução dos erros da API
├── erros.py          # erros previstos, com mensagens para o usuário
├── tests/
│   └── test_tratamento_erros.py   # testes com integração simulada
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

5. Copie o arquivo `.env.example` para `.env`:
   ```
   copy .env.example .env          # Windows
   cp .env.example .env            # Linux/Mac
   ```
   Abra o `.env` e preencha os valores (veja a seção Configuração). O arquivo `.env` está no `.gitignore` e **nunca deve ser enviado ao GitHub**.

## Configuração

O acesso ao serviço é configurado por variáveis no arquivo `.env`:

| Variável | Obrigatória | Descrição |
|---|---|---|
| `GEMINI_API_KEY` | sim | Chave de API gerada em aistudio.google.com |
| `GEMINI_MODEL` | sim | ID do modelo de texto do Gemini a ser usado |
| `GEMINI_TIMEOUT` | não | Tempo máximo de espera, em segundos (padrão: 30) |

Exemplo com valores fictícios:

```
GEMINI_API_KEY=cole_sua_chave_aqui
GEMINI_MODEL=id-do-modelo
GEMINI_TIMEOUT=30
```

Os nomes de modelos do Gemini mudam com o tempo. Se o programa informar que o modelo não foi encontrado, consulte a lista de modelos disponíveis no AI Studio e atualize `GEMINI_MODEL`.

## Execução

```
python app.py
```

Cole o abstract do artigo no terminal. Para finalizar a entrada, vá para uma linha nova e aperte `Ctrl+Z` e `Enter` (Windows) ou `Ctrl+D` (Linux/Mac). A ficha será exibida na tela.

## Exemplo de entrada e saída

**Entrada:**

```
Despite decades of research on time-series anomaly detection, the
eectiveness of existing anomaly detectors remains constrained
to specic domains - a model that performs well on one dataset
may fail on another. Consequently, developing automated solutions for anomaly detection remains a pressing challenge. However,
the AutoML community has predominantly focused on supervised
learning solutions, which are impractical for anomaly detection
due to the lack of labeled data and the absence of a well-dened
objective function for model evaluation. While recent studies have
evaluated standalone anomaly detectors, no study has ever evaluated automated solutions for selecting or generating scores in
an automated manner. In this study, we (i) provide a systematic
review and taxonomy of automated solutions for time-series anomaly detection, categorizing them into selection, ensembling, and
generation methods; (ii) introduce TSB-AutoAD, a comprehensive
benchmark encompassing 20 standalone methods and 70 variants;
and (iii) conduct the most extensive evaluation in this area to date.
Our benchmark includes state-of-the-art methods across all three
categories, evaluated on TSB-AD, a recently curated heterogeneous
testbed from nine domains. Our ndings reveal a signicant gap,
where over half of the existing solutions do not statistically outperform a simple random choice. Foundation models that claim to
oer generalized, one-size-ts-all solutions have yet to deliver on
this promise. While naive ensembling achieves high accuracy, it
comes at a substantial computational overhead. Conversely, methods leveraging historical datasets enable fast inference but suer
under out-of-distribution conditions. To address this trade-o, we
propose a selective ensembling solution, which combines model
selection with ensembling to oer a lightweight, practical balance
between accuracy and eciency. We open-source TSB-AutoAD
and highlight the need for more robust and ecient solutions.
```

**Saída:**

```
--- FICHA ---

- Método: TSB-AutoAD (que inclui revisão sistemática, taxonomia categorizada em seleção, ensemble e geração; além de uma solução de selective ensembling combinando seleção de modelos com ensemble)
- Dataset(s): TSB-AD (consistindo em nove domínios)
- Métrica(s): não informado
- Principal resultado: Mais da metade das soluções existentes não superam estatisticamente uma escolha aleatória simples, modelos de fundação ainda não cumprem a promessa de soluções generalizadas, ensembling ingênuo tem alto custo computacional, e a solução proposta de selective ensembling oferece um balanço prático entre acurácia e eficiência.
```

**Exemplo de erro (entrada vazia):**

```
Erro: Nenhum texto foi informado. Cole o abstract do artigo e tente de novo.
```

## Tratamento de erros

Em vez de exibir um erro técnico extenso, o programa encerra com uma mensagem explicativa nos casos:

- entrada vazia ou grande demais (limite de 8000 caracteres);
- chave de API ausente ou recusada pelo serviço;
- modelo ou timeout mal configurados;
- modelo não encontrado;
- limite de uso do serviço atingido;
- serviço indisponível ou sobrecarregado;
- timeout e falha de comunicação;
- resposta vazia ou fora do formato esperado (faltam campos da ficha).

Erros não previstos também são capturados e mostram apenas o tipo do erro, sem detalhes internos.

## Segurança

- A chave de API fica apenas no arquivo `.env`, local e ignorado pelo Git. O repositório contém somente o `.env.example`, sem credenciais reais.
- A chave nunca é exibida: o objeto de configuração oculta o valor ao ser impresso, e as mensagens de erro não a incluem.

## Testes

**Testes simulados (automáticos):** usam um cliente simulado no lugar do Gemini, portanto não precisam de internet nem de chave e não consomem cota.

```
python -m unittest discover -s tests -v
```

Cobrem entrada vazia ou longa, configuração ausente ou inválida, credencial ausente e inválida, modelo não encontrado, limite de uso, serviço indisponível, timeout, falha de comunicação e resposta vazia ou em formato inesperado.

**Testes reais (manuais):** executados com `python app.py`, com chamada real ao Gemini.

| Cenário | Como reproduzir | Resultado |
|---|---|---|
| Abstract válido | Colar um abstract | (descreva o que aconteceu) |
| Entrada vazia | Finalizar a entrada sem colar nada | (descreva) |
| Credencial ausente | Deixar `GEMINI_API_KEY=` vazia no `.env` | (descreva) |
| Credencial inválida | Usar uma chave falsa no `.env` | (descreva) |

## Uso de ferramentas de IA
O assistente Claude (Anthropic) foi usado como apoio ao longo do projeto: para orientar a configuração do ambiente e do Git/GitHub, e gerar versões iniciais do código, dos testes e da documentação. O código foi executado, testado e revisado por mim, e as decisões sobre o problema e a organização foram minhas.
