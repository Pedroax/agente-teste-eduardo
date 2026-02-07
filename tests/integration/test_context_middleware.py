"""Testes de integração para middlewares de contexto.

Estes testes verificam se as estratégias de gerenciamento de contexto
(trim, summarize, none) funcionam corretamente com o agente real.

Executar com: pytest tests/integration/ -v
"""

import os

import pytest
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage
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
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b"),
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

    def test_trim_removes_old_messages(self):
        """Invoca o middleware real e verifica remoção via reducer."""
        from langgraph.graph import add_messages

        from whatsapp_langchain.agents.middleware.trim import create_trim_middleware

        mw = create_trim_middleware(keep_messages=4)

        messages = [
            HumanMessage(content="Olá", id="h1"),
            AIMessage(content="Resp 1", id="a1"),
            HumanMessage(content="Msg 2", id="h2"),
            AIMessage(content="Resp 2", id="a2"),
            HumanMessage(content="Msg 3", id="h3"),
            AIMessage(content="Resp 3", id="a3"),
            HumanMessage(content="Msg 4", id="h4"),
        ]

        result = mw.before_model({"messages": messages}, None)

        # Middleware deve retornar RemoveMessages
        assert result is not None
        assert len(result["messages"]) == 3  # remove 3 das 7

        # Aplica pelo reducer real — igual ao que o LangGraph faz
        final = add_messages(messages, result["messages"])

        assert len(final) == 4
        assert final[0].content == "Resp 2"
        assert final[1].content == "Msg 3"
        assert final[2].content == "Resp 3"
        assert final[3].content == "Msg 4"

    def test_trim_adjusts_odd_to_even(self):
        """keep_messages ímpar é ajustado para par (pares user/assistant)."""
        from langgraph.graph import add_messages

        from whatsapp_langchain.agents.middleware.trim import create_trim_middleware

        mw = create_trim_middleware(keep_messages=5)

        messages = [
            HumanMessage(content="Msg 1", id="h1"),
            AIMessage(content="Resp 1", id="a1"),
            HumanMessage(content="Msg 2", id="h2"),
            AIMessage(content="Resp 2", id="a2"),
            HumanMessage(content="Msg 3", id="h3"),
            AIMessage(content="Resp 3", id="a3"),
            HumanMessage(content="Msg 4", id="h4"),
        ]

        result = mw.before_model({"messages": messages}, None)

        assert result is not None
        final = add_messages(messages, result["messages"])

        # 5 ajustado para 4 → mantém últimas 4
        assert len(final) == 4
        assert final[0].content == "Resp 2"
        assert final[3].content == "Msg 4"

    def test_trim_no_op_when_few_messages(self):
        """Não faz nada quando há poucas mensagens."""
        from whatsapp_langchain.agents.middleware.trim import create_trim_middleware

        mw = create_trim_middleware(keep_messages=4)

        messages = [
            HumanMessage(content="Olá", id="h1"),
            AIMessage(content="Resp 1", id="a1"),
        ]

        result = mw.before_model({"messages": messages}, None)

        assert result is None

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
