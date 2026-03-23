# 🚀 Deploy Rápido no Railway - 15 MINUTOS

## 📋 Pré-requisitos
- Conta GitHub (para conectar o repositório)
- Conta Railway (grátis em railway.app)

---

## 🎯 PASSO A PASSO

### **1. Criar Repositório GitHub (3 min)**

No seu terminal:
```bash
cd "c:\Users\Desktop\OneDrive\Área de Trabalho\whatsapp-langchain"

# Inicializar git (se ainda não tiver)
git init

# Adicionar todos os arquivos
git add .

# Commit
git commit -m "feat: Agente FHE com UAZAPI e multimodal completo"

# Criar repositório no GitHub e fazer push
# (Crie em github.com/new)
git remote add origin https://github.com/SEU-USUARIO/whatsapp-fhe.git
git branch -M main
git push -u origin main
```

---

### **2. Criar Projeto no Railway (5 min)**

1. Acesse: https://railway.app/
2. Clique em "Start a New Project"
3. Escolha "Deploy from GitHub repo"
4. Selecione o repositório que você criou
5. Railway vai detectar automaticamente (Python/Nixpacks)

---

### **3. Adicionar PostgreSQL (2 min)**

1. No projeto Railway, clique em "+ New"
2. Escolha "Database" → "PostgreSQL"
3. Railway cria automaticamente e gera `DATABASE_URL`
4. Copie a `DATABASE_URL` (vai precisar)

---

### **4. Configurar Variáveis de Ambiente (3 min)**

No painel do seu serviço (API), vá em "Variables" e adicione:

```
OPENROUTER_API_KEY=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
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_MIDIA_MODEL=google/gemini-2.0-flash-exp

UAZAPI_BASE_URL=https://api-ax.uazapi.com
UAZAPI_INSTANCE_TOKEN=42e8b4fe-87fe-4118-a218-6857b566bc93
UAZAPI_PHONE_NUMBER=556196502174

DATABASE_URL=(cole a URL do PostgreSQL que o Railway gerou)

PORT=8000
LOG_LEVEL=info
LOG_JSON=true

RATE_LIMIT_PER_HOUR=30
MESSAGE_BUFFER_SECONDS=2.0
LLM_RATE_LIMIT_REQUESTS_PER_SECOND=0.5
LLM_RATE_LIMIT_MAX_BURST=10

POLL_INTERVAL_SECONDS=1.0
LEASE_SECONDS=60
MAX_ATTEMPTS=3

MEDIA_IMAGE_ENABLED=true
MEDIA_AUDIO_ENABLED=true

CONTEXT_STRATEGY=trim
TRIM_KEEP_TURNS=5

MEMORY_ENABLED=true
EMBEDDING_MODEL=openai/text-embedding-3-small
EMBEDDING_DIMS=1536
MEMORY_SEARCH_LIMIT=5
```

---

### **5. Deploy API e Worker (2 min)**

**Opção A: Dois serviços separados (RECOMENDADO)**

1. **API (já criado):**
   - Settings → Start Command: `uvicorn whatsapp_langchain.server.main:app --host 0.0.0.0 --port $PORT`

2. **Worker (criar novo):**
   - Clique em "+ New"
   - Escolha "Empty Service"
   - Settings → Start Command: `python -m whatsapp_langchain.worker.main`
   - Variables → Adicione as MESMAS variáveis da API

**Opção B: Um serviço com Procfile (MAIS SIMPLES)**
- Railway vai usar o Procfile automaticamente
- Vai rodar API (web) e Worker simultaneamente

---

### **6. Obter URL da API (1 min)**

1. No serviço da API, vá em "Settings"
2. Clique em "Generate Domain"
3. Railway vai gerar uma URL tipo: `https://whatsapp-fhe-production.up.railway.app`
4. **COPIE ESSA URL** (vai usar no webhook)

---

### **7. Configurar Webhook no UAZAPI (2 min)**

1. Acesse seu painel UAZAPI: https://uazapi.com/
2. Vá na instância `automatexteste2`
3. Configure webhook:
   - URL: `https://SUA-URL-RAILWAY.up.railway.app/webhook/uazapi?agent=fhe_assistant`
   - Método: POST
   - Eventos: Marque "message"

4. Salve e teste!

---

## ✅ PRONTO! SISTEMA NO AR

### Testando:

1. Envie mensagem para: **+55 61 9650-2174**
2. Digite: "Oi, quanto custa a formação?"
3. Aguarde resposta (5-10 segundos)

### Verificando logs:

- Railway → Seu serviço → Aba "Deployments"
- Clique no deployment ativo → "View Logs"
- Veja o agente processando mensagens em tempo real

---

## 🔍 Troubleshooting

### Erro: "Module not found"
- Certifique-se que fez `git push` de TODOS os arquivos
- Verifique que `pyproject.toml` está no repositório

### Erro: "Database connection failed"
- Verifique que `DATABASE_URL` está configurada
- Certifique-se que o PostgreSQL está rodando

### Webhook não recebe mensagens:
- Verifique URL do webhook no UAZAPI
- URL deve ter `/webhook/uazapi?agent=fhe_assistant`
- Certifique-se que a API está rodando (health check: `/health`)

---

## 💰 Custos

**Railway (Plano Gratuito):**
- $5 créditos/mês grátis
- Suficiente para testes e MVP
- Upgrade para $20/mês se precisar mais

**OpenRouter:**
- Claude 3.5 Sonnet: ~$3/milhão tokens input
- Gemini 2.0 Flash: ~$0.075/milhão tokens
- Estimativa: $10-20/mês para volume moderado

**UAZAPI:**
- Verifique seu plano atual
- Geralmente: R$ 49-99/mês dependendo do volume

---

## 🎉 Próximos Passos

Depois que estiver funcionando:

1. ✅ Testar todas as funcionalidades (texto, imagem, áudio, vídeo)
2. ✅ Ajustar prompts se necessário
3. ✅ Enviar número para o cliente testar
4. ✅ Monitorar logs e ajustar conforme feedback

---

**Desenvolvido para ACT Institute - Formação em Hipnose Ericksoniana**
