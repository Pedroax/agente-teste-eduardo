"""Webhook UAZAPI para receber mensagens WhatsApp.

Endpoint POST que recebe mensagens do UAZAPI e enfileira para processamento assíncrono.
"""

from fastapi import APIRouter, Request, Response
from structlog import get_logger

from whatsapp_langchain.shared.queue import enqueue_or_buffer

logger = get_logger(__name__)

router = APIRouter()


@router.post("/webhook/uazapi")
async def webhook_uazapi(request: Request, agent: str = "fhe_assistant") -> Response:
    """Recebe webhook do UAZAPI com mensagens WhatsApp.

    Formato do webhook UAZAPI (exemplo):
    {
        "event": "message",
        "data": {
            "key": {
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": false,
                "id": "MESSAGE_ID"
            },
            "message": {
                "conversation": "Texto da mensagem"
            },
            "messageType": "conversation",
            "pushName": "Nome do Contato",
            "messageTimestamp": 1234567890
        }
    }

    Args:
        request: Request FastAPI com payload JSON
        agent: ID do agente a usar (padrão: fhe_assistant)

    Returns:
        Response vazia (200 OK) - processamento assíncrono via worker
    """
    try:
        # Parse JSON payload
        payload = await request.json()

        logger.info("uazapi_webhook_received", payload=payload, agent=agent)

        # Validar estrutura básica
        event = payload.get("event")
        data = payload.get("data", {})

        # Ignorar eventos que não são mensagens
        if event != "message":
            logger.debug("uazapi_webhook_ignored_event", event=event)
            return Response(status_code=200)

        # Extrair informações da mensagem
        key = data.get("key", {})
        message_data = data.get("message", {})

        # Número do remetente (remover @s.whatsapp.net)
        remote_jid = key.get("remoteJid", "")
        from_number = remote_jid.replace("@s.whatsapp.net", "").replace("@g.us", "")

        # Ignorar mensagens enviadas por nós mesmos
        if key.get("fromMe", False):
            logger.debug("uazapi_webhook_ignored_from_me", from_number=from_number)
            return Response(status_code=200)

        # Ignorar mensagens de grupo (opcional)
        if "@g.us" in remote_jid:
            logger.debug("uazapi_webhook_ignored_group", remote_jid=remote_jid)
            return Response(status_code=200)

        # Extrair texto e mídia da mensagem
        message_type = data.get("messageType", "")
        body = ""
        media_url = None
        media_type = None

        if message_type == "conversation":
            body = message_data.get("conversation", "")

        elif message_type == "extendedTextMessage":
            body = message_data.get("extendedTextMessage", {}).get("text", "")

        elif message_type == "imageMessage":
            # Imagem com caption opcional
            image_msg = message_data.get("imageMessage", {})
            body = image_msg.get("caption", "")  # Caption pode ser vazio
            media_url = image_msg.get("url")  # URL direta da imagem
            media_type = image_msg.get("mimetype", "image/jpeg")

        elif message_type == "audioMessage":
            # Áudio (nota de voz)
            audio_msg = message_data.get("audioMessage", {})
            body = ""  # Áudio não tem caption
            media_url = audio_msg.get("url")
            media_type = audio_msg.get("mimetype", "audio/ogg")

        elif message_type == "videoMessage":
            # Vídeo com caption opcional
            video_msg = message_data.get("videoMessage", {})
            body = video_msg.get("caption", "")
            media_url = video_msg.get("url")
            media_type = video_msg.get("mimetype", "video/mp4")

        elif message_type == "documentMessage":
            # Documento (PDF, DOC, etc)
            doc_msg = message_data.get("documentMessage", {})
            file_name = doc_msg.get("fileName", "documento")
            body = f"[Documento: {file_name}]"
            media_url = doc_msg.get("url")
            media_type = doc_msg.get("mimetype", "application/pdf")

        else:
            # Tipo não suportado (sticker, location, contact, etc)
            logger.warning(
                "uazapi_webhook_unsupported_type",
                message_type=message_type,
                from_number=from_number
            )
            return Response(status_code=200)

        # Se for só mídia sem texto/caption, usar texto padrão
        if media_url and (not body or not body.strip()):
            if "image" in message_type:
                body = "[Imagem enviada]"
            elif "audio" in message_type:
                body = "[Áudio enviado]"
            elif "video" in message_type:
                body = "[Vídeo enviado]"
            elif "document" in message_type:
                body = "[Documento enviado]"

        # Validar que temos pelo menos texto ou mídia
        if not media_url and (not body or not body.strip()):
            logger.debug("uazapi_webhook_empty_message", from_number=from_number)
            return Response(status_code=200)

        # Enfileirar mensagem para processamento assíncrono
        message_id = key.get("id", "")

        await enqueue_or_buffer(
            message_id=message_id,
            phone=from_number,
            body=body.strip() if body else "",
            agent_id=agent,
            media_url=media_url,  # URL da mídia (se houver)
            media_type=media_type  # Tipo MIME da mídia
        )

        logger.info(
            "uazapi_webhook_enqueued",
            message_id=message_id,
            from_number=from_number,
            agent=agent,
            body_preview=body[:50]
        )

        # Retornar 200 OK imediatamente
        # Worker vai processar de forma assíncrona
        return Response(status_code=200)

    except Exception as e:
        # Log erro mas retorna 200 para não reenviar
        logger.exception(
            "uazapi_webhook_error",
            error=str(e),
            agent=agent
        )
        return Response(status_code=200)
