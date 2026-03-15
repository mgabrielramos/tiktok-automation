# 🎬 TikTok Automation

Automação completa e gratuita para criação e publicação de vídeos no TikTok com IA.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](tiktok-automation/LICENSE)

---

## 📋 Visão Geral

Este repositório contém dois sistemas complementares de automação para TikTok:

### 1. 🐍 Sistema Python Completo (`tiktok-automation/`)

Pipeline end-to-end que automatiza **toda** a criação e postagem de vídeos:

```
Notícias (RSS) → IA (Roteiro) → TTS (Áudio) → Vídeo (MoviePy) → TikTok (Upload)
```

- ✅ Busca de notícias de 5+ fontes RSS (G1, BBC Brasil, UOL, R7, CNN Brasil)
- ✅ Geração de roteiros de humor com IA gratuita (OpenRouter — Llama 3.3 70B, Gemma 3, etc.)
- ✅ Narração automática com Edge TTS (vozes neurais Microsoft, 100% gratuito)
- ✅ Criação de vídeos 1080×1920 com legendas (MoviePy + FFmpeg)
- ✅ Upload automático para TikTok via cookies (sem API oficial)
- ✅ Dashboard web com painel de controle completo
- ✅ Orquestração via n8n + cron scheduler
- ✅ Banco de dados SQLite para métricas e histórico

### 2. 🔄 Workflow n8n (`tiktok-humor-noticias-workflow.json`)

Template n8n para geração de roteiros de humor diários — ideal para quem já usa n8n:

- ✅ Busca de notícias via RSS (G1, BBC Brasil)
- ✅ Geração de roteiros com templates pré-definidos
- ✅ Postagem automática no TikTok via OAuth2
- ✅ Notificações via Slack ou Email

---

## 🗂️ Estrutura do Repositório

```
tiktok-automation/                          ← Raiz do repositório
├── README.md                               ← Este arquivo
├── GUIA_VIDEOS.md                          ← Guia de criação de vídeos
├── config.example.json                     ← Configuração de exemplo
├── tiktok-humor-noticias-workflow.json     ← Workflow n8n standalone
│
└── tiktok-automation/                      ← Sistema Python completo
    ├── README.md                           ← Documentação completa
    ├── INICIO_RAPIDO.md                    ← Guia de início rápido (10 min)
    ├── docker-compose.yml                  ← Orquestração Docker
    ├── requirements.txt                    ← Dependências Python
    ├── .env.example                        ← Template de variáveis de ambiente
    ├── src/                                ← Código-fonte Python
    │   ├── main.py                         ← API FastAPI
    │   ├── config.py                       ← Configurações
    │   └── modules/                        ← Módulos de automação
    ├── docker/                             ← Arquivos Docker
    ├── scripts/                            ← Scripts de inicialização
    ├── workflows/n8n/                      ← Workflows n8n integrados
    └── docs/                               ← Documentação adicional
```

---

## 🚀 Início Rápido

### Sistema Python Completo (Recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/mgabrielramos/tiktok-automation.git
cd tiktok-automation/tiktok-automation

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env e adicione: OPENROUTER_API_KEY=sk_or_...

# 3. Inicie os serviços
./scripts/start.sh        # Linux/Mac
scripts\start.bat         # Windows

# 4. Acesse os serviços
# API:       http://localhost:8000
# Dashboard: http://localhost:8000/dashboard
# n8n:       http://localhost:5678
# Swagger:   http://localhost:8000/docs
```

Veja o [Guia de Início Rápido](tiktok-automation/INICIO_RAPIDO.md) para instruções completas.

### Workflow n8n Standalone

Para usar apenas o workflow n8n sem o sistema Python completo:

1. Importe `tiktok-humor-noticias-workflow.json` no seu n8n
2. Configure as credenciais OAuth2 do TikTok
3. Ative o workflow

Veja a seção [Workflow n8n](#-workflow-n8n-standalone-1) abaixo para o guia completo.

---

## 💰 Custos

| Serviço | Plano | Custo |
|---------|-------|-------|
| OpenRouter (IA) | Free tier | R$ 0,00 |
| Edge TTS | Gratuito | R$ 0,00 |
| TikTok | Gratuito | R$ 0,00 |
| n8n | Self-hosted | R$ 0,00 |
| Docker | Open source | R$ 0,00 |
| **Total** | | **R$ 0,00/mês** |

---

## 📖 Documentação

| Arquivo | Descrição |
|---------|-----------|
| [tiktok-automation/README.md](tiktok-automation/README.md) | Documentação completa do sistema Python |
| [tiktok-automation/INICIO_RAPIDO.md](tiktok-automation/INICIO_RAPIDO.md) | Guia de início rápido (10 minutos) |
| [GUIA_VIDEOS.md](GUIA_VIDEOS.md) | Opções para criação de vídeos |
| [tiktok-automation/docs/DASHBOARD.md](tiktok-automation/docs/DASHBOARD.md) | Guia do Dashboard web |
| [tiktok-automation/docs/TEMPLATES.md](tiktok-automation/docs/TEMPLATES.md) | Customização de templates de humor |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Como contribuir com o projeto |

---

## 🔄 Workflow n8n Standalone

### 1. Importar o Workflow no n8n

1. Abra seu n8n (Docker)
2. Vá em **Workflows** → **Add Workflow**
3. Clique nos **três pontos** no canto superior direito
4. Selecione **Import from File**
5. Escolha o arquivo `tiktok-humor-noticias-workflow.json`

### 2. Instalar Nó do TikTok (Opcional)

Se quiser usar o nó da comunidade ao invés de HTTP Request direto:

```bash
# Acesse o container Docker do n8n
docker exec -it <nome-container-n8n> bash

