"""Testes demonstrativos E2E com stack Docker.

Estes cenários são focados em demonstração de funcionalidades para aula:
- webhook com imagem
- webhook com áudio
- memória semântica no Postgres Store

Pré-requisito:
    docker compose up -d --build
"""

from __future__ import annotations

import os
import threading
import time
import uuid
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import httpx
import psycopg
import pytest
from langchain_openai import OpenAIEmbeddings
from langgraph.store.postgres.aio import AsyncPostgresStore
from langgraph.store.postgres.base import PostgresIndexConfig
from pydantic import SecretStr

from whatsapp_langchain.shared.config import settings

pytestmark = pytest.mark.docker_demo

DEFAULT_DB_URL = "postgresql://postgres:postgres@localhost:5432/whatsapp_langchain"
API_BASE_URL = "http://localhost:8000"
ASSETS_DIR = Path(__file__).parents[1] / "assets"


def _get_db_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DB_URL)


def _query_message_status(db_url: str, message_sid: str) -> tuple | None:
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT status, response, error, media_type
                FROM message_queue
                WHERE message_id = %s
                ORDER BY id DESC
                LIMIT 1
                """,
                (message_sid,),
            )
            return cur.fetchone()


def _wait_terminal_status(
    db_url: str,
    message_sid: str,
    timeout_seconds: int = 90,
) -> tuple:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        row = _query_message_status(db_url, message_sid)
        if row and row[0] in {"done", "failed"}:
            return row
        time.sleep(1)
    raise AssertionError(f"Mensagem {message_sid} não finalizou em {timeout_seconds}s")


@pytest.fixture(scope="module")
def ensure_docker_stack() -> str:
    """Valida pré-requisitos: API e DB acessíveis localmente."""
    try:
        response = httpx.get(f"{API_BASE_URL}/health", timeout=3)
        if response.status_code != 200:
            pytest.skip("API não saudável. Rode: docker compose up -d --build")
    except Exception:
        pytest.skip("API não acessível. Rode: docker compose up -d --build")

    db_url = _get_db_url()
    try:
        with psycopg.connect(db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
    except Exception:
        pytest.skip("DB não acessível. Verifique docker compose e DATABASE_URL")

    return db_url


@pytest.fixture(scope="module")
def media_server_urls() -> dict[str, str]:
    """Sobe servidor HTTP local para mídia consumida pelo worker no container."""
    image_file = ASSETS_DIR / "sample.png"
    audio_file = ASSETS_DIR / "sample.ogg"
    if not image_file.exists() or not audio_file.exists():
        pytest.skip("Assets de demo ausentes em tests/assets/")

    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, format: str, *args) -> None:
            return

    handler = partial(QuietHandler, directory=str(ASSETS_DIR))
    server = ThreadingHTTPServer(("0.0.0.0", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    port = server.server_address[1]
    try:
        yield {
            "image_url": f"http://host.docker.internal:{port}/sample.png",
            "audio_url": f"http://host.docker.internal:{port}/sample.ogg",
        }
    finally:
        server.shutdown()
        thread.join(timeout=5)


def test_demo_webhook_image_e2e(
    ensure_docker_stack: str,
    media_server_urls: dict[str, str],
):
    """Demonstra pipeline completo de imagem via webhook assíncrono."""
    sid = f"SMIMG{uuid.uuid4().hex[:12]}"
    phone = f"+5511{uuid.uuid4().int % 10**8:08d}"

    response = httpx.post(
        f"{API_BASE_URL}/webhook/twilio?agent=rhawk_assistant",
        data={
            "MessageSid": sid,
            "From": f"whatsapp:{phone}",
            "To": "whatsapp:+14155238886",
            "Body": "Descreva esta imagem.",
            "NumMedia": "1",
            "MediaUrl0": media_server_urls["image_url"],
            "MediaContentType0": "image/png",
        },
        timeout=10,
    )
    assert response.status_code == 200

    status, output, error, media_type = _wait_terminal_status(ensure_docker_stack, sid)
    assert media_type == "image/png"
    assert status == "done", f"Processamento de imagem falhou: {error}"
    assert output and output.strip()


def test_demo_webhook_audio_e2e(
    ensure_docker_stack: str,
    media_server_urls: dict[str, str],
):
    """Demonstra pipeline completo de áudio via webhook assíncrono."""
    sid = f"SMAUD{uuid.uuid4().hex[:12]}"
    phone = f"+5521{uuid.uuid4().int % 10**8:08d}"

    response = httpx.post(
        f"{API_BASE_URL}/webhook/twilio?agent=rhawk_assistant",
        data={
            "MessageSid": sid,
            "From": f"whatsapp:{phone}",
            "To": "whatsapp:+14155238886",
            "Body": "Transcreva e responda.",
            "NumMedia": "1",
            "MediaUrl0": media_server_urls["audio_url"],
            "MediaContentType0": "audio/ogg",
        },
        timeout=10,
    )
    assert response.status_code == 200

    status, output, error, media_type = _wait_terminal_status(ensure_docker_stack, sid)
    assert media_type == "audio/ogg"
    assert status == "done", f"Processamento de áudio falhou: {error}"
    assert output and output.strip()


@pytest.mark.asyncio
async def test_demo_semantic_memory_roundtrip(ensure_docker_stack: str):
    """Demonstra gravação e busca semântica no Postgres Store."""
    api_key = settings.openrouter_api_key
    if not api_key:
        pytest.skip("OPENROUTER_API_KEY não configurada")

    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        base_url=settings.openrouter_base_url,
        api_key=SecretStr(api_key.get_secret_value()),
    )
    index_config: PostgresIndexConfig = {
        "embed": embeddings,
        "dims": settings.embedding_dims,
        "fields": ["$"],
    }

    namespace = (f"demo-user-{uuid.uuid4().hex[:8]}", "memories")

    async with AsyncPostgresStore.from_conn_string(
        ensure_docker_stack,
        index=index_config,
    ) as store:
        await store.setup()
        await store.aput(
            namespace,
            "m1",
            {"memory": "Meu nome é Ronnald e eu estudo sistemas de agentes."},
        )
        await store.aput(
            namespace,
            "m2",
            {"memory": "Prefiro exemplos práticos com testes automatizados."},
        )

        results = await store.asearch(
            namespace,
            query="Qual é o meu nome?",
            limit=5,
        )

    assert results
    recovered = " ".join(str(r.value.get("memory", "")).lower() for r in results)
    assert "ronnald" in recovered
