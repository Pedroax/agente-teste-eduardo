# 🚀 DEPLOY COMPLETO - GitHub + Railway

## Passo 1: Criar Repositório GitHub (2 min)

### 1.1 Criar repo no GitHub
1. Acesse: https://github.com/new
2. Nome do repositório: `whatsapp-fhe` (ou o nome que preferir)
3. Deixe como **Private** (por segurança das credenciais)
4. **NÃO** marque "Initialize with README"
5. Clique em "Create repository"

### 1.2 Fazer push do código

No seu terminal, execute:

```bash
# Remover o remote antigo
git remote remove origin

# Adicionar novo remote (SUBSTITUA SEU-USUARIO pelo seu username GitHub)
git remote add origin https://github.com/SEU-USUARIO/whatsapp-fhe.git

# Fazer push
git push -u origin main
```

Se pedir autenticação:
- Username: seu username do GitHub
- Password: use um **Personal Access Token** (não a senha normal)
  - Crie em: https://github.com/settings/tokens
  - Marque: `repo` (acesso completo)

---

## Passo 2: Deploy no Railway (10 min)

### 2.1 Criar Projeto
1. Acesse: https://railway.app/
2. Clique em **"New Project"**
3. Escolha **"Deploy from GitHub repo"**
4. Autorize o Railway a acessar seus repositórios
5. Selecione o repositório `whatsapp-fhe`
6. Railway vai começar o deploy automaticamente

### 2.2 Adicionar PostgreSQL
1. No projeto, clique em **"+ New"**
2. Escolha **"Database"** → **"Add PostgreSQL"**
3. Railway cria automaticamente
4. Aguarde alguns segundos até ficar "Active"

### 2.3 Configurar Variáveis de Ambiente da API

1. Clique no serviço da **API** (não o banco)
2. Vá em **"Variables"**
3. Cole TODAS as variáveis do arquivo `RAILWAY_ENV_VARS.txt`
4. **IMPORTANTE:** Para `DATABASE_URL`, clique em "Add Reference":
   - Selecione o banco PostgreSQL
   - Escolha `DATABASE_URL`
   - Isso vai vincular automaticamente

### 2.4 Criar Serviço Worker

**Opção A: Usar Procfile (RECOMENDADO - mais simples)**
- O Railway já detecta o Procfile automaticamente
- Vai rodar API e Worker no mesmo serviço
- Pule para o Passo 2.5

**Opção B: Serviços separados (mais controle)**
1. Clique em **"+ New"** → **"Empty Service"**
2. Conecte ao mesmo repositório GitHub
3. Vá em **"Settings"** → **"Start Command"**:
   ```
   python -m whatsapp_langchain.worker.main
   ```
4. Vá em **"Variables"**
5. Adicione as MESMAS variáveis da API

### 2.5 Obter URL da API

1. Clique no serviço da API
2. Vá em **"Settings"**
3. Seção **"Networking"**
4. Clique em **"Generate Domain"**
5. Railway vai gerar algo como:
   ```
   https://whatsapp-fhe-production.up.railway.app
   ```
6. **COPIE ESSA URL** - vai usar no webhook

---

## Passo 3: Configurar Webhook UAZAPI (3 min)

### 3.1 Acessar Painel UAZAPI
1. Acesse: https://uazapi.com/
2. Faça login
3. Vá na instância **automatexteste2**

### 3.2 Configurar Webhook
1. Vá em **"Webhook"** ou **"Configurações"**
2. Configure:
   - **URL do Webhook:**
     ```
     https://SUA-URL-RAILWAY.up.railway.app/webhook/uazapi?agent=fhe_assistant
     ```
     (Substitua `SUA-URL-RAILWAY` pela URL que copiou)

   - **Método:** POST
   - **Eventos:** Marque **"message"** ou **"all"**

3. **Salve** a configuração

---

## Passo 4: Testar Tudo! (5 min)

### 4.1 Verificar Deploy
1. No Railway, vá em **"Deployments"**
2. Certifique-se que está **"Active"** (verde)
3. Clique no deployment → **"View Logs"**
4. Deve mostrar: `Application startup complete`

### 4.2 Testar Health Check
Abra no navegador:
```
https://SUA-URL-RAILWAY.up.railway.app/health
```

Deve retornar:
```json
{"status": "healthy"}
```

### 4.3 Testar Mensagem WhatsApp

