# 📊 Dashboard - Painel de Controle TikTok Automation

> Interface web completa para gerenciar toda a automação

---

## 🎯 Visão Geral

O dashboard é uma interface web moderna e profissional que permite:

- 📊 Visualizar estatísticas em tempo real
- ✨ Gerar conteúdo manualmente
- 📤 Fazer uploads para TikTok
- ⚙️ Configurar o sistema
- 📜 Ver histórico de atividades
- 📰 Triggerar geração diária

---

## 🚀 Acesso

### URL do Dashboard

```
http://localhost:8000/dashboard
```

Ou pela raiz:
```
http://localhost:8000/
```

---

## 📱 Funcionalidades

### 1. Status Bar

Mostra o status dos serviços:

| Indicador | Descrição |
|-----------|-----------|
| 🔵 API | Status da API FastAPI |
| 🔵 TikTok | Status do SessionID |
| 🔵 OpenRouter | Status da API de IA |

**Cores:**
- 🟢 Online = Funcionando
- 🔴 Offline = Problema

---

### 2. Quick Actions (Ações Rápidas)

| Ação | Ícone | Descrição |
|------|-------|-----------|
| **Gerar Conteúdo** | ✨ | Abre modal para geração manual |
| **Geração Diária** | 📰 | Triggera geração automática |
| **Upload Manual** | 📤 | Upload de vídeo existente |
| **Configurações** | ⚙️ | Ver configurações do sistema |

---

### 3. Cards de Estatísticas

| Card | Métrica | Descrição |
|------|---------|-----------|
| 📊 **Total de Gerações** | Número total + quantidade hoje |
| 📤 **Total de Uploads** | Número total + sucessos |
| 👁️ **Visualizações Totais** | Total de views + likes |
| ⏱️ **Duração Média** | Média em segundos + modelo IA |

---

### 4. Atividade Recente

Lista as últimas atividades do sistema:

- 🔄 Gerações de conteúdo
- 📤 Uploads realizados
- ⚠️ Erros ocorridos

**Cores de status:**
- 🟢 SUCCESS = Sucesso
- 🔴 ERROR = Erro
- 🟡 INFO = Informação

---

### 5. Gerações Recentes

Tabela com histórico de gerações:

| Coluna | Descrição |
|--------|-----------|
| Data | Dia da geração |
| Notícia | Título da notícia |
| Modelo IA | Modelo usado |
| Status | Sucesso ou erro |

---

### 6. Status do Sistema

Painel lateral com:

- Status dos serviços
- Última geração
- Fontes mais usadas

---

## ✨ Modal de Geração de Conteúdo

### Campos

| Campo | Tipo | Obrigatório |
|-------|------|-------------|
| Título da Notícia | Texto | ✅ |
| Descrição | Texto | ✅ |
| Link | URL | ❌ |
| Modelo de IA | Select | ❌ |
| Gerar Áudio | Checkbox | ❌ |
| Gerar Vídeo | Checkbox | ❌ |

### Modelos de IA Disponíveis

1. **Llama 3.3 70B** (Recomendado)
2. **Google Gemma 3**
3. **Mistral Small**
4. **DeepSeek R1**

### Barra de Progresso

Durante a geração, mostra:
- Progresso em porcentagem
- Status atual (Iniciando, Gerando roteiro, etc.)

---

## 📤 Modal de Upload Manual

### Campos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| Caminho do Vídeo | Texto | Path completo do arquivo |
| Título/Descrição | Texto | Descrição do vídeo |
| Agendar para | DateTime | Agendamento (opcional) |

### Exemplo de Caminho

```
/app/output/videos/video_20260222_090000.mp4
```

---

## ⚙️ Modal de Configurações

Mostra todas as configurações atuais:

- `tiktok_configurado`: Se SessionID está configurado
- `openrouter_configurado`: Se API key está configurada
- `default_model`: Modelo de IA padrão
- `default_voice`: Voz TTS padrão
- E outras configurações salvas

---

## 🔌 API Endpoints do Dashboard

### Principais

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/dashboard` | GET | Página HTML do dashboard |
| `/dashboard/data` | GET | Dados completos do dashboard |
| `/dashboard/statistics` | GET | Estatísticas gerais |
| `/dashboard/generate` | POST | Gerar conteúdo manual |
| `/dashboard/generate-daily` | POST | Triggerar geração diária |
| `/dashboard/upload` | POST | Fazer upload |
| `/dashboard/settings` | GET/POST | Configurações |
| `/dashboard/activity` | GET | Logs de atividade |

### Exemplo de Uso da API

```bash
# Obter dados do dashboard
curl http://localhost:8000/dashboard/data

# Gerar conteúdo
curl -X POST http://localhost:8000/dashboard/generate \
  -H "Content-Type: application/json" \
  -d '{
    "noticia_titulo": "Brasil lança foguete",
    "noticia_descricao": "Novo foguete espacial brasileiro",
    "modelo_ia": "meta-llama/llama-3.3-70b-instruct:free"
  }'

