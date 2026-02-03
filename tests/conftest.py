"""Fixtures compartilhadas para testes.

Este arquivo é carregado automaticamente pelo pytest.
Contém fixtures reutilizáveis em todos os testes.
"""

import os

import pytest
from dotenv import load_dotenv

# Carrega .env antes de qualquer teste
load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def check_api_key():
    """Verifica se a API key está configurada antes de rodar testes de integração."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        pytest.skip("OPENROUTER_API_KEY não configurada. Pulando testes de integração.")


@pytest.fixture
def sample_messages():
    """Mensagens de exemplo para testes de contexto."""
    return [
        {"role": "user", "content": "Olá, meu nome é João."},
        {"role": "assistant", "content": "Olá João! Como posso ajudar?"},
        {"role": "user", "content": "Gosto de programação Python."},
        {"role": "assistant", "content": "Python é ótimo! O que desenvolve?"},
        {"role": "user", "content": "Estou aprendendo sobre LangChain."},
        {"role": "assistant", "content": "LangChain é excelente para agentes."},
        {"role": "user", "content": "Qual a diferença entre trim e summarize?"},
    ]
