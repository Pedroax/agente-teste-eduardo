# Deploy no Railway

## Pré-requisitos

- Conta no [Railway](https://railway.app/)
- Conta no [Twilio](https://www.twilio.com/) com número WhatsApp
- Conta no [OpenRouter](https://openrouter.ai/)
- Repositório no GitHub

## Visão Geral

O projeto roda como 4 serviços isolados no Railway:

```
┌─────────────────────────────────────────────────┐
│                Railway Project                  │
├────────────┬────────────┬──────────┬────────────┤
│    API     │   Worker   │ Frontend │ PostgreSQL │
│  FastAPI   │   Python   │ Next.js  │  Database  │
└────────────┴────────────┴──────────┴────────────┘
```

## Passo 1: Criar o Projeto

1. Acesse [railway.app](https://railway.app/)
2. **New Project** → **Deploy from GitHub repo**
3. Conecte seu repositório

## Passo 2: Adicionar PostgreSQL

1. No projeto, clique em **+ New**
2. Selecione **Database → PostgreSQL**
3. Aguarde a criação

## Passo 3: Configurar a API

1. **+ New → GitHub Repo** (mesmo repositório)
2. Em **Settings**:
   - **Dockerfile Path**: `Dockerfile.api`
3. Em **Variables**:
   ```
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   ENVIRONMENT=prod
   LOG_LEVEL=info
   VALIDATE_TWILIO_SIGNATURE=true
   RATE_LIMIT_PER_HOUR=30
   MESSAGE_BUFFER_SECONDS=2.0
   ADMIN_USER=admin
   ADMIN_PASSWORD=<senha-segura>
   ```
4. Em **Settings → Networking**: **Generate Domain**
5. Anote a URL (ex: `api-production-xxxx.up.railway.app`)

## Passo 4: Configurar o Worker

1. **+ New → GitHub Repo** (mesmo repositório)
2. Em **Settings**:
   - **Dockerfile Path**: `Dockerfile.worker`
3. Em **Variables**:
   ```
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   ENVIRONMENT=prod
   LOG_LEVEL=info
   OPENROUTER_API_KEY=sk-or-v1-...
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   TWILIO_ACCOUNT_SID=AC...
   TWILIO_AUTH_TOKEN=...
   TWILIO_FROM_NUMBER=whatsapp:+55...
   POLL_INTERVAL_SECONDS=1
   LEASE_SECONDS=60
   MAX_ATTEMPTS=3
   MEDIA_IMAGE_ENABLED=true
   MEDIA_AUDIO_ENABLED=true
   TYPING_INDICATOR_ENABLED=true
   LLM_RATE_LIMIT_REQUESTS_PER_SECOND=0.5
   LLM_RATE_LIMIT_MAX_BURST=10
   ```

O Worker não precisa de domínio público.

## Passo 5: Configurar o Frontend

1. **+ New → GitHub Repo** (mesmo repositório)
2. Em **Settings**:
   - **Root Directory**: `frontend`
3. Em **Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://api-production-xxxx.up.railway.app
   ```
4. Em **Settings → Networking**: **Generate Domain**

## Passo 6: Configurar o Twilio

1. Acesse [Twilio Console](https://console.twilio.com/)
2. Vá para **Messaging → WhatsApp**
3. Configure o webhook:
   - **URL**: `https://api-production-xxxx.up.railway.app/webhook/twilio?agent=assistant`
   - **Method**: `POST`

## Passo 7: Verificar

### Health Check

```bash
curl https://api-production-xxxx.up.railway.app/health
# {"status": "ok", "database": "connected"}
```

### Listar Agentes

```bash
curl https://api-production-xxxx.up.railway.app/api/agents
# ["assistant"]
```

### Testar

Envie uma mensagem para seu número WhatsApp e verifique:
1. **Logs do API**: Railway → api → Logs
2. **Logs do Worker**: Railway → worker → Logs
3. **Resposta no WhatsApp**

## Troubleshooting

| Problema | Solução |
|----------|---------|
| Mensagem não chega na API | Verifique webhook no Twilio e domínio da API |
| Worker não processa | Verifique `DATABASE_URL` e credenciais do Twilio |
| Erro de conexão com banco | Confirme que PostgreSQL está rodando, verifique `DATABASE_URL` |
| Agente não encontrado | Verifique `?agent=` na URL e se o código foi deployado |

## Escalar

### Mais Workers

Para processar mais mensagens, duplique o serviço Worker no Railway. Ambos vão competir pela fila — o lock (`FOR UPDATE SKIP LOCKED`) garante que nenhuma mensagem é processada duas vezes.

### Mais Recursos

Em **Settings → Resources**, aumente RAM e vCPU conforme necessário.

## Custos Estimados

O Railway cobra pelo uso real de recursos (CPU, RAM, rede). Com baixo volume, os 4 serviços compartilham os créditos do plano:

| Plano | Custo | Inclui |
|-------|-------|--------|
| **Hobby** | $5/mês | $5 de créditos de uso + recursos básicos |
| **Pro** | $20/mês | $20 de créditos + mais recursos |

Com baixo volume (dezenas de conversas por dia), o plano Hobby de **~$5/mês** é suficiente para rodar todos os 4 serviços. O custo sobe conforme o uso de CPU/RAM aumenta.

## Auto-Deploy

O Railway faz deploy automático a cada push para a branch `main`. Não precisa de CI/CD separado — o próprio Railway builda e deploya cada serviço automaticamente.

Para rollback: Railway → Serviço → **Deployments** → selecione um deploy anterior → **Redeploy**.
