"""Agente assistant - assistente virtual genérico.

Este é o agente padrão do projeto, usado como exemplo e template
para criar novos agentes.

Uso:
    from whatsapp_langchain.agents.catalog.assistant import build_graph

    agent = build_graph()
    result = agent.invoke({"messages": [{"role": "user", "content": "Olá!"}]})
"""

from .agent import build_graph
from .prompts import SYSTEM_PROMPT

__all__ = ["build_graph", "SYSTEM_PROMPT"]
