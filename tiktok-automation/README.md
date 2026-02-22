# 🎬 TikTok Automation - Automação Completa e Gratuita

> Sistema profissional de automação para TikTok com IA gratuita, rodando 100% em Docker
> **COM DASHBOARD PROFISSIONAL INCLUÍDO!**

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 Visão Geral

Este projeto automatiza **completamente** a criação e postagem de vídeos no TikTok:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Notícias  │───▶│  IA (Roteiro)│───▶│  TTS (Áudio)│───▶│   Vídeo     │
│   RSS/API   │    │  OpenRouter │    │  Edge TTS   │    │  MoviePy    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                  │
                                                                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   TikTok    │◀───│   Upload    │◀───│  Legendas   │◀───│  Template   │
│   Posted    │    │  tiktok-up  │    │  SRT/VTT    │    │  Fundo      │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                  │
                                                                  ▼
                                                           ┌─────────────┐
                                                           │  📊 Dashboard│
                                                           │  Web UI     │
                                                           └─────────────┘
```

### ✅ O Que Este Sistema Faz

| Funcionalidade | Descrição | Custo |
|---------------|-----------|-------|
| 📰 Busca Notícias | RSS de G1, BBC, UOL, R7, CNN | Grátis |
| 🤖 Gera Roteiro | IA (Llama 3.3 70B, Gemma 3, etc.) | Grátis |
| 🔊 Narração | Edge TTS (vozes neurais Microsoft) | Grátis |
| 🎬 Cria Vídeo | MoviePy + FFmpeg com legendas | Grátis |
| 📤 Upload | tiktok-uploader via cookies | Grátis |
| 📊 Orquestração | n8n workflows + cron scheduler | Grátis |
| 📊 **Dashboard Web** | **Painel de controle completo** | **Grátis** |

---

## 📋 Requisitos

### Obrigatórios

- **Docker Desktop** (Windows/Mac) ou **Docker + Docker Compose** (Linux)
- **Git** (para clonar o repositório)
- **Conta no OpenRouter** (grátis): https://openrouter.ai/

### Opcionais

- **Conta no TikTok** (para upload)
- **Telegram** (para notificações)

---

## 🛠️ Instalação Rápida

### 1. Clone o Repositório

```bash
cd C:\Users\josia\Desktop\32d\tiktok-automation
```

### 2. Configure as Variáveis de Ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o .env com suas configurações
# (veja a seção de Configuração abaixo)
```

### 3. Inicie os Serviços

**Windows:**
```bash
scripts\start.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/start.sh
./scripts/start.sh
```

### 4. Acesse os Serviços

| Serviço | URL | Descrição |
|---------|-----|-----------|
| API | http://localhost:8000 | API principal |
| Swagger | http://localhost:8000/docs | Documentação da API |
| n8n | http://localhost:5678 | Workflows de automação |
| **📊 Dashboard** | **http://localhost:8000/dashboard** | **Painel de controle** |

---

## 📊 Dashboard (NOVO!)

O projeto agora inclui um **dashboard web completo** para gerenciar toda a automação:

### Funcionalidades do Dashboard

- ✅ **Visualização em Tempo Real** - Estatísticas atualizadas automaticamente
- ✨ **Geração Manual** - Crie conteúdo sob demanda
- 📤 **Upload Direto** - Envie vídeos para TikTok
- ⚙️ **Configurações** - Gerencie todas as opções
- 📜 **Histórico** - Veja todas as atividades
- 📰 **Geração Diária** - Trigger automático de conteúdo

### Acesso

```bash
http://localhost:8000/dashboard
```

### Recursos

| Recurso | Descrição |
|---------|-----------|
| Status Bar | Status dos serviços (API, TikTok, OpenRouter) |
| Quick Actions | Ações rápidas com 1 clique |
| Cards de Estatísticas | Métricas principais em tempo real |
| Atividade Recente | Log de todas as operações |
| Gerações Recentes | Histórico completo |
| Modal de Geração | Interface para criar conteúdo |
| Modal de Upload | Upload de vídeos existentes |

**Veja mais em:** [docs/DASHBOARD.md](docs/DASHBOARD.md)

---

## ⚙️ Configuração

### OpenRouter (IA Gratuita)

1. Acesse https://openrouter.ai/
2. Crie uma conta (grátis)
3. Vá em **Keys** e crie uma nova API key
4. Adicione no `.env`:

```env
OPENROUTER_API_KEY=sk_or_...
```

**Modelos gratuitos disponíveis:**
- `meta-llama/llama-3.3-70b-instruct:free` ⭐ Recomendado
- `google/gemma-3-27b-it:free`
- `mistralai/mistral-small-3.1-24b-instruct:free`
- `qwen/qwen3-coder:free`
- `deepseek/deepseek-r1-0528:free`

### TikTok SessionID

Para upload automático, você precisa do cookie `sessionid`:

