"""
TikTok Automation - API Principal

API FastAPI que integra todos os módulos para automação completa
do TikTok com geração de conteúdo por IA gratuita.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger
import asyncio
import os
import sys

# Adiciona src ao path
sys.path.insert(0, str(os.path.dirname(os.path.dirname(__file__))))

from src.config import settings
from src.modules.ia_generator import IAGenerator
from src.modules.tts_module import TTSModule
from src.modules.video_creator import VideoCreator
from src.modules.tiktok_uploader_module import TikTokUploaderModule
from src.modules.news_fetcher import NewsFetcher
from src.routes.dashboard import router as dashboard_router

# =============================================================================
# CONFIGURAÇÃO DA APLICAÇÃO
# =============================================================================

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Automação completa para TikTok com IA gratuita e Dashboard",
)

# Incluir rotas do dashboard
app.include_router(dashboard_router, prefix="/dashboard")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configura loguru
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level,
)
logger.add(
    str(settings.logs_dir / "app_{time:YYYY-MM-DD}.log"),
    rotation="00:00",
    retention="7 days",
    level=settings.log_level,
)

# =============================================================================
# INSTÂNCIAS DOS MÓDULOS
# =============================================================================

ia_generator = IAGenerator()
tts_module = TTSModule()
video_creator = VideoCreator()
tiktok_uploader = TikTokUploaderModule()
news_fetcher = NewsFetcher()

# =============================================================================
# MODELOS PYDANTIC
# =============================================================================


class NoticiaInput(BaseModel):
    """Input para geração de roteiro"""

    titulo: str
    descricao: str
    link: Optional[str] = ""


class RoteiroRequest(BaseModel):
    """Request para gerar roteiro"""

    noticia: NoticiaInput
    template: Optional[str] = None
    modelo_ia: Optional[str] = None


class VideoRequest(BaseModel):
    """Request para criar vídeo"""

    roteiro: Dict[str, str]
    audio_path: Optional[str] = None
    usar_template_fundo: bool = True
    cor_fundo: Optional[List[int]] = None


class UploadRequest(BaseModel):
    """Request para upload"""

    video_path: str
    titulo: str
    agendar_para: Optional[str] = None  # ISO format


class GeracaoCompletaRequest(BaseModel):
    """Request para geração completa (notícia -> vídeo)"""

    noticia: Optional[NoticiaInput] = None
    buscar_aleatoria: bool = False
    gerar_audio: bool = True
    gerar_video: bool = True
    fazer_upload: bool = False
    voz_tts: Optional[str] = None


# =============================================================================
# ENDPOINTS
# =============================================================================


@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "nome": settings.app_name,
        "versao": settings.version,
        "status": "online",
        "dashboard": "/dashboard",
        "documentacao": "/docs",
    }


@app.get("/dashboard", include_in_schema=False)
async def dashboard_root():
    """Redireciona para o dashboard HTML"""
    from fastapi.responses import FileResponse
    return FileResponse("src/web/dashboard.html")


@app.get("/health")
async def health_check():
    """Health check para Docker"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/status")