**Teste 1: Texto Simples**
1. Envie mensagem para: **+55 61 9650-2174**
2. Digite: "Oi, quanto custa a formação?"
3. Aguarde 5-15 segundos
4. Deve receber resposta do agente

**Teste 2: Imagem**
1. Envie uma imagem
2. Agente deve descrever a imagem

**Teste 3: Áudio**
1. Envie um áudio
2. Agente deve transcrever e responder

**Teste 4: Ferramentas**
1. Digite: "Sou psicólogo especializado em ansiedade, cobra R$ 300 por sessão"
2. Agente deve usar a ferramenta `roi_calculator`

### 4.4 Monitorar Logs em Tempo Real

No Railway:
1. **"Deployments"** → Clique no deployment ativo
2. **"View Logs"**
3. Você vai ver:
   ```
   INFO: Mensagem recebida de whatsapp:+5561...
   INFO: Processando mensagem...
   INFO: Resposta enviada
   ```

---

## 🎯 CHECKLIST FINAL

- [ ] Código no GitHub
- [ ] Deploy Railway funcionando (verde)
- [ ] PostgreSQL conectado
- [ ] Variáveis de ambiente configuradas
- [ ] Webhook UAZAPI configurado
- [ ] Health check retorna 200
- [ ] Teste de mensagem texto OK
- [ ] Teste de imagem OK
- [ ] Teste de áudio OK
- [ ] Teste de ferramenta (ROI) OK

---

## 🔍 Troubleshooting

### Deploy falhou no Railway
- Verifique os logs: pode ser falta de variável
- Certifique-se que `DATABASE_URL` está configurada
- Verifique que o Procfile está no repositório

### Webhook não recebe mensagens
1. Verifique URL do webhook no UAZAPI
2. URL deve terminar com `/webhook/uazapi?agent=fhe_assistant`
3. Teste o health check primeiro

### Agente não responde
1. Verifique logs do Worker no Railway
2. Certifique-se que Worker está rodando
3. Verifique `OPENROUTER_API_KEY` está correta

### Erro de banco de dados
1. Certifique-se que PostgreSQL está "Active"
2. Verifique se `DATABASE_URL` está configurada
3. Tente "Restart" no serviço

---

## 📱 Demonstração para o Cliente

Quando for mostrar para o cliente FHE:

### Roteiro Sugerido:

1. **Abertura:**
   "Vou te mostrar o agente funcionando em tempo real no WhatsApp"

2. **Teste 1 - Texto:**
   - Mostre o número: +55 61 9650-2174
   - Envie: "Oi, quanto custa a formação?"
   - Destaque a **naturalidade** da resposta

3. **Teste 2 - Imagem:**
   - Envie uma imagem (ex: logo da empresa)
   - Agente vai descrever e contextualizar
   - "Veja que ele ENTENDE imagens, não só texto"

4. **Teste 3 - Ferramenta ROI:**
   - Envie: "Sou psicólogo, atendo ansiedade, cobro R$ 250"
   - Agente vai calcular ROI personalizado
   - "Ele PENSA e usa ferramentas, não é FAQ"

5. **Teste 4 - Memória:**
   - Envie: "Qual era minha especialidade mesmo?"
   - Agente vai lembrar
   - "Ele tem MEMÓRIA de longo prazo"

6. **Fechar:**
   "Isso é só um MVP. No projeto completo, integramos:
   - Sistema de agendamento
   - CRM
   - Analytics
   - Múltiplos agentes especializados"

---

## 💰 Custos Estimados

**Railway:**
- Plano Hobby: $5/mês (500h + $5 créditos)
- Plano Pro: $20/mês (se precisar escalar)

**OpenRouter:**
- Claude 3.5 Sonnet: ~$3/1M tokens
- Gemini 2.0 Flash: ~$0.075/1M tokens
- Estimativa: $10-20/mês (volume moderado)

**UAZAPI:**
- Conforme seu plano atual

**Total estimado: R$ 150-250/mês para MVP**

---

## 🎉 Próximos Passos (Pós-aprovação)

1. Adicionar analytics (tempo de resposta, taxa de conversão)
2. Criar dashboard de métricas
3. Implementar A/B testing de prompts
4. Adicionar mais ferramentas (agendamento, pagamento)
5. Integrar com CRM do cliente

---

**Desenvolvido para ACT Institute - Formação em Hipnose Ericksoniana**
**Agente: FHE Assistant | Powered by Claude 3.5 Sonnet + Gemini 2.0 Flash**