# Triggerar geração diária
curl -X POST http://localhost:8000/dashboard/generate-daily
```

---

## 🎨 Design e Temas

### Cores

| Variável | Cor | Uso |
|----------|-----|-----|
| `--primary` | #fe2c55 | Rosa TikTok |
| `--secondary` | #25f4ee | Ciano TikTok |
| `--dark` | #121212 | Fundo principal |
| `--darker` | #0a0a0a | Fundo escuro |
| `--success` | #00c853 | Sucesso |
| `--danger` | #ff5252 | Erro |
| `--warning` | #ffc107 | Atenção |

### Responsividade

O dashboard é responsivo:
- Desktop: Grid 2 colunas
- Mobile: Grid 1 coluna

---

## 🔄 Auto-Refresh

O dashboard atualiza automaticamente:

- **Dados do dashboard:** A cada 30 segundos
- **Status dos serviços:** Ao carregar
- **Atividade recente:** Incluído nos dados

### Refresh Manual

Clique em **🔄 Atualizar** no header.

---

## 📊 Estrutura de Dados

### Resposta do `/dashboard/data`

```json
{
  "sucesso": true,
  "dados": {
    "statistics": {
      "total_geracoes": 50,
      "total_uploads": 45,
      "uploads_sucesso": 42,
      "total_visualizacoes": 15000,
      "total_likes": 3500,
      "geracoes_hoje": 3,
      "media_duracao_videos": 32.5,
      "modelo_ia_mais_usado": "llama-3.3-70b-instruct:free",
      "fontes_mais_usadas": [
        {"fonte": "G1", "count": 20},
        {"fonte": "BBC Brasil", "count": 15}
      ],
      "ultima_geracao": {
        "timestamp": "2026-02-22T09:00:00",
        "noticia": "Brasil lança novo foguete"
      }
    },
    "recent_generations": [...],
    "recent_uploads": [...],
    "recent_logs": [...],
    "timestamp": "2026-02-22T10:00:00"
  }
}
```

---

## 🐛 Solução de Problemas

### Dashboard não carrega

**Solução:**
1. Verifique se a API está no ar: `http://localhost:8000/health`
2. Verifique os logs: `docker-compose logs tiktok-automation`

### Status mostra "Offline"

**Solução:**
1. TikTok: Verifique SessionID no `.env`
2. OpenRouter: Verifique API key no `.env`
3. API: Reinicie o container

### Geração falha

**Solução:**
1. Verifique se há notícias disponíveis
2. Verifique créditos OpenRouter
3. Veja logs de erro no dashboard

---

## 🎯 Dicas de Uso

### 1. Geração Rápida

Use **Geração Diária** para conteúdo automático baseado em notícias.

### 2. Geração Personalizada

Use **Nova Geração** para controlar manualmente o conteúdo.

### 3. Monitoramento

Deixe o dashboard aberto em segundo plano para monitorar em tempo real.

### 4. Upload em Lote

Use o modal de upload para enviar vídeos gerados anteriormente.

---

## 📱 Screenshots

### Dashboard Principal

```
┌─────────────────────────────────────────────────────────────┐
│ 🎬 TikTok Automation                    🔄  ✨ Nova Geração │
├─────────────────────────────────────────────────────────────┤
│ 🟢 API: Online  🟢 TikTok: Online  🟢 OpenRouter: Online   │
├─────────────────────────────────────────────────────────────┤
│ ✨ Gerar  📰 Diário  📤 Upload  ⚙️ Config                  │
├─────────────────────────────────────────────────────────────┤
│ 📊 50      📤 45      👁️ 15K    ⏱️ 32s                     │
│ Total     Uploads    Views     Duração                     │
├───────────────────────────┬─────────────────────────────────┤
│ 📜 Atividade Recente     │ 💻 Status do Sistema            │
│ 🔄 Geração concluída     │ 🟢 API: Online                  │
│ 📤 Upload realizado      │ 🟢 TikTok: Online               │
│ ⚠️ Erro de conexão       │ 📰 Última Geração               │
└───────────────────────────┴─────────────────────────────────┘
```

---

## 🔗 Links Úteis

| Recurso | URL |
|---------|-----|
| Dashboard | http://localhost:8000/dashboard |
| Swagger API | http://localhost:8000/docs |
| n8n | http://localhost:5678 |

---

## 🚀 Próximas Funcionalidades

- [ ] Gráficos de performance (Chart.js)
- [ ] Exportação de relatórios (PDF/CSV)
- [ ] Gestão de múltiplas contas TikTok
- [ ] Analytics de vídeos postados
- [ ] Editor de templates de humor
- [ ] Agendamento visual de postagens

---

**Dashboard profissional para automação TikTok! 🎉**