async def get_status():
    """Status completo do sistema"""
    return {
        "app": {
            "nome": settings.app_name,
            "versao": settings.version,
            "status": "online",
        },
        "modulos": {
            "ia_generator": "configurado" if ia_generator.api_key else "sem API key",
            "tts_module": "configurado",
            "video_creator": "configurado",
            "tiktok_uploader": "configurado" if tiktok_uploader.sessionid else "sem sessionid",
            "news_fetcher": f"{len(news_fetcher.sources)} fontes",
        },
        "configuracoes": {
            "openrouter_configurado": bool(settings.openrouter_api_key),
            "tiktok_configurado": bool(settings.tiktok_sessionid),
            "modelo_padrao": settings.default_model,
            "voz_padrao": settings.default_tts_voice,
        },
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/api/generate-roteiro")
async def generate_roteiro(request: RoteiroRequest):
    """
    Gera roteiro de humor baseado em notícia

    Args:
        request: Dados da notícia e opções

    Returns:
        Roteiro gerado pela IA
    """
    logger.info(f"Gerando roteiro para: {request.noticia.titulo[:50]}...")

    resultado = await ia_generator.gerar_roteiro(
        noticia_titulo=request.noticia.titulo,
        noticia_descricao=request.noticia.descricao,
        noticia_link=request.noticia.link or "",
        template=request.template,
        modelo=request.modelo_ia,
    )

    if not resultado["sucesso"]:
        raise HTTPException(status_code=500, detail=resultado.get("erro", "Erro ao gerar roteiro"))

    return resultado


@app.post("/api/generate-tts")
async def generate_tts(texto: str, voz: Optional[str] = None):
    """
    Gera áudio a partir de texto

    Args:
        texto: Texto para converter
        voz: Voz do TTS (opcional)

    Returns:
        Informações do áudio gerado
    """
    logger.info(f"Gerando TTS ({len(texto)} chars)")

    resultado = await tts_module.gerar_audio(
        texto=texto,
        voz=voz,
    )

    if not resultado["sucesso"]:
        raise HTTPException(status_code=500, detail=resultado.get("erro", "Erro ao gerar áudio"))

    return resultado


@app.post("/api/create-video")
async def create_video(request: VideoRequest):
    """
    Cria vídeo para TikTok

    Args:
        request: Dados do vídeo

    Returns:
        Informações do vídeo criado
    """
    logger.info("Criando vídeo...")

    # Determina fundo
    imagem_fundo = None
    cor_fundo = tuple(request.cor_fundo) if request.cor_fundo else None

    if request.usar_template_fundo:
        template_path = settings.templates_dir / "fundo_padrao.png"
        if template_path.exists():
            imagem_fundo = str(template_path)

    # Precisa de áudio
    if not request.audio_path:
        raise HTTPException(status_code=400, detail="audio_path é obrigatório")

    resultado = await video_creator.criar_video_com_legendas(
        audio_path=request.audio_path,
        roteiro=request.roteiro,
        imagem_fundo=imagem_fundo,
        cor_fundo=cor_fundo,
        tema=request.roteiro.get("noticia", "")[:100],  # Usa parte da notícia como tema
    )

    if not resultado["sucesso"]:
        raise HTTPException(status_code=500, detail=resultado.get("erro", "Erro ao criar vídeo"))

    return resultado


@app.post("/api/upload-video")
async def upload_video(request: UploadRequest):
    """
    Faz upload de vídeo para TikTok

    Args:
        request: Dados do upload

    Returns:
        Resultado do upload
    """
    logger.info(f"Fazendo upload: {request.video_path}")

    agendar_para = None
    if request.agendar_para:
        agendar_para = datetime.fromisoformat(request.agendar_para)

    resultado = await tiktok_uploader.upload_video(
        video_path=request.video_path,
        titulo=request.titulo,
        agendar_para=agendar_para,
    )

    if not resultado["sucesso"]:
        raise HTTPException(status_code=500, detail=resultado.get("erro", "Erro no upload"))

    return resultado


@app.post("/api/generate-daily")
async def generate_daily(background_tasks: BackgroundTasks):
    """
    Gera conteúdo diário automaticamente

    Fluxo completo:
    1. Busca notícia aleatória
    2. Gera roteiro com IA
    3. Gera áudio TTS
    4. Cria vídeo
    5. (Opcional) Faz upload

    Args:
        background_tasks: Para processamento em background

    Returns:
        Status da geração
    """
    logger.info("=== INICIANDO GERAÇÃO DIÁRIA ===")

    try:
        # 1. Busca notícia
        logger.info("Passo 1: Buscando notícia...")
        noticia = await news_fetcher.buscar_noticia_aleatoria()

        if not noticia:
            return {
                "sucesso": False,
                "erro": "Nenhuma notícia encontrada",
            }

        logger.info(f"Notícia selecionada: {noticia['titulo'][:50]}...")

        # 2. Gera roteiro
        logger.info("Passo 2: Gerando roteiro com IA...")
        roteiro_result = await ia_generator.gerar_roteiro(
            noticia_titulo=noticia["titulo"],
            noticia_descricao=noticia["descricao"],
            noticia_link=noticia["link"],
        )

        if not roteiro_result["sucesso"]:
            return {
                "sucesso": False,
                "erro": "Falha ao gerar roteiro",
                "detalhe": roteiro_result.get("erro"),
            }

        roteiro = roteiro_result["roteiro_formatado"]
        roteiro_completo = roteiro_result["roteiro_completo"]

        # 3. Gera áudio
        logger.info("Passo 3: Gerando áudio TTS...")
        audio_result = await tts_module.gerar_audio_roteiro_completo(
            roteiro=roteiro,
        )

        if not audio_result["sucesso"]:
            return {
                "sucesso": False,
                "erro": "Falha ao gerar áudio",
                "detalhe": audio_result.get("erro"),
            }

        # 4. Cria vídeo
        logger.info("Passo 4: Criando vídeo...")

        # Gera template se não existir
        template_path = settings.templates_dir / "fundo_padrao.png"
        if not template_path.exists():
            await video_creator.gerar_template_padrao()

        video_result = await video_creator.criar_video_com_legendas(
            audio_path=audio_result["caminho_arquivo"],
            roteiro=roteiro,
            imagem_fundo=str(template_path),
            tema=noticia.get("titulo", "")[:100],  # Usa título da notícia como tema
        )

        if not video_result["sucesso"]:
            return {
                "sucesso": False,
                "erro": "Falha ao criar vídeo",
                "detalhe": video_result.get("erro"),
            }

        logger.success("=== GERAÇÃO DIÁRIA CONCLUÍDA ===")

        return {
            "sucesso": True,
            "mensagem": "Conteúdo diário gerado com sucesso!",
            "noticia": {
                "titulo": noticia["titulo"],
                "fonte": noticia["fonte"],
            },
            "roteiro": roteiro_completo[:200] + "...",
            "audio": audio_result["caminho_arquivo"],
            "video": video_result["caminho_arquivo"],
            "duracao": video_result.get("duracao_segundos", 0),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Erro na geração diária: {e}")
        return {
            "sucesso": False,
            "erro": str(e),
        }


@app.post("/api/upload-pending")
async def upload_pending():
    """
    Faz upload de vídeos pendentes

    Procura vídeos na pasta output e faz upload

    Returns:
        Resultado do upload
    """
    logger.info("Verificando vídeos pendentes para upload...")

    # Procura vídeos na pasta de output
    videos_dir = settings.videos_dir
    videos = list(videos_dir.glob("video_*.mp4"))

    if not videos:
        return {
            "mensagem": "Nenhum vídeo pendente encontrado",
            "videos_encontrados": 0,
        }

    resultados = []

    for video_path in videos[:1]:  # Upload de 1 vídeo por vez
        # Extrai título do nome do arquivo ou usa padrão
        titulo = f"Vídeo gerado automaticamente #humor #noticias"

        resultado = await tiktok_uploader.upload_video(
            video_path=str(video_path),
            titulo=titulo,
        )

        resultados.append({
            "video": str(video_path),
            "resultado": resultado,
        })

    return {
        "videos_processados": len(resultados),
        "resultados": resultados,
    }


@app.get("/api/news")
async def get_news(limite: int = 10):
    """
    Busca notícias atuais

    Args:
        limite: Número máximo de notícias

    Returns:
        Lista de notícias
    """
    noticias = await news_fetcher.buscar_todas_noticias()
    return {"noticias": noticias[:limite]}


@app.get("/api/voices")
async def get_voices():
    """Lista vozes TTS disponíveis"""
    vozes = await tts_module.listar_vozes()
    return {"vozes": vozes}


@app.get("/api/test-ia")
async def test_ia():
    """Testa conexão com OpenRouter"""
    resultado = await ia_generator.testar_modelos_gratuitos()
    return {"teste": resultado}


@app.get("/api/templates")
async def get_templates():
    """Lista templates de humor disponíveis"""
    return {"templates": settings.humor_templates}


# =============================================================================
# INICIALIZAÇÃO
# =============================================================================


@app.on_event("startup")
async def startup_event():
    """Executa na inicialização"""
    logger.info(f"Iniciando {settings.app_name} v{settings.version}")
    logger.info(f"Timezone: {settings.timezone}")

    # Cria diretórios
    settings.create_directories()

    # Gera template padrão
    try:
        template_path = settings.templates_dir / "fundo_padrao.png"
        if not template_path.exists():
            logger.info("Gerando template padrão...")
            await video_creator.gerar_template_padrao()
    except Exception as e:
        logger.warning(f"Não foi possível gerar template: {e}")

    logger.info("Inicialização concluída!")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