**Método 1 - Developer Tools:**
1. Acesse https://www.tiktok.com e faça login
2. Pressione **F12**
3. Vá em **Application** > **Cookies** > **https://www.tiktok.com**
4. Copie o valor de `sessionid`

**Método 2 - Extensão:**
1. Instale a extensão **"Get cookies.txt"** (Chrome/Firefox)
2. Acesse tiktok.com
3. Clique na extensão e exporte os cookies
4. Extraia o valor de `sessionid`

Adicione no `.env`:
```env
TIKTOK_SESSIONID=seu_sessionid_aqui
```

### Telegram (Notificações Opcionais)

1. Crie um bot com **@BotFather** no Telegram
2. Pegue o token
3. Descubra seu **chat_id** com **@userinfobot**
4. Adicione no `.env`:

```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=123456789
```

---

## 📖 Uso

### API Endpoints Principais

#### 1. Gerar Conteúdo Diário (Completo)

```bash
curl -X POST http://localhost:8000/api/generate-daily
```

Este endpoint executa todo o fluxo:
1. Busca notícia aleatória
2. Gera roteiro com IA
3. Gera narração TTS
4. Cria vídeo com legendas
5. Retorna caminhos dos arquivos

**Resposta:**
```json
{
  "sucesso": true,
  "noticia": {
    "titulo": "Brasil lança novo foguete espacial",
    "fonte": "G1"
  },
  "roteiro": "🎭 VOCÊ NÃO VAI ACREDITAR!...",
  "audio": "/app/output/audio/roteiro_completo_20260222_090000.mp3",
  "video": "/app/output/videos/video_20260222_090000.mp4",
  "duracao": 32
}
```

#### 2. Gerar Apenas Roteiro

```bash
curl -X POST http://localhost:8000/api/generate-roteiro \
  -H "Content-Type: application/json" \
  -d '{
    "noticia": {
      "titulo": "Ministério da Saúde anuncia nova vacina",
      "descricao": "Vacina será distribuída gratuitamente pelo SUS",
      "link": "https://g1.globo.com/..."
    }
  }'
```

#### 3. Gerar Áudio TTS

```bash
curl -X POST "http://localhost:8000/api/generate-tts?texto=Olá%20mundo&voz=pt-BR-FranciscaNeural"
```

#### 4. Criar Vídeo

```bash
curl -X POST http://localhost:8000/api/create-video \
  -H "Content-Type: application/json" \
  -d '{
    "roteiro": {
      "hook": "🎭 Hook aqui",
      "noticia": "📰 Notícia",
      "piada": "😂 Piada",
      "cta": "👆 CTA"
    },
    "audio_path": "/app/output/audio/audio.mp3"
  }'
```

#### 5. Upload para TikTok

```bash
curl -X POST http://localhost:8000/api/upload-video \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "/app/output/videos/video.mp4",
    "titulo": "Vídeo engraçado #humor #viral"
  }'
```

### Workflows n8n

O projeto inclui um workflow pré-configurado:

1. **tiktok-daily-generation.json** - Geração diária automática

**Para importar:**
1. Acesse http://localhost:5678
2. Vá em **Workflows**
3. Clique em **Adicionar Workflow**
4. Menu **⋮** > **Import from File**
5. Selecione `workflows/n8n/tiktok-daily-generation.json`
6. Ative o workflow

---

## 📁 Estrutura do Projeto

```
tiktok-automation/
├── docker/
│   ├── Dockerfile              # Imagem principal
│   └── nginx/                  # Configuração Nginx (opcional)
├── src/
│   ├── main.py                 # API FastAPI
│   ├── config.py               # Configurações
│   └── modules/
│       ├── ia_generator.py     # Geração de roteiro (OpenRouter)
│       ├── tts_module.py       # Text-to-Speech (Edge TTS)
│       ├── video_creator.py    # Criação de vídeo (MoviePy)
│       ├── tiktok_uploader_module.py  # Upload TikTok
│       └── news_fetcher.py     # Busca de notícias RSS
├── workflows/n8n/
│   └── tiktok-daily-generation.json
├── scripts/
│   ├── start.sh / start.bat    # Scripts de inicialização
│   └── test_sessionid.py       # Testar SessionID
├── output/
│   ├── videos/                 # Vídeos gerados
│   ├── audio/                  # Áudios TTS
│   └── scripts/                # Roteiros em texto
├── templates/
│   └── fundo_padrao.png        # Template de fundo
├── logs/                       # Logs da aplicação
├── config/                     # Configurações adicionais
├── docker-compose.yml          # Orquestração Docker
├── requirements.txt            # Dependências Python
├── .env.example                # Exemplo de configuração
└── README.md                   # Esta documentação
```

---

## 🔧 Comandos Úteis

### Ver Logs

```bash
# Todos os logs
docker-compose logs -f

# Logs específicos
docker-compose logs -f tiktok-automation
docker-compose logs -f n8n
docker-compose logs -f scheduler
```

### Reiniciar Serviços

```bash
docker-compose restart
```

