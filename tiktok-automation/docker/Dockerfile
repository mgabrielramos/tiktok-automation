# =============================================================================
# DOCKERFILE - TIKTOK AUTOMATION
# =============================================================================
# Imagem base Python com todas as dependências para automação de vídeo
# =============================================================================

FROM python:3.11-slim-bookworm

# Metadados
LABEL maintainer="TikTok Automation Project"
LABEL description="Automação completa para TikTok com IA gratuita"
LABEL version="1.0.0"

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive \
    NODE_VERSION=20 \
    FFMPEG_VERSION=6.1

# =============================================================================
# INSTALAÇÃO DE DEPENDÊNCIAS DO SISTEMA
# =============================================================================

RUN apt-get update && apt-get install -y --no-install-recommends \
    # FFmpeg e codecs de vídeo
    ffmpeg \
    # Ferramentas de build
    build-essential \
    git \
    curl \
    wget \
    # Node.js para scripts JavaScript
    gnupg \
    ca-certificates \
    # Utilitários
    tzdata \
    locales \
    # Fontes para renderização de texto (UTF-8)
    fonts-liberation \
    fonts-dejavu-core \
    fonts-freefont-ttf \
    # Limpeza
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# CONFIGURAÇÃO DE LOCALE E TIMEZONE
# =============================================================================

RUN sed -i 's/# pt_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen pt_BR.UTF-8 && \
    update-locale LANG=pt_BR.UTF-8

ENV LANG=pt_BR.UTF-8 \
    LANGUAGE=pt_BR:pt \
    LC_ALL=pt_BR.UTF-8 \
    TZ=America/Sao_Paulo

RUN ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime && \
    echo "${TZ}" > /etc/timezone

# =============================================================================
# INSTALAÇÃO DO NODE.JS
# =============================================================================

RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g npm@latest && \
    node --version && \
    npm --version

# =============================================================================
# CRIAÇÃO DO DIRETÓRIO DE TRABALHO
# =============================================================================

WORKDIR /app

# =============================================================================
# INSTALAÇÃO DE DEPENDÊNCIAS PYTHON
# =============================================================================

# Copia requirements primeiro para cache do Docker
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# =============================================================================
# INSTALAÇÃO DO TIKTOK-UPLOADER
# =============================================================================

RUN pip install tiktok-uploader && \
    playwright install chromium

# =============================================================================
# CONFIGURAÇÃO DE USUÁRIO NÃO-ROOT (SEGURANÇA)
# =============================================================================

RUN groupadd -r tiktok && useradd -r -g tiktok tiktok && \
    chown -R tiktok:tiktok /app

USER tiktok

# =============================================================================
# HEALTH CHECK
# =============================================================================

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# =============================================================================
# EXPOSIÇÃO DE PORTA
# =============================================================================

EXPOSE 8000

# =============================================================================
# COMANDO PADRÃO
# =============================================================================

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