# Instale o nó da comunidade
npm install @igabm/n8n-nodes-tiktok

# Reinicie o container
docker restart <nome-container-n8n>
```

**Requisito:** n8n versão 1.107.0 ou superior.

---

## 🔐 Configurar TikTok API

### Passo 1: Criar App no TikTok Developer

1. Acesse [TikTok for Developers](https://developers.tiktok.com/)
2. Faça login com sua conta TikTok
3. Vá em **My Apps** → **Create App**
4. Preencha:
   - **App Name:** Ex: "Auto Post TikTok"
   - **Description:** "Automação de postagens de humor"
   - **Website:** Pode ser um URL genérico
   - **Redirect URI:** `https://<seu-n8n-domain>.com/rest/oauth2-credential/callback`

### Passo 2: Adicionar Content Posting API

1. No dashboard do app, clique em **Add Product**
2. Selecione **Content Posting API**
3. Preencha o formulário explicando o uso

### Passo 3: Configurar OAuth2 no n8n

1. No n8n, vá em **Credentials** → **Add Credential**
2. Busque por **TikTok OAuth2 API**
3. Preencha:
   - **Client ID:** Do dashboard do TikTok
   - **Client Secret:** Do dashboard do TikTok
   - **OAuth Scope:** 
     - `video.upload`
     - `video.publish`
     - `user.info.basic`
4. Clique em **Connect** e autorize

### Passo 4: Submeter para Aprovação

⚠️ **Importante:** O app precisa ser aprovado para posts públicos.

1. Vá em **App Review** no dashboard
2. Preencha:
   - Vídeo demonstrativo do app em uso
   - Descrição detalhada do fluxo
   - URLs de redirecionamento
3. Aguarde aprovação (2 dias a 2 semanas)

---

## ⚙️ Configurar Fontes de Notícias

### RSS Incluídos (Padrão)

- G1 Últimas Notícias: `https://rss.globo.com/rss/feeds/ultimas-noticias.xml`
- BBC Brasil: `https://feeds.bbci.co.uk/portuguese/rss.xml`

### Adicionar Mais Fontes

Edite o workflow e adicione nós HTTP Request:

```
URLs sugeridas:
- UOL: https://noticias.uol.com.br/rss/ultimas-noticias.xml
- R7: https://feeds.r7.com/r7/ultimas-noticias/feed/
- CNN Brasil: https://www.cnnbrasil.com.br/feed/
```

---

## 📝 Personalizar Templates de Humor

Edite o nó **Gerar Roteiro Humor** (Code node) para adicionar seus próprios templates:

```javascript
const templates = [
  {
    nome: "Seu Template Personalizado",
    roteiro: `🎭 SEU TÍTULO AQUI! 

${noticia.titulo}

SEU TEXTO DE HUMOR AQUI! 😂

#suas #hashtags #aqui`
  },
  // Adicione mais templates...
];
```

---

## 🎥 Criando os Vídeos

### Opção 1: Gravação Manual (Recomendado)

1. O workflow salva o roteiro em `/app/videos/`
2. Grave você mesmo lendo o roteiro
3. Faça upload pelo app do TikTok ou use a API

### Opção 2: IA de Vídeo (Pago)

Integre com estas APIs no workflow:

| Serviço | Custo | Qualidade |
|---------|-------|-----------|
| **Sora (OpenAI)** | Pago | Alta |
| **Runway ML** | $12-95/mês | Alta |
| **Pika Labs** | Gratuito limitado | Média |
| **HeyGen** | $29+/mês | Alta (avatar) |

### Opção 3: Slideshow Automático

Use o **Canva API** ou **FFmpeg** para criar slideshow com:
- Imagem de fundo da notícia
- Texto do roteiro sobreposto
- Narração TTS

---

## 🔊 Narração com TTS Gratuito

### Edge TTS (Microsoft - Gratuito)

```bash
# No seu servidor/container
pip install edge-tts

