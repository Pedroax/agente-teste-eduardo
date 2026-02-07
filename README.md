# WhatsApp LangChain

Template educacional e production-ready para criar agentes de IA no WhatsApp usando LangGraph.

## O que é?

Um sistema completo que conecta agentes de IA ao WhatsApp. Você define o comportamento do agente usando Langchain/LangGraph, e a infraestrutura cuida do resto: receber mensagens, processar com IA, e responder automaticamente.

## Arquitetura

![Arquitetura](docs/architecture.png)

```
Usuário (WhatsApp)
       │
       ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Twilio     │────▶│     API      │────▶│ PostgreSQL  │
│  (Provider)  │     │  (FastAPI)   │     │  (Fila +    │
└─────────────┘     └──────────────┘     │ Checkpointer)│
                                          └──────┬───────┘
                                                 │
┌─────────────┐     ┌──────────────┐             │
│   Twilio     │◀───│   Worker     │◀────────────┘
│  (Resposta)  │    │  (LangGraph) │
└─────────────┘     └──────────────┘

┌──────────────┐
│  Admin Panel │───▶ API (métricas, conversas, fila)
│  (Next.js)   │
└──────────────┘
```

**Por que 4 serviços?**

- **API** recebe a mensagem e enfileira. Responde em milissegundos.
- **Worker** processa com IA. Pode demorar segundos — sem bloquear a API.
- **PostgreSQL** armazena a fila de mensagens e o histórico de conversas.
- **Frontend** monitora tudo via Admin Panel.

Isso garante que nenhuma mensagem é perdida, mesmo sob alta carga.

## Quick Start

### 1. Instale o uv (gerenciador de pacotes)

```bash
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# Mac/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ou via pip (qualquer OS)
pip install uv
```

### 2. Configure o projeto

```bash
git clone <repo-url>
cd whatsapp-langchain

# Cria ambiente virtual e instala dependências
make setup
# Ou manualmente: uv venv && uv pip install -e ".[dev]"

# Configure as variáveis de ambiente
cp .env.example .env   # Edite com sua OPENROUTER_API_KEY
```

### 3. Desenvolva o agente

```bash
make dev   # Abre o LangGraph Studio no navegador
# Ou manualmente: uv run langgraph dev
```

O LangGraph Studio permite conversar com o agente `rhawk_assistant` e ver o grafo executando em tempo real. O agente é definido em `src/whatsapp_langchain/agents/catalog/rhawk_assistant/`.

## Estrutura do Projeto

```
whatsapp-langchain/
├── src/whatsapp_langchain/
│   ├── agents/                 # Agentes de IA
│   │   ├── catalog/            # Um diretório por agente
│   │   │   └── rhawk_assistant/ # Agente padrão (agent.py, graph.py, prompts.py)
│   │   └── middleware/         # Trim, Summarize (gerenciamento de contexto)
│   ├── server/                 # API FastAPI (em breve)
│   ├── worker/                 # Processamento de mensagens (em breve)
│   └── shared/                 # Config, DB, Models (em breve)
├── tests/                      # Testes automatizados
├── langgraph.json              # Registry de agentes
├── pyproject.toml              # Dependências e configuração
├── Makefile                    # Comandos úteis
└── docs/                       # Documentação
```

## Documentação

| Documento | Descrição |
|-----------|-----------|
| [Primeiros Passos](docs/GETTING_STARTED.md) | Setup, LangGraph Studio, testes |
| [Arquitetura](docs/ARCHITECTURE.md) | Como o sistema funciona |
| [Criando Agentes](docs/ADDING_AGENTS.md) | Como criar novos agentes |

## Pré-requisitos

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (gerenciador de pacotes — funciona no Windows, Mac e Linux)
- Conta [OpenRouter](https://openrouter.ai/) (LLM)
- Conta [LangSmith](https://smith.langchain.com/) (necessário para o LangGraph Studio)

> **Windows:** Recomendamos instalar o [WSL](https://learn.microsoft.com/pt-br/windows/wsl/install) (Windows Subsystem for Linux) para melhor compatibilidade com as ferramentas de desenvolvimento. Não é obrigatório, mas simplifica bastante o setup.

## Comandos

### Comandos diretos (qualquer OS)

```bash
uv venv                      # Cria ambiente virtual
uv pip install -e ".[dev]"   # Instala dependências
uv run langgraph dev         # LangGraph Studio
uv run ruff check .          # Lint
uv run ruff format .         # Formata código
uv run pyright src/          # Type check
uv run pytest                # Testes
```

### Atalhos Makefile (Mac/Linux/WSL)

```bash
make setup          # Cria .venv e instala dependências
make dev            # LangGraph Studio (desenvolvimento de agentes)
make lint           # Encontra problemas (ruff check)
make format         # Formata código (ruff format)
make fix            # Corrige problemas automaticamente
make typecheck      # Verifica tipos estáticos (pyright)
make check          # Verifica tudo (lint + format + types)
make test           # Roda todos os testes
make clean          # Remove __pycache__
```

## Roadmap

O projeto está sendo construído em fases:

- **Fase 1 (atual)** — Pacote de agentes: `create_agent()`, middleware de contexto (trim/summarize), LangGraph Studio
- **Fase 2** — API (FastAPI) + Worker + PostgreSQL como fila
- **Fase 3** — Integração Twilio (WhatsApp), mídia (imagem/áudio), rate limiting
- **Fase 4** — Admin Panel (Next.js) + Deploy no Railway

## Licença

[TOPHAWKS Community License](LICENSE) — Uso restrito a membros da comunidade [TOPHAWKS](https://www.rhawk.pro/comunidade).
