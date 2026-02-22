# 🚀 Guia de Início Rápido - TikTok Automation

> Comece a automatizar seus vídeos do TikTok em 10 minutos!

---

## ⏱️ Timeline de Instalação

| Passo | Tempo | Descrição |
|-------|-------|-----------|
| 1 | 2 min | Instalar Docker |
| 2 | 1 min | Clonar repositório |
| 3 | 3 min | Configurar .env |
| 4 | 3 min | Obter API keys |
| 5 | 1 min | Iniciar serviços |
| **Total** | **~10 min** | ✅ Pronto para usar! |

---

## 📋 Passo a Passo

### Passo 1: Instalar Docker (2 min)

**Windows:**
1. Baixe em: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
2. Execute o instalador
3. Abra Docker Desktop e aguarde iniciar

**Verifique:**
```bash
docker --version
# Deve mostrar: Docker version 20.x.x...
```

---

### Passo 2: Clonar Repositório (1 min)

```bash
cd C:\Users\josia\Desktop\32d
# O projeto já está na pasta tiktok-automation
```

---

### Passo 3: Configurar .env (3 min)

```bash
cd tiktok-automation
copy .env.example .env
```

**Edite o `.env` e configure:**

```env
# OBRIGATÓRIO - OpenRouter (IA grátis)
OPENROUTER_API_KEY=

# OPCIONAL - TikTok (só se quiser upload automático)
TIKTOK_SESSIONID=

# DEIXE COMO ESTÁ
N8N_HOST=localhost
LOG_LEVEL=INFO
TZ=America/Sao_Paulo
```

---

### Passo 4: Obter API Keys (3 min)

#### OpenRouter (Obrigatório para IA)

1. Acesse https://openrouter.ai/
2. Clique em **Sign In** (crie conta grátis)
3. Vá em **Keys** no menu
4. Clique em **Create Key**
5. Dê um nome (ex: "TikTok Automation")
6. Copie a key e cole no `.env`

**É 100% grátis!** Você recebe créditos gratuitos todo mês.

#### TikTok SessionID (Opcional - para upload automático)

1. Acesse https://www.tiktok.com
2. Faça login na sua conta
3. Pressione **F12**
4. Vá em **Application** > **Cookies**
5. Copie o valor de `sessionid`
6. Cole no `.env`

**Sem SessionID:** O sistema gera o vídeo, mas você posta manualmente.

---

### Passo 5: Iniciar Serviços (1 min)

```bash
# No PowerShell ou Prompt
scripts\start.bat
```

**Ou manualmente:**
```bash
docker-compose up -d
```

**Aguarde 30 segundos** para os serviços iniciarem.

---

## ✅ Verificação

### 1. Teste a API

Abra no navegador:
- http://localhost:8000/health
- http://localhost:8000/api/status

**Deve mostrar:**
```json
{
  "status": "healthy",
  ...
}
```

### 2. Teste a Geração

```bash
curl -X POST http://localhost:8000/api/generate-daily
```

**Ou acesse no navegador:**
- http://localhost:8000/docs
- Clique em **POST /api/generate-daily**
- Clique em **Try it out**
- Clique em **Execute**

### 3. Acesse o n8n

http://localhost:5678

**Primeiro acesso:**
1. Crie sua conta (admin/admin)
2. Vá em **Workflows**
3. Importe o arquivo `workflows/n8n/tiktok-daily-generation.json`

---

## 🎬 Primeiro Vídeo

### Método 1: Via API (Recomendado)

```bash
curl -X POST http://localhost:8000/api/generate-daily
```

**Resposta esperada:**
```json
{
  "sucesso": true,
  "noticia": {...},
  "video": "/app/output/videos/video_20260222_090000.mp4",
  "duracao": 32
}
```

### Método 2: Via n8n

1. No n8n, ative o workflow importado
2. Clique em **Execute Workflow**
3. Aguarde o processo

### Método 3: Via Swagger

1. Acesse http://localhost:8000/docs
2. POST `/api/generate-daily`
3. **Try it out** → **Execute**

---

## 📍 Onde Encontrar os Arquivos

### Vídeos Gerados

```
tiktok-automation/output/videos/
```

### Áudios/TTS

```
tiktok-automation/output/audio/
```

### Roteiros em Texto

```
tiktok-automation/output/scripts/
```

---

## 🔧 Próximos Passos

### 1. Personalizar Templates

Edite `src/config.py`:
```python
humor_templates = [
    # Adicione seus próprios templates
]
```

### 2. Adicionar Fontes de Notícias

Edite `src/config.py`:
```python
news_sources = [
    # Adicione mais RSS feeds
]
```

### 3. Configurar Notificações Telegram

No `.env`:
```env
TELEGRAM_BOT_TOKEN=seu_token
TELEGRAM_CHAT_ID=seu_chat_id
```

### 4. Agendar Postagens

O scheduler já está configurado para:
- **09:00** - Gerar conteúdo
- **18:00** - Fazer upload

Edite no `docker-compose.yml` se quiser mudar.

---

## ❓ Problemas Comuns

### "Connection refused"

**Solução:** Aguarde 30 segundos após iniciar. Os serviços demoram um pouco.

```bash
docker-compose logs -f
```

### "OPENROUTER_API_KEY not set"

**Solução:** Verifique se o `.env` está na mesma pasta do `docker-compose.yml`.

### "No module named 'X'"

**Solução:** Rebuild do container:

```bash
docker-compose build --no-cache
docker-compose up -d
```

### SessionID inválido

**Solução:** SessionID expira! Obtenha um novo:

1. Logout no TikTok
2. Login novamente
3. Copie novo sessionid
4. Atualize `.env`
5. `docker-compose restart tiktok-automation`

---

## 📊 Comandos Úteis do Dia a Dia

```bash
# Ver logs em tempo real
docker-compose logs -f

# Ver apenas erros
docker-compose logs --tail=100 | grep ERROR

# Reiniciar serviço
docker-compose restart tiktok-automation

# Parar tudo
docker-compose down

# Iniciar tudo
docker-compose up -d

# Ver status
docker-compose ps

# Acessar container
docker exec -it tiktok-automation bash
```

---

## 🎯 Checklist Diário

- [ ] Verificar se serviços estão rodando: `docker-compose ps`
- [ ] Checar logs de erro: `docker-compose logs --tail=50`
- [ ] Verificar vídeos gerados: `ls output/videos/`
- [ ] Confirmar uploads (se automático)

---

## 📞 Precisa de Ajuda?

1. **Logs:** `docker-compose logs -f`
2. **Health Check:** http://localhost:8000/health
3. **Status:** http://localhost:8000/api/status
4. **Swagger:** http://localhost:8000/docs

---

## 🎉 Pronto!

Agora é só esperar o horário agendado ou triggerar manualmente!

**Horários padrão:**
- 🌅 **09:00** - Gera novo conteúdo
- 🌆 **18:00** - Posta no TikTok (horário de pico)

**Para teste imediato:**
```bash
curl -X POST http://localhost:8000/api/generate-daily
```

---

**Boa sorte e bons vídeos! 🎬🚀**
