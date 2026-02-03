"""Middleware de Trim para gerenciamento de contexto.

O trim é a estratégia mais simples e barata para gerenciar contexto:
remove mensagens antigas e mantém apenas as N mais recentes.

Trade-offs:
    - Custo: Zero (não faz chamada LLM extra)
    - Contexto: Perdido (mensagens antigas são descartadas)
    - Latência: Nenhuma

Quando usar:
    - Chatbots simples onde histórico antigo não importa
    - Testes e desenvolvimento
    - Quando custo é prioridade sobre contexto

Exemplo:
    from whatsapp_langchain.agents.middleware import create_trim_middleware

    trim = create_trim_middleware(keep_messages=10)
    agent = create_agent(model=model, middleware=[trim], ...)
"""

from typing import Any

from langchain.agents import AgentState
from langchain.agents.middleware import before_model
from langgraph.runtime import Runtime


def create_trim_middleware(keep_messages: int = 10):
    """Cria middleware que mantém apenas as N mensagens mais recentes.

    O middleware preserva sempre a primeira mensagem (system prompt) e
    as N mensagens mais recentes. Mensagens intermediárias são descartadas.

    Args:
        keep_messages: Número de mensagens recentes a manter (além do system).
                       Default: 10.

    Returns:
        Função middleware decorada com @before_model.

    Exemplo:
        Conversa com 15 mensagens + system, keep_messages=4:

        Antes:  [system] [u1] [a1] [u2] [a2] ... [u7] [a7] [u8]
        Depois: [system] [a6] [u7] [a7] [u8]

    Nota:
        O número de mensagens mantidas é ajustado para ser par (excluindo system),
        garantindo que sempre tenhamos pares completos de user/assistant.
    """

    @before_model
    def trim_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        messages = state["messages"]

        # Se temos poucas mensagens, não precisa fazer trim
        # +1 porque a primeira é o system prompt
        if len(messages) <= keep_messages + 1:
            return None

        # Preserva a primeira mensagem (system prompt)
        first_msg = messages[0]

        # Garante número par de mensagens (pares user/assistant completos)
        recent_count = keep_messages if keep_messages % 2 == 0 else keep_messages + 1
        recent_messages = messages[-recent_count:]

        # Retorna o novo estado com mensagens trimadas
        return {"messages": [first_msg, *recent_messages]}

    return trim_messages
