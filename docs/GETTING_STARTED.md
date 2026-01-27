# Primeiros Passos

## Pré-requisitos

- **Python 3.12+** — [python.org](https://www.python.org/)
- **Node.js 20+** — [nodejs.org](https://nodejs.org/) (para o Admin Panel)
- **Docker e Docker Compose** — [docker.com](https://www.docker.com/)
- **Conta OpenRouter** — [openrouter.ai](https://openrouter.ai/) (chave de API para os modelos)

## 1. Setup

```bash
git clone <repo-url>
cd whatsapp-langchain

# Cria ambiente virtual e instala dependências
make setup

# Copia o template de variáveis de ambiente
cp .env.example .env
```

Edite o `.env` com suas credenciais:

```bash
# Obrigatório
OPENROUTER_API_KEY=sk-or-v1-...

# O resto pode ficar com os valores padrão para dev
```

## 2. Desenvolvendo Agentes (LangGraph Studio)

O jeito mais rápido de começar é usando o LangGraph Studio:

```bash
make dev
```

Isso abre o LangGraph Studio no navegador. Você pode conversar com o agente `assistant` e ver o grafo executando em tempo real.

O agente é definido em `src/whatsapp_langchain/agents/catalog/assistant/`. Edite e veja as mudanças ao vivo.

## 3. Rodando a Infraestrutura

### Com Docker (recomendado)

```bash
# Sobe API + Worker + PostgreSQL
make up

# Em outro terminal, sobe o Admin Panel
make frontend
```

Serviços disponíveis:
- **API**: http://localhost:8000
- **Admin Panel**: http://localhost:3000
- **Health Check**: http://localhost:8000/health

### Sem Docker (desenvolvimento)

Se preferir rodar cada serviço separadamente:

```bash
# Terminal 1: Banco de dados
make db

# Terminal 2: API
make api

# Terminal 3: Worker
make worker

# Terminal 4: Frontend
make frontend
```

## 4. Testando

### Simular uma mensagem

Sem precisar do Twilio, você pode simular um webhook:

```bash
curl -X POST http://localhost:8000/webhook/twilio?agent=assistant \
  -d "MessageSid=SM123" \
  -d "From=whatsapp:+5511999999999" \
  -d "To=whatsapp:+5511888888888" \
  -d "Body=Olá, tudo bem?" \
  -d "NumMedia=0"
```

A mensagem entra na fila. O Worker processa e loga a resposta no terminal.

### Endpoint síncrono (educacional)

Para comparar com o fluxo assíncrono:

```bash
curl -X POST http://localhost:8000/webhook/sync?agent=assistant \
  -d "MessageSid=SM123" \
  -d "From=whatsapp:+5511999999999" \
  -d "To=whatsapp:+5511888888888" \
  -d "Body=Olá, tudo bem?" \
  -d "NumMedia=0"
```

Este endpoint processa inline e retorna a resposta diretamente. Compare a latência com o endpoint async usando os [testes de stress](docs/STRESS_TESTING.md).

## 5. Admin Panel

Acesse http://localhost:3000 com as credenciais:

- **Usuário**: valor de `ADMIN_USER` no `.env` (padrão: `admin`)
- **Senha**: valor de `ADMIN_PASSWORD` no `.env`

No painel você pode:
- Ver métricas (conversas, mensagens processadas, fila)
- Acompanhar conversas em tempo real
- Monitorar o status da fila

## Conectando ao Twilio (opcional para dev)

Para testes locais, o Twilio não é necessário. O Worker loga as respostas no terminal.

Para conectar ao WhatsApp real, você tem duas opções:

1. **Deploy no Railway** (recomendado) — Veja [Deploy](DEPLOY.md)
2. **ngrok** (opcional) — Se quiser testar localmente com WhatsApp real:
   ```bash
   ngrok http 8000
   # Configure o webhook no Twilio com a URL do ngrok
   ```

## Troubleshooting

### API não conecta ao banco

```
Verifique se o PostgreSQL está rodando:
docker-compose ps

Verifique a variável DATABASE_URL no .env
```

### Worker não processa mensagens

```
Verifique se o Worker está rodando:
make worker

Verifique os logs:
make logs
```

### Agente não encontrado

```
Verifique se o agente está registrado no langgraph.json
Verifique o parâmetro ?agent= na URL do webhook
```

## Próximos Passos

- [Criando Agentes](ADDING_AGENTS.md) — Crie seu próprio agente
- [Arquitetura](ARCHITECTURE.md) — Entenda como o sistema funciona
- [Deploy](DEPLOY.md) — Coloque em produção
