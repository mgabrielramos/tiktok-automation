#!/bin/bash
# =============================================================================
# SCRIPT DE INICIALIZAÇÃO - TIKTOK AUTOMATION
# =============================================================================
# Este script inicia todos os serviços Docker necessários
# =============================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     TIKTOK AUTOMATION - Script de Inicialização       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verifica se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker não encontrado! Instale o Docker primeiro.${NC}"
    exit 1
fi

# Verifica se docker-compose está instalado
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ docker-compose não encontrado! Instale primeiro.${NC}"
    exit 1
fi

# Detecta comando docker-compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

echo -e "${YELLOW}📁 Diretório: $(pwd)${NC}"
echo -e "${YELLOW}🐳 Docker versão: $(docker --version)${NC}"
echo ""

# Verifica arquivo .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado!${NC}"
    echo -e "${YELLOW}📝 Criando a partir do .env.example...${NC}"
    
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ .env criado!${NC}"
        echo -e "${YELLOW}⚠️  EDITE O ARQUIVO .env E CONFIGURE:${NC}"
        echo -e "   - OPENROUTER_API_KEY (opcional para IA grátis)"
        echo -e "   - TIKTOK_SESSIONID (necessário para upload)"
        echo -e "   - N8N_HOST (seu domínio ou localhost)"
        echo ""
        echo -e "${YELLOW}Pressione Enter após configurar o .env...${NC}"
        read
    else
        echo -e "${RED}❌ .env.example não encontrado!${NC}"
        exit 1
    fi
fi

# Carrega variáveis do .env
set -a
source .env
set +a

echo -e "${BLUE}🔧 Verificando configurações...${NC}"

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  OPENROUTER_API_KEY não configurada (IA pode não funcionar)${NC}"
else
    echo -e "${GREEN}✅ OpenRouter API configurada${NC}"
fi

if [ -z "$TIKTOK_SESSIONID" ]; then
    echo -e "${YELLOW}⚠️  TIKTOK_SESSIONID não configurada (upload não funcionará)${NC}"
else
    echo -e "${GREEN}✅ TikTok SessionID configurado${NC}"
fi

echo ""
echo -e "${BLUE}🚀 Iniciando serviços Docker...${NC}"

# Para serviços existentes
echo -e "${YELLOW}🛑 Parando serviços existentes...${NC}"
$COMPOSE_CMD down 2>/dev/null || true

# Remove containers antigos
echo -e "${YELLOW}🧹 Limpando containers antigos...${NC}"
docker container prune -f 2>/dev/null || true

# Build e start
echo -e "${BLUE}📦 Build das imagens (pode demorar na primeira vez)...${NC}"
$COMPOSE_CMD build

echo ""
echo -e "${GREEN}🚀 Iniciando serviços...${NC}"
$COMPOSE_CMD up -d

echo ""
echo -e "${GREEN}✅ Serviços iniciados!${NC}"
echo ""

# Aguarda serviços ficarem prontos
echo -e "${BLUE}⏳ Aguardando serviços ficarem prontos...${NC}"
sleep 10

# Status dos containers
echo ""
echo -e "${BLUE}📊 Status dos containers:${NC}"
$COMPOSE_CMD ps

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              🎉 INICIALIZAÇÃO CONCLUÍDA! 🎉           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📱 Serviços disponíveis:${NC}"
echo -e "   • API de Automação: http://localhost:8000"
echo -e "   • n8n Workflow:     http://localhost:5678"
echo -e "   • Swagger Docs:     http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}📝 Próximos passos:${NC}"
echo -e "   1. Acesse http://localhost:8000/docs para ver a API"
echo -e "   2. Configure workflows no n8n (http://localhost:5678)"
echo -e "   3. Teste a geração com: curl http://localhost:8000/api/generate-daily -X POST"
echo ""
echo -e "${BLUE}📖 Para ver logs: ${NC}docker-compose logs -f"
echo -e "${BLUE}📖 Para parar:    ${NC}docker-compose down"
echo ""
