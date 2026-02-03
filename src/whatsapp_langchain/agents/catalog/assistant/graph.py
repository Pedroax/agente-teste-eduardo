"""Grafo para uso com langgraph dev.

Este arquivo exporta uma variável `graph` para integração com `langgraph dev`.
O servidor de produção usa `build_graph()` de agent.py, passando o checkpointer.
"""

from whatsapp_langchain.agents.catalog.assistant.agent import build_graph

# Grafo compilado para langgraph dev (in-memory, sem checkpointer)
graph = build_graph()
