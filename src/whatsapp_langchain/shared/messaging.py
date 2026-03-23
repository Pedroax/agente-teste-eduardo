"""Abstração unificada para envio de mensagens (Twilio ou UAZAPI).

Detecta automaticamente qual provedor usar baseado nas configurações.
"""

from structlog import get_logger

from whatsapp_langchain.shared.config import get_settings

logger = get_logger(__name__)


class MessagingClient:
    """Cliente unificado que usa Twilio ou UAZAPI automaticamente."""

    def __init__(self):
        """Inicializa cliente baseado em configurações disponíveis."""
        settings = get_settings()

        # Detectar qual provedor usar
        self.use_uazapi = False
        self.use_twilio = False

        # Preferência: UAZAPI se configurado
        if hasattr(settings, "UAZAPI_INSTANCE_TOKEN") and settings.UAZAPI_INSTANCE_TOKEN:
            self.use_uazapi = True
            logger.info("messaging_client_using_uazapi")

            from whatsapp_langchain.shared.uazapi import get_uazapi_client
            self.client = get_uazapi_client()

        # Fallback: Twilio
        elif hasattr(settings, "TWILIO_ACCOUNT_SID") and settings.TWILIO_ACCOUNT_SID:
            self.use_twilio = True
            logger.info("messaging_client_using_twilio")

            from whatsapp_langchain.worker.twilio_client import TwilioClient
            self.client = TwilioClient()

        else:
            logger.warning("messaging_client_no_provider_configured")
            self.client = None

    async def send_message(self, to: str, body: str) -> dict:
        """Envia mensagem de texto.

        Args:
            to: Número do destinatário
            body: Texto da mensagem

        Returns:
            Resposta do provedor

        Raises:
            RuntimeError: Se nenhum provedor configurado
        """
        if not self.client:
            raise RuntimeError("Nenhum provedor de mensagens configurado (UAZAPI ou Twilio)")

        return await self.client.send_message(to, body)

    async def send_typing(self, to: str, duration: int = 3) -> dict:
        """Envia indicador de digitação.

        Args:
            to: Número do destinatário
            duration: Duração em segundos

        Returns:
            Resposta do provedor (ou dict vazio se não suportado)
        """
        if not self.client:
            return {}

        if hasattr(self.client, "send_typing"):
            return await self.client.send_typing(to, duration)

        return {}

    async def download_media(self, media_url: str) -> bytes:
        """Baixa mídia de URL.

        Args:
            media_url: URL da mídia

        Returns:
            Bytes da mídia

        Raises:
            RuntimeError: Se nenhum provedor configurado
        """
        if not self.client:
            raise RuntimeError("Nenhum provedor de mensagens configurado")

        if hasattr(self.client, "download_media"):
            return await self.client.download_media(media_url)

        # Fallback: download direto
        import httpx
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(media_url, timeout=30.0)
            response.raise_for_status()
            return response.content


# Singleton global
_messaging_client: MessagingClient | None = None


def get_messaging_client() -> MessagingClient:
    """Retorna instância singleton do cliente de mensagens.

    Returns:
        MessagingClient: Cliente configurado (UAZAPI ou Twilio)
    """
    global _messaging_client
    if _messaging_client is None:
        _messaging_client = MessagingClient()
    return _messaging_client
