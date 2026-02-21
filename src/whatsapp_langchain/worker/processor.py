"""Processador de mensagens — orquestra agente e fila.

Responsável por:
1. Construir a HumanMessage (com mídia se houver)
2. Carregar o agente via loader (com checkpointer PostgreSQL)
3. Executar o agente
4. Salvar a resposta no banco (mark_done ou mark_failed)

Uso:
    from whatsapp_langchain.worker.processor import process_message

    await process_message(message, pool, checkpointer=checkpointer, store=store)
"""

import structlog
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.store.base import BaseStore
from psycopg_pool import AsyncConnectionPool

from whatsapp_langchain.agents.loader import load_graph
from whatsapp_langchain.shared.models import MessageQueue
from whatsapp_langchain.shared.queue import (
    mark_done,
    mark_failed,
    upsert_conversation,
)
from whatsapp_langchain.worker.media import (
    AUTO_RESPONSE_MEDIA_FAILURE,
    preprocess_incoming_message,
)

logger = structlog.get_logger()


async def process_message(
    message: MessageQueue,
    pool: AsyncConnectionPool,
    *,
    checkpointer: BaseCheckpointSaver,
    store: BaseStore | None = None,
) -> None:
    """Processa uma mensagem da fila com o agente apropriado.

    Faz download de mídia se presente, carrega o grafo do agente com
    checkpointer PostgreSQL, executa e salva a resposta.

    Args:
        message: Mensagem a processar (já reservada via claim).
        pool: Pool de conexões do psycopg.
        checkpointer: Checkpointer LangGraph já inicializado no boot.
        store: Store LangGraph compartilhado (None se memória desabilitada).
    """
    logger.info(
        "processing_message",
        message_id=message.id,
        phone=message.phone_number,
        agent_id=message.agent_id,
        attempt=message.attempts,
    )

    try:
        # 1. Pré-processar entrada (mídia -> texto) antes do agente
        pre = await preprocess_incoming_message(
            body=message.incoming_message,
            media_url=message.media_url,
            media_type=message.media_type,
        )

        # Se mídia está desabilitada ou falhou, não chama o agente
        if not pre.should_invoke_agent:
            auto_response = pre.auto_response or AUTO_RESPONSE_MEDIA_FAILURE
            await mark_done(
                pool,
                message.id,
                auto_response,
                normalized_input=None,
                media_processing_status=pre.media_processing_status,
                media_processing_error=pre.media_processing_error,
            )
            await upsert_conversation(
                pool,
                phone_number=message.phone_number,
                agent_id=message.agent_id,
                last_message=auto_response,
            )
            logger.info(
                "message_auto_responded",
                message_id=message.id,
                phone=message.phone_number,
                agent_id=message.agent_id,
                media_status=pre.media_processing_status,
            )
            return

        normalized_text = pre.normalized_text or message.incoming_message
        human_message = HumanMessage(content=normalized_text)

        # 2. Carregar agente com checkpointer + store (se memória habilitada)
        invoke_config = {
            "configurable": {
                "thread_id": message.thread_id,
                "user_id": message.phone_number,
            }
        }

        graph = load_graph(
            message.agent_id,
            checkpointer=checkpointer,
            store=store,
        )
        result = await graph.ainvoke(
            {"messages": [human_message]},
            config=invoke_config,
        )

        # 4. Extrair resposta
        response_text = result["messages"][-1].content

        # 5. Salvar resultado
        await mark_done(
            pool,
            message.id,
            response_text,
            normalized_input=pre.normalized_text,
            media_processing_status=pre.media_processing_status,
            media_processing_error=pre.media_processing_error,
        )
        await upsert_conversation(
            pool,
            phone_number=message.phone_number,
            agent_id=message.agent_id,
            last_message=response_text,
        )

        logger.info(
            "message_processed",
            message_id=message.id,
            phone=message.phone_number,
            agent_id=message.agent_id,
            response_length=len(response_text),
        )

    except Exception as e:
        logger.error(
            "message_processing_error",
            message_id=message.id,
            phone=message.phone_number,
            agent_id=message.agent_id,
            error=str(e),
        )
        await mark_failed(pool, message.id, str(e))
