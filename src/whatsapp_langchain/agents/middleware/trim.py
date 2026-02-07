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
from langchain_core.messages import RemoveMessage
from langgraph.runtime import Runtime


def create_trim_middleware(keep_messages: int = 10):
    """Cria middleware que mantém apenas as N mensagens mais recentes.

    Descarta mensagens antigas e mantém as ``keep_messages`` mais recentes.
    O system prompt não precisa de tratamento — o ``create_agent()`` o injeta
    automaticamente via ``ModelRequest.system_message`` a cada chamada.

    Args:
        keep_messages: Número de mensagens recentes a manter. Default: 10.

    Returns:
        Função middleware decorada com @before_model.

    Exemplo:
        Conversa com 15 mensagens, keep_messages=4:

        Antes:  [h1] [a1] [h2] [a2] ... [h7] [a7] [h8]
        Depois: [a6] [h7] [a7] [h8]

    Nota:
        O número é ajustado para par, garantindo pares completos user/assistant.

    Importante:
        O reducer ``add_messages`` faz merge, não replace — retornar uma lista
        menor NÃO remove mensagens. Usamos RemoveMessage para cada mensagem
        que deve sair do estado.
    """

    @before_model
    def trim_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        messages = state["messages"]

        if len(messages) <= keep_messages:
            return None

        # Garante número par (pares completos user/assistant)
        recent_count = keep_messages if keep_messages % 2 == 0 else keep_messages - 1

        # Remove tudo antes das mensagens recentes
        messages_to_remove = messages[:-recent_count]

        return {
            "messages": [
                RemoveMessage(id=m.id) for m in messages_to_remove if m.id is not None
            ]
        }

    return trim_messages
