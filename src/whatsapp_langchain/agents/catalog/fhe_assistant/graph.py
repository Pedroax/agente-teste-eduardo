"""Export para langgraph dev CLI.

Este módulo exporta a variável `graph` esperada pelo langgraph dev.
Para desenvolvimento local:

    langgraph dev

O CLI vai encontrar e servir este grafo em http://localhost:8123
"""

from .agent import build_graph

# langgraph dev espera uma variável chamada 'graph'
# Compilamos sem checkpointer/store (in-memory)
graph = build_graph()