### Parar Serviços

```bash
docker-compose down
```

### Rebuild Completo

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Acessar Container

```bash
# Container principal
docker exec -it tiktok-automation bash

# n8n
docker exec -it n8n bash
```

---

## 🎨 Personalização

### Templates de Humor

Edite `src/config.py` para adicionar seus próprios templates:

```python
humor_templates = [
    {
        "name": "Seu Template",
        "hook": "🎭 Seu hook aqui",
        "style": "seu_estilo",
        "tone": "seu_tom",
    },
]
```

### Fontes de Notícias

Adicione mais fontes RSS em `src/config.py`:

```python
news_sources = [
    {
        "name": "Sua Fonte",
        "url": "https://sua-fonte.com/rss",
        "language": "pt-BR",
        "enabled": True,
    },
]
```

### Vozes TTS

Veja vozes disponíveis:

```bash
curl http://localhost:8000/api/voices
```

---

## 🐛 Solução de Problemas

### IA Não Gera Roteiro

**Problema:** Erro 401 ou "API key inválida"

**Solução:**
1. Verifique se `OPENROUTER_API_KEY` está correta no `.env`
2. Teste a key em https://openrouter.ai/playground
3. Verifique os logs: `docker-compose logs tiktok-automation`

### Upload Falha

**Problema:** "SessionID inválido"

**Solução:**
1. SessionID expira! Obtenha um novo
2. Teste com o script: `python scripts/test_sessionid.py`
3. Verifique se está logado no TikTok

### Vídeo Não É Criado

**Problema:** Erro no MoviePy/FFmpeg

**Solução:**
1. Verifique se o áudio foi gerado: `ls output/audio/`
2. Verifique permissões das pastas
3. Rebuild do container: `docker-compose build`

### n8n Não Conecta na API

**Problema:** Erro de conexão no workflow

**Solução:**
1. Use `http://tiktok-automation:8000` (nome do serviço, não localhost)
2. Verifique se ambos estão na mesma rede Docker
3. Teste: `docker exec n8n wget http://tiktok-automation:8000/health`

---

## 📊 Limites e Custos

### OpenRouter (Gratuito)

| Limite | Valor |
|--------|-------|
| Requisições/minuto | 20 |
| Requisições/dia | 200 |
| Custo | $0 |

**Dica:** Com 200 requisições/dia, você pode gerar ~60-100 roteiros (dependendo do tamanho).

### Edge TTS

- **Ilimitado** e gratuito
- Qualidade neural (Azure)
- 10+ vozes em português

### TikTok Upload

- **Gratuito** via cookies
- Limite: ~25 vídeos/dia (limite do TikTok)
- Requer SessionID válido

---

## 🔒 Segurança

### Boas Práticas

1. **Nunca compartilhe** seu `.env`
2. **Mude a encryption key** do n8n em produção
3. **Renove o SessionID** periodicamente (expira em ~7-30 dias)
4. Use **HTTPS** se expor o n8n publicamente

### Adicionar HTTPS (Opcional)

Para produção, use o perfil com Nginx:

```bash
docker-compose --profile with-proxy up -d
```

Configure SSL no Nginx com Let's Encrypt.

---

## 🚀 Produção

### Deploy em Servidor Remoto

```bash
# 1. Clone em servidor VPS
git clone <repo>
cd tiktok-automation

# 2. Configure .env
cp .env.example .env
# Edite N8N_HOST para seu domínio

# 3. Inicie
docker-compose up -d

# 4. Configure reverse proxy (Nginx/Caddy)
# 5. SSL com Let's Encrypt
```

### Monitoramento

```bash
# Logs em tempo real
docker-compose logs -f

# Uso de recursos
docker stats

# Health check
curl http://localhost:8000/health
```

### Backup

```bash
# Backup do n8n (workflows salvos)
docker run --rm \
  -v tiktok-n8n-data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/n8n-backup.tar.gz /data
```

---

## 📈 Roadmap

- [ ] Suporte a múltiplas contas TikTok
- [ ] Geração de thumbnails automática
- [ ] Analytics de performance dos vídeos
- [ ] A/B testing de roteiros
- [ ] Integração com Instagram Reels
- [ ] Integração com YouTube Shorts

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/MinhaFeature`)
3. Commit (`git commit -m 'Adiciona MinhaFeature'`)
4. Push (`git push origin feature/MinhaFeature`)
5. Pull Request

---

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

## 🙏 Agradecimentos

- **OpenRouter** - IA gratuita de qualidade
- **Microsoft** - Edge TTS gratuito
- **tiktok-uploader** - Upload automatizado
- **n8n** - Orquestração open-source
- **MoviePy** - Edição de vídeo em Python

---

## 📞 Suporte

- **Issues:** GitHub Issues
- **Discord:** (link futuro)
- **Email:** (link futuro)

---

**Feito com ❤️ para criadores de conteúdo brasileiros**

🎭 **Vamos viralizar!**
