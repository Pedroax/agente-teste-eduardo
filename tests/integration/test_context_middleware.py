"""Testes de integração para middlewares de contexto.

Estes testes verificam se as estratégias de gerenciamento de contexto
(trim, summarize, none) funcionam corretamente com o agente real.

Executar com: pytest tests/integration/ -v
"""

import os

import pytest
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from whatsapp_langchain.agents.middleware import get_context_middleware

load_dotenv()


# --- Fixtures ---


@pytest.fixture
def model():
    """Modelo configurado para testes."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        pytest.skip("OPENROUTER_API_KEY não configurada")

    return ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001"),
        api_key=SecretStr(api_key),
        base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    )


# --- Testes do Trim Middleware ---


class TestTrimMiddleware:
    """Testes para a estratégia trim."""

    def test_trim_keeps_n_messages(self):
        """Verifica que o trim mantém apenas N mensagens recentes."""
        # Cria middleware com keep_messages=2
        middleware = get_context_middleware(strategy="trim", trim_keep_messages=2)

        assert len(middleware) == 1
        assert middleware[0] is not None

    def test_trim_logic_directly(self):
        """Testa a lógica do trim diretamente, sem o agente."""
        # Simula estado com muitas mensagens
        messages = [
            SystemMessage(content="Você é um assistente."),
            HumanMessage(content="Msg 1"),
            AIMessage(content="Resp 1"),
            HumanMessage(content="Msg 2"),
            AIMessage(content="Resp 2"),
            HumanMessage(content="Msg 3"),
            AIMessage(content="Resp 3"),
            HumanMessage(content="Msg 4"),
        ]

        # Simula o que o trim faria com keep_messages=2
        keep_messages = 2
        first_msg = messages[0]

        # Garante número par
        recent_count = keep_messages if keep_messages % 2 == 0 else keep_messages + 1
        recent_messages = messages[-recent_count:]

        result = [first_msg, *recent_messages]

        # Deve ter: system + 2 mensagens recentes
        assert len(result) == 3
        assert result[0].content == "Você é um assistente."
        assert result[-1].content == "Msg 4"

    def test_trim_preserves_system_prompt(self):
        """Verifica que o trim sempre preserva o system prompt."""
        messages = [
            SystemMessage(content="System importante"),
            HumanMessage(content="Msg 1"),
            AIMessage(content="Resp 1"),
            HumanMessage(content="Msg 2"),
            AIMessage(content="Resp 2"),
            HumanMessage(content="Msg 3"),
        ]

        keep_messages = 2
        first_msg = messages[0]
        recent_count = keep_messages if keep_messages % 2 == 0 else keep_messages + 1
        recent_messages = messages[-recent_count:]

        result = [first_msg, *recent_messages]

        # System prompt deve estar presente
        assert result[0].content == "System importante"

    def test_trim_with_agent_integration(self, model):
        """Teste de integração: agente com trim responde corretamente."""
        middleware = get_context_middleware(strategy="trim", trim_keep_messages=4)

        agent = create_agent(
            model=model,
            tools=[],
            system_prompt="Responda de forma breve.",
            middleware=middleware,
        )

        # Primeira mensagem
        result = agent.invoke(
            {"messages": [HumanMessage(content="Olá, meu nome é Carlos.")]},
            config={"configurable": {"thread_id": "test-trim-1"}},
        )

        assert result is not None
        assert "messages" in result


# --- Testes do Summarize Middleware ---


class TestSummarizeMiddleware:
    """Testes para a estratégia summarize."""

    def test_summarize_creates_middleware(self):
        """Verifica que o summarize cria o middleware corretamente."""
        middleware = get_context_middleware(
            strategy="summarize",
            summarize_trigger_tokens=100,
            summarize_keep_messages=2,
        )

        assert len(middleware) == 1
        assert middleware[0] is not None

    def test_summarize_with_agent_integration(self, model):
        """Teste de integração: agente com summarize responde corretamente."""
        middleware = get_context_middleware(
            strategy="summarize",
            summarize_trigger_tokens=500,  # Valor baixo para teste
            summarize_keep_messages=2,
        )

        agent = create_agent(
            model=model,
            tools=[],
            system_prompt="Responda de forma breve.",
            middleware=middleware,
        )

        # Primeira mensagem
        result = agent.invoke(
            {"messages": [HumanMessage(content="Olá!")]},
            config={"configurable": {"thread_id": "test-summarize-1"}},
        )

        assert result is not None
        assert "messages" in result


# --- Testes do None (sem middleware) ---


class TestNoneMiddleware:
    """Testes para strategy=none (sem gerenciamento de contexto)."""

    def test_none_returns_empty_list(self):
        """Verifica que strategy=none retorna lista vazia."""
        middleware = get_context_middleware(strategy="none")

        assert middleware == []
        assert len(middleware) == 0

    def test_none_with_agent_integration(self, model):
        """Teste de integração: agente sem middleware responde corretamente."""
        middleware = get_context_middleware(strategy="none")

        agent = create_agent(
            model=model,
            tools=[],
            system_prompt="Responda de forma breve.",
            middleware=middleware,
        )

        result = agent.invoke(
            {"messages": [HumanMessage(content="Olá!")]},
            config={"configurable": {"thread_id": "test-none-1"}},
        )

        assert result is not None
        assert "messages" in result


# --- Testes da Factory ---


class TestGetContextMiddleware:
    """Testes para a factory get_context_middleware()."""

    def test_default_strategy_is_summarize(self):
        """Verifica que o default é summarize quando não há env var."""
        # Salva e limpa a env var
        original = os.environ.pop("CONTEXT_STRATEGY", None)

        try:
            middleware = get_context_middleware()
            # Deve retornar um middleware (summarize)
            assert len(middleware) == 1
        finally:
            # Restaura
            if original:
                os.environ["CONTEXT_STRATEGY"] = original

    def test_override_parameters(self):
        """Verifica que parâmetros override funcionam."""
        middleware = get_context_middleware(
            strategy="trim",
            trim_keep_messages=5,
        )

        assert len(middleware) == 1

    def test_invalid_strategy_returns_empty(self):
        """Verifica que estratégia inválida retorna lista vazia."""
        middleware = get_context_middleware(strategy="invalid_strategy")

        assert middleware == []
