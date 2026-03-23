"""Agente FHE Assistant - Consultor Digital da Formação em Hipnose Ericksoniana.

Agente autônomo especializado em qualificar leads e educar profissionais
interessados na FHE do ACT Institute.

Usa create_agent do LangChain 1.0 com:
- Ferramentas especializadas (ROI calculator, case studies, objection handler)
- Middleware de contexto configurável
- Memória semântica cross-thread via LangGraph Store
"""

from langchain.agents import create_agent
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.store.base import BaseStore

from whatsapp_langchain.agents.middleware import get_context_middleware
from whatsapp_langchain.agents.tools import read_memory, save_memory
from whatsapp_langchain.shared.llm import create_chat_model

from .prompts import SYSTEM_PROMPT
from .tools import objection_handler, roi_calculator, send_case_study


def build_graph(
    checkpointer: BaseCheckpointSaver | None = None,
    store: BaseStore | None = None,
):
    """Constrói o agente FHE Assistant.

    O agente é um consultor digital autônomo que:
    - Qualifica leads interessados na FHE
    - Calcula ROI personalizado por profissão e especialidade
    - Envia casos de sucesso similares ao perfil do lead
    - Trata objeções com argumentação estruturada
    - Usa memória semântica para personalização contínua

    Ferramentas disponíveis:
    - roi_calculator: Calcula retorno sobre investimento personalizado
    - send_case_study: Envia proof social relevante ao perfil
    - objection_handler: Argumentos estruturados para objeções comuns
    - save_memory: Salva insights importantes sobre o lead
    - read_memory: Recupera informações de conversas anteriores

    Args:
        checkpointer: Checkpointer para persistência de estado da conversa.
                      None em dev (in-memory), PostgresSaver em prod.
        store: Store para memória semântica cross-thread.
               None desabilita memória, InMemoryStore em dev,
               AsyncPostgresStore em prod.

    Returns:
        CompiledStateGraph: Agente compilado pronto para uso.

    Exemplo:
        # Em produção com persistência
        from langgraph.checkpoint.postgres import AsyncPostgresSaver
        from langgraph.store.postgres import AsyncPostgresStore

        checkpointer = AsyncPostgresSaver(pool)
        store = AsyncPostgresStore(pool)
        graph = build_graph(checkpointer, store)

        # Executar
        response = await graph.ainvoke(
            {"messages": [HumanMessage("Quanto custa a formação?")]},
            config={
                "configurable": {
                    "thread_id": "whatsapp:+5511999999999",
                    "user_id": "+5511999999999"
                }
            }
        )
    """
    # Modelo principal com rate limiter centralizado
    # Usa configuração de .env (OPENROUTER_MODEL)
    model = create_chat_model()

    # Middleware de contexto baseado em CONTEXT_STRATEGY
    # Gerencia histórico de mensagens (trim/summarize)
    middleware = get_context_middleware()

    # Ferramentas especializadas do FHE
    tools = [
        roi_calculator,      # Calcula ROI personalizado
        send_case_study,     # Envia proof social
        objection_handler,   # Trata objeções
    ]

    # Adiciona ferramentas de memória se store disponível
    if store:
        tools.extend([save_memory, read_memory])

    # Cria agente com create_agent (LangChain 1.0)
    # Agente ReAct: Raciocina, usa ferramentas, responde
    return create_agent(
        model=model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        middleware=middleware,
        checkpointer=checkpointer,
        store=store,
    )