# Gerar áudio
edge-tts --text "Seu roteiro aqui" --write-media narracao.mp3
```

### gTTS (Google - Gratuito)

```bash
pip install gTTS
gtts-cli "Seu roteiro aqui" -o narracao.mp3
```

---

## 📅 Agendamento

O trigger está configurado para **rodar a cada 24 horas**.

Para mudar o horário:

1. Edite o nó **Trigger Diário**
2. Ajuste o campo `hours` para o horário desejado
3. Ex: Para rodar às 8h da manhã, configure o cron appropriately

---

## 🔔 Notificações

### Slack

1. Crie um webhook em [Slack Apps](https://api.slack.com/apps)
2. No workflow, edite o nó **Notificar (Slack/Email)**
3. Substitua `https://hook.slack.com/services/SEU/WEBHOOK/AQUI` pelo seu webhook

### Email

Substitua o nó de Slack por:
- **SendGrid** (grátis 100 emails/dia)
- **Gmail** (requer OAuth2)
- **SMTP** direto

---

## ⚠️ Limitações e Considerações

### TikTok API

| Limite | Valor |
|--------|-------|
| Posts por dia | 25 |
| Requisições por minuto | 6 |
| Tamanho máximo vídeo | 10 minutos |
| Resolução recomendada | 1080x1920 (9:16) |

### Aprovação do App

- ⏱️ Tempo: 2 dias a 2 semanas
- 📹 Posts ficam **privados** até aprovação
- ✅ Após aprovação: posts públicos automaticamente

### Conteúdo de Humor

- Verifique se a notícia é apropriada para sátira
- Evite temas sensíveis (tragédias, política polarizada)
- Mantenha o tom leve e divertido

---

## 🐛 Solução de Problemas

### "OAuth2 token expired"

1. Vá em **Credentials** no n8n
2. Edite a credencial do TikTok
3. Clique em **Reconnect**

### "App not approved for public posts"

- Seus posts estão indo como **privados**
- Submeta o app para revisão no TikTok Developer
- Aguarde aprovação

### "RSS feed empty"

- Verifique se a URL do RSS está ativa
- Adicione múltiplas fontes como backup

### "Vídeo rejeitado pelo TikTok"

- Verifique formato: MP4, codec H.264
- Resolução: 1080x1920 mínimo
- Duração: 3-60 segundos ideal

---

## 📁 Estrutura de Arquivos

```
32d/
├── tiktok-humor-noticias-workflow.json    # Workflow n8n
├── README.md                               # Esta documentação
└── videos/                                 # (Opcional) Pasta para vídeos
    ├── roteiro_2026-02-22.txt
    └── tiktok_2026-02-22_123.mp4
```

---

## 🎯 Próximos Passos Sugeridos

### Para o Workflow n8n

1. **Teste o workflow** manualmente primeiro
2. **Configure a API do TikTok** e aguarde aprovação
3. **Personalize os templates** de humor com sua voz
4. **Adicione mais fontes** de notícias
5. **Migre para o Sistema Python Completo** para ter geração de vídeo automatizada

### Para o Sistema Python Completo

1. Configure `.env` com `OPENROUTER_API_KEY`
2. Execute `docker-compose up -d` e acesse o Dashboard
3. Personalize os templates em `src/config.py`
4. Configure o TikTok SessionID para upload automático

---

## 💡 Dicas de Conteúdo Viral

- 📈 Use trending hashtags do dia
- ⏰ Poste em horários de pico (18h-21h)
- 🎵 Use músicas trending do TikTok
- 📱 Legendas curtas e impactantes
- 🔄 Interaja nos comentários nas primeiras horas

---

## 📞 Suporte e Links Úteis

- 📖 [Documentação n8n](https://docs.n8n.io/)
- 🎵 [TikTok API Docs](https://developers.tiktok.com/)
- 💬 [Comunidade n8n](https://community.n8n.io/)
- 🤖 [OpenRouter (IA gratuita)](https://openrouter.ai/)
- 🐛 [Issues / Sugestões](https://github.com/mgabrielramos/tiktok-automation/issues)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Leia o [CONTRIBUTING.md](CONTRIBUTING.md) para saber como.

---

**Feito com ❤️ para criadores de conteúdo brasileiros 🎭**
