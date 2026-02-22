# 🎥 Guia de Criação de Vídeo para TikTok

Como transformar os roteiros gerados em vídeos prontos para postar.

---

## 📊 Comparativo de Opções

| Método | Custo | Qualidade | Esforço | Automatização |
|--------|-------|-----------|---------|---------------|
| Gravação Manual | Grátis | Alta | Médio | Baixa |
| TTS + Slideshow | Grátis | Média | Baixo | Alta |
| Avatar IA | $29+/mês | Alta | Baixo | Alta |
| Vídeo Generativo | $10-100/mês | Variável | Baixo | Alta |

---

## 🎬 Opção 1: Gravação Manual (Recomendado para Começar)

### Vantagens
- ✅ Totalmente gratuito
- ✅ Autêntico e pessoal
- ✅ Sem dependência de APIs
- ✅ Melhor engajamento (rostos reais performam melhor)

### Fluxo no Workflow

O workflow já salva o roteiro em arquivo TXT. Para gravar:

1. **Receba a notificação** (Slack/Email)
2. **Abra o roteiro** salvo em `/app/videos/`
3. **Grave com o celular** em pé (formato 9:16)
4. **Edite no CapCut** (gratuito) se quiser
5. **Poste no TikTok**

### Dicas de Gravação

```
📱 Configurações:
- Resolução: 1080x1920
- FPS: 30 ou 60
- Formato: MP4 ou MOV
- Duração: 15-60 segundos

💡 Iluminação:
- Luz natural de frente
- Ring light se tiver
- Evite contra-luz

🎤 Áudio:
- Ambiente silencioso
- Use fone com microfone
- Ou microfone externo
```

---

## 🔊 Opção 2: TTS + Slideshow (100% Gratuito)

### Edge TTS (Microsoft)

**Instalação:**
```bash
pip install edge-tts
```

**Comando básico:**
```bash
edge-tts --text "Seu roteiro aqui" --write-media narracao.mp3
```

**Vozes em Português:**
```bash
# Listar vozes disponíveis
edge-tts --list-voices | findstr pt-BR

# Vozes recomendadas:
pt-BR-FranciscaNeural  # Feminina
pt-BR-AntonioNeural    # Masculina
pt-BR-BrendaNeural     # Feminina emocional
```

### Criar Slideshow com FFmpeg

**Instalar FFmpeg:**
```bash
# Windows (Chocolatey)
choco install ffmpeg

# Linux
apt-get install ffmpeg

# Docker (adicionar ao container n8n)
apk add --no-cache ffmpeg
```

**Script de automação (bash):**
```bash
#!/bin/bash

# Inputs
ROTEIRO="$1"
IMAGEM_FUNDO="$2"
SAIDA="$3"

# Gerar narração
edge-tts --text "$ROTEIRO" --write-media temp_audio.mp3

# Criar vídeo com imagem estática + áudio
ffmpeg -loop 1 -i "$IMAGEM_FUNDO" -i temp_audio.mp3 \
  -c:v libx264 -tune stillimage -c:a aac \
  -b:a 192k -pix_fmt yuv420p -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  -shortest -y "$SAIDA"

# Limpar
rm temp_audio.mp3

echo "Vídeo criado: $SAIDA"
```

### Adicionar Legendas Automáticas

**Usando Aegisub (gratuito):**
1. Importe o áudio
2. Gere legendas automáticas
3. Exporte como .ass
4. Queime no vídeo com FFmpeg

**Ou use o CapCut** que gera legendas automáticas grátis.

---

## 🤖 Opção 3: Avatar com IA (Pago)

### HeyGen

**Preços:**
- Starter: $29/mês (15 créditos)
- Creator: $89/mês (50 créditos)

**Integração com n8n:**
```json
{
  "method": "POST",
  "url": "https://api.heygen.com/v1/video.generate",
  "headers": {
    "X-API-Key": "SUA_API_KEY"
  },
  "body": {
    "video_inputs": [
      {
        "character": {
          "character_id": "SEU_AVATAR_ID"
        },
        "voice": {
          "voice_id": "SEU_VOICE_ID"
        },
        "text": "Seu roteiro aqui"
      }
    ]
  }
}
```

**Workflow:**
1. Gerar roteiro no n8n
2. Enviar para HeyGen API
3. Aguardar processamento (webhook)
4. Baixar vídeo gerado
5. Postar no TikTok

### D-ID

**Preços:**
- Lite: $5.99/mês (15 créditos)
- Starter: $29/mês

**API similar ao HeyGen**, com avatares falantes.

---

## 🎨 Opção 4: Vídeo Generativo

### Runway ML

**Preços:**
- Standard: $12/mês
- Pro: $28/mês

**Recursos:**
- Gen-2: Texto para vídeo
- Treine modelos personalizados
- Edição com IA

