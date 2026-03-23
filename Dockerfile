FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copiar código
COPY src/ ./src/

EXPOSE 8000

# Comando será sobrescrito pelo Procfile no Railway
CMD ["echo", "Use Procfile"]
