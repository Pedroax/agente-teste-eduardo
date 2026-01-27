# Criando Agentes

## Convenção

Cada agente vive em seu próprio diretório dentro de `src/whatsapp_langchain/agents/catalog/`:

```
agents/catalog/meu_agente/
├── __init__.py
├── graph.py      # StateGraph + build_graph()
├── prompts.py    # System prompt
└── state.py      # Estado do agente (TypedDict)
```

A função `build_graph(checkpointer=None)` é o ponto de entrada. Ela retorna um grafo compilado do LangGraph.

## Passo a Passo

### 1. Criar o diretório

```bash
mkdir -p src/whatsapp_langchain/agents/catalog/meu_agente
touch src/whatsapp_langchain/agents/catalog/meu_agente/__init__.py
```

### 2. Definir o estado

```python
# state.py
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
```

### 3. Definir o prompt

```python
# prompts.py
SYSTEM_PROMPT = """Você é um assistente especializado em vendas.
Seja objetivo, amigável e ajude o cliente a encontrar o produto ideal.
Responda sempre em português."""
```

### 4. Criar o grafo

```python
# graph.py
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from .state import AgentState
from .prompts import SYSTEM_PROMPT
from ...middleware.trim import create_trim_node


def build_graph(checkpointer=None):
    llm = ChatOpenAI(
        model="openai/gpt-4o-mini",
        base_url="https://openrouter.ai/api/v1",
    )

    async def call_model(state: AgentState):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        response = await llm.ainvoke(messages)
        return {"messages": [response]}

    graph = StateGraph(AgentState)
    graph.add_node("trim", create_trim_node())
    graph.add_node("model", call_model)

    graph.add_edge(START, "trim")
    graph.add_edge("trim", "model")
    graph.add_edge("model", END)

    return graph.compile(checkpointer=checkpointer)
```

### 5. Registrar no langgraph.json

```json
{
  "graphs": {
    "assistant": "./src/whatsapp_langchain/agents/catalog/assistant/graph.py:build_graph",
    "meu_agente": "./src/whatsapp_langchain/agents/catalog/meu_agente/graph.py:build_graph"
  },
  "env": ".env"
}
```

### 6. Testar

```bash
make dev   # Abre o LangGraph Studio
```

No Studio, selecione `meu_agente` e converse para validar.

### 7. Ativar no WhatsApp

Configure o webhook do Twilio com o parâmetro `agent`:

```
https://sua-api.up.railway.app/webhook/twilio?agent=meu_agente
```

## Middleware de Memória

Os agentes podem usar dois middlewares para gerenciar o tamanho do contexto:

### Trim (recomendado para começar)

Mantém apenas as últimas N mensagens. Simples e sem custo extra.

```python
from ...middleware.trim import create_trim_node

# No grafo:
graph.add_node("trim", create_trim_node(max_tokens=4000))
graph.add_edge(START, "trim")
graph.add_edge("trim", "model")
```

**Quando usar**: Conversas curtas, respostas baseadas em contexto recente.

### Summarize

Sumariza mensagens antigas usando uma chamada extra ao LLM. Preserva mais contexto.

```python
from ...middleware.summarize import create_summarize_node

# No grafo:
graph.add_node("summarize", create_summarize_node(
    llm=llm,
    max_messages_before_summary=20,
    messages_to_keep=5,
))
graph.add_edge(START, "summarize")
graph.add_edge("summarize", "model")
```

**Quando usar**: Conversas longas onde o histórico é importante (ex: suporte ao cliente).

### Trade-offs

| | Trim | Summarize |
|--|------|-----------|
| **Custo** | Zero | 1 chamada LLM extra |
| **Contexto perdido** | Mensagens antigas descartadas | Resumo preserva contexto |
| **Latência** | Zero | +1-2s por sumarização |
| **Melhor para** | Conversas curtas, FAQ | Suporte, vendas complexas |

## Agente com Tools

```python
# graph.py
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode


@tool
def consultar_estoque(produto: str) -> str:
    """Consulta o estoque de um produto."""
    # Sua lógica aqui
    return f"{produto}: 42 unidades disponíveis"


def build_graph(checkpointer=None):
    tools = [consultar_estoque]
    llm = ChatOpenAI(model="openai/gpt-4o-mini").bind_tools(tools)

    async def call_model(state):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        return {"messages": [await llm.ainvoke(messages)]}

    def should_continue(state):
        last = state["messages"][-1]
        return "tools" if last.tool_calls else END

    graph = StateGraph(AgentState)
    graph.add_node("model", call_model)
    graph.add_node("tools", ToolNode(tools))

    graph.add_edge(START, "model")
    graph.add_conditional_edges("model", should_continue)
    graph.add_edge("tools", "model")

    return graph.compile(checkpointer=checkpointer)
```

## Boas Práticas

- **Um agente por caso de uso** — `assistant`, `vendas`, `suporte`, etc
- **Prompts em `prompts.py`** — Separados do código do grafo
- **Estado em `state.py`** — Facilita adicionar campos customizados
- **Sem dependências externas** — O agente não deve importar de `server/` ou `worker/`
- **Teste no Studio primeiro** — `make dev` antes de conectar ao WhatsApp