**Limitações:**
- Vídeos curtos (4 segundos por geração)
- Precisa concatenar múltiplos clips

### Pika Labs

**Preços:**
- Gratuito com marca d'água
- Pro: $8/mês

**Acesso:**
- Via Discord ou API
- Comandos: `/create`, `/animate`

### Luma Dream Machine

**Preços:**
- Gratuito: 30 vídeos/mês
- Unlimited: $30/mês

**Qualidade:** Alta, bom para cenas cinematográficas

---

## 🔧 Opção 5: Canva API (Semi-automático)

### Fluxo

1. **Crie um template** no Canva (formato TikTok 1080x1920)
2. **Use a API do Canva** para:
   - Substituir texto pelo roteiro
   - Trocar imagens
3. **Exporte como vídeo**
4. **Poste no TikTok**

### Código de Exemplo

```javascript
// Nó Code no n8n
const canvaApiKey = 'SUA_API_KEY';
const templateId = 'SEU_TEMPLATE_ID';

const response = await fetch('https://api.canva.com/v1/designs', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${canvaApiKey}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    template_id: templateId,
    elements: [
      {
        id: 'texto_principal',
        text: $input.item.json.roteiro
      }
    ]
  })
});

const data = await response.json();
return { json: { video_url: data.export_url } };
```

---

## 🎞️ Opção 6: Renderização com After Effects (Profissional)

### Usando After Effects + Dataclay Templater

**Fluxo:**
1. Crie template .aep
2. Alimente com JSON do roteiro
3. Renderize em lote
4. Exporte MP4

**Custo:**
- After Effects: R$119/mês
- Templater: $395 (único) ou $20/mês

---

## 📦 Workflow Completo Automatizado (Exemplo)

Aqui está um exemplo de workflow **totalmente automatizado** usando TTS + FFmpeg:

```
Trigger Diário
    ↓
Buscar Notícias RSS
    ↓
Gerar Roteiro Humor
    ↓
Edge TTS (gerar áudio)
    ↓
FFmpeg (criar vídeo com imagem + áudio + legendas)
    ↓
Upload TikTok API
    ↓
Notificar Conclusão
```

### Nó para Edge TTS (HTTP Request ou Execute Command)

```javascript
// Code node para preparar comando
const roteiro = $input.item.json.roteiro.replace(/[\n"]/g, ' ');
const arquivoSaida = `/app/videos/audio_${Date.now()}.mp3`;

return {
  json: {
    comando: `edge-tts --text "${roteiro}" --voice pt-BR-FranciscaNeural --write-media "${arquivoSaida}"`,
    arquivoAudio: arquivoSaida
  }
};
```

### Nó Execute Command (Docker)

```yaml
# docker-compose.yml do n8n
services:
  n8n:
    image: n8nio/n8n
    environment:
      - N8N_STARTUP_ACTIVE_EXECUTIONS=100
    volumes:
      - ./videos:/app/videos
    command: >
      sh -c "
        apk add --no-cache python3 py3-pip &&
        pip3 install edge-tts &&
        /docker-entrypoint.sh
      "
```

---

## 🎯 Minha Recomendação

### Para Começar (Gratuito)

1. **Use o workflow** para gerar roteiros
2. **Grave você mesmo** com o celular
3. **Edite no CapCut** (grátis, já tem legendas automáticas)
4. **Poste manualmente** até ter aprovação da API

### Para Escalar (Investimento Baixo)

1. **Edge TTS** para narração (grátis)
2. **Canva Pro** para templates (R$35/mês)
3. **FFmpeg** para renderizar
4. **API do TikTok** para postar automático

### Para Produção (Investimento Médio)

1. **HeyGen** ou **D-ID** para avatares ($29-89/mês)
2. **Runway ML** para vídeos generativos ($12-28/mês)
3. **n8n Cloud** para mais execuções ($20-50/mês)

---

## 📋 Checklist de Publicação

Antes de postar, verifique:

- [ ] Vídeo em formato 9:16 (1080x1920)
- [ ] Duração entre 15-60 segundos
- [ ] Áudio claro e sem ruídos
- [ ] Legendas legíveis
- [ ] Hashtags relevantes (3-5)
- [ ] Hook nos primeiros 3 segundos
- [ ] Call-to-action no final

---

## 🔗 Links Úteis

- **Edge TTS:** https://github.com/rany2/edge-tts
- **FFmpeg:** https://ffmpeg.org/
- **CapCut:** https://www.capcut.com/
- **Canva:** https://www.canva.com/
- **HeyGen:** https://www.heygen.com/
- **Runway:** https://runwayml.com/
- **Pika:** https://pika.art/
- **Luma:** https://lumalabs.ai/dream-machine

---

**Dica final:** Comece simples, valide o conteúdo, depois automatize mais! 🚀
