"""Cliente UAZAPI para integração WhatsApp.

Substitui Twilio como provedor de mensagens WhatsApp.
"""

import httpx
from structlog import get_logger

from whatsapp_langchain.shared.config import get_settings

logger = get_logger(__name__)


class UazapiClient:
    """Cliente assíncrono para UAZAPI."""

    def __init__(self):
        """Inicializa cliente UAZAPI com configurações."""
        settings = get_settings()
        self.base_url = getattr(settings, "UAZAPI_BASE_URL", "https://api-ax.uazapi.com")
        self.instance_token = getattr(settings, "UAZAPI_INSTANCE_TOKEN", "")
        self.phone_number = getattr(settings, "UAZAPI_PHONE_NUMBER", "")

        if not self.instance_token:
            logger.warning("UAZAPI_INSTANCE_TOKEN não configurado")

    async def send_message(self, to: str, body: str) -> dict:
        """Envia mensagem de texto via UAZAPI.

        Args:
            to: Número do destinatário (formato: 5511999999999)
            body: Texto da mensagem

        Returns:
            Resposta da API UAZAPI

        Raises:
            httpx.HTTPError: Se falhar ao enviar
        """
        # Limpar formato do número (remover whatsapp: se vier do Twilio format)
        clean_to = to.replace("whatsapp:", "").replace("+", "").strip()

        url = f"{self.base_url}/message/text"

        payload = {
            "phone": clean_to,
            "message": body,
            "isGroup": False
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.instance_token}"
        }

        async with httpx.AsyncClient() as client:
            logger.info(
                "uazapi_sending_message",
                to=clean_to,
                message_preview=body[:50]
            )

            response = await client.post(
                url,
                json=payload,
                headers=headers,
                timeout=30.0
            )

            response.raise_for_status()
            result = response.json()

            logger.info(
                "uazapi_message_sent",
                to=clean_to,
                response=result
            )

            return result

    async def send_typing(self, to: str, duration: int = 3) -> dict:
        """Envia indicador de digitação (typing...).

        Args:
            to: Número do destinatário
            duration: Duração em segundos (padrão: 3)

        Returns:
            Resposta da API ou dict vazio se não suportado

        Note:
            UAZAPI pode não ter endpoint específico para typing.
            Implementar se disponível na API.
        """
        # UAZAPI não tem endpoint dedicado de typing na documentação
        # Retornar vazio sem erro para não quebrar fluxo
        logger.debug("uazapi_typing_not_supported", to=to)
        return {}

    async def download_media(self, media_url: str) -> bytes:
        """Baixa mídia de URL.

        Args:
            media_url: URL da mídia fornecida pelo webhook UAZAPI

        Returns:
            Bytes da mídia

        Raises:
            httpx.HTTPError: Se falhar ao baixar

        Note:
            URLs do UAZAPI geralmente são públicas e não precisam de autenticação.
            Se precisar de auth, adicionar header Authorization aqui.
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            logger.info("uazapi_downloading_media", url=media_url[:100])

            # UAZAPI fornece URLs diretas, não precisa de auth normalmente
            # Mas incluímos o token por segurança
            headers = {}
            if self.instance_token:
                headers["Authorization"] = f"Bearer {self.instance_token}"

            response = await client.get(
                media_url,
                headers=headers,
                follow_redirects=True
            )
            response.raise_for_status()

            logger.info(
                "uazapi_media_downloaded",
                size_bytes=len(response.content),
                content_type=response.headers.get("content-type")
            )

            return response.content


# Singleton global
_uazapi_client: UazapiClient | None = None


def get_uazapi_client() -> UazapiClient:
    """Retorna instância singleton do cliente UAZAPI.

    Returns:
        UazapiClient: Cliente configurado
    """
    global _uazapi_client
    if _uazapi_client is None:
        _uazapi_client = UazapiClient()
    return _uazapi_client
