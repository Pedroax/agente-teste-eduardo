# -*- coding: utf-8 -*-
"""Teste rápido do agente FHE sem precisar de todo o stack.

Testa o agente diretamente sem banco de dados.
"""

import asyncio
import sys
from langchain_core.messages import HumanMessage

# Fix encoding para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Simular configuração mínima
import os
os.environ["OPENROUTER_API_KEY"] = "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"
os.environ["OPENROUTER_BASE_URL"] = "https://openrouter.ai/api/v1"
os.environ["OPENROUTER_MODEL"] = "anthropic/claude-3.5-sonnet"
os.environ["CONTEXT_STRATEGY"] = "none"
os.environ["MEMORY_ENABLED"] = "false"
os.environ["LOG_LEVEL"] = "info"
os.environ["LOG_JSON"] = "false"

from whatsapp_langchain.agents.catalog.fhe_assistant import build_graph


async def test_agente():
    """Testa o agente FHE com conversas simuladas."""

    print("[AGENTE] Iniciando FHE Assistant...")
    print("=" * 60)

    # Criar agente sem checkpointer/store (in-memory)
    graph = build_graph(checkpointer=None, store=None)

    # Simular conversas
    conversas = [
        "Oi, quanto custa a formação?",
        "Sou psicóloga, atendo ansiedade",
        "R$ 8.000 é muito caro",
        "Queria ter certeza que funciona"
    ]

    for i, mensagem in enumerate(conversas, 1):
        print(f"\n{'='*60}")
        print(f"[LEAD {i}/4]: {mensagem}")
        print(f"{'='*60}\n")

        try:
            result = await graph.ainvoke(
                {"messages": [HumanMessage(content=mensagem)]},
                config={"configurable": {"thread_id": "test_conversation"}}
            )

            resposta = result["messages"][-1].content

            print(f"[AGENTE FHE]:\n{resposta}\n")

        except Exception as e:
            print(f"[ERRO]: {e}\n")
            import traceback
            traceback.print_exc()
            break

    print("=" * 60)
    print("[OK] Teste concluido!")


if __name__ == "__main__":
    asyncio.run(test_agente())
