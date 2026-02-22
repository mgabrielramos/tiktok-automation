"""
Rotas da API para Dashboard e Painel de Controle
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.requests import Request
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import asyncio

from ..modules.database import db
from ..modules.ia_generator import ia_generator
from ..modules.tts_module import tts_module
from ..modules.video_creator import video_creator
from ..modules.tiktok_uploader_module import tiktok_uploader_module
from ..modules.news_fetcher import news_fetcher
from ..config import settings

router = APIRouter()


# =============================================================================
# MODELOS PYDANTIC
# =============================================================================


class ManualGenerationRequest(BaseModel):
    """Request para geração manual"""

    noticia_titulo: str
    noticia_descricao: str
    noticia_link: Optional[str] = ""
    modelo_ia: Optional[str] = None
    gerar_audio: bool = True
    gerar_video: bool = True


class UploadManualRequest(BaseModel):
    """Request para upload manual"""

    video_path: str
    titulo: str
    agendar_para: Optional[str] = None


class SettingsUpdateRequest(BaseModel):
    """Request para atualizar configurações"""

    key: str
    value: str


# =============================================================================
# ROTAS DO DASHBOARD
# =============================================================================


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_html():
    """Página principal do dashboard"""
    return FileResponse("src/web/dashboard.html")


@router.get("/dashboard/data")
async def get_dashboard_data():
    """Dados do dashboard"""
    try:
        data = db.get_dashboard_data()
        return {"sucesso": True, "dados": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/statistics")
async def get_statistics():
    """Estatísticas gerais"""
    try:
        stats = db.get_statistics()
        return {"sucesso": True, "estatisticas": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# ROTAS DE GERAÇÃO
# =============================================================================


@router.post("/dashboard/generate")
async def manual_generate(request: ManualGenerationRequest):
    """Gera conteúdo manualmente"""
    try:
        resultado = {
            "sucesso": True,
            "etapas": [],
        }

        # 1. Gerar roteiro
        roteiro_result = await ia_generator.gerar_roteiro(
            noticia_titulo=request.noticia_titulo,
            noticia_descricao=request.noticia_descricao,
            noticia_link=request.noticia_link or "",
            modelo=request.modelo_ia,
        )

        resultado["etapas"].append({"nome": "roteiro", "resultado": roteiro_result})

        if not roteiro_result["sucesso"]:
            resultado["sucesso"] = False
            resultado["erro"] = roteiro_result.get("erro")
            return resultado

        # 2. Gerar áudio
        if request.gerar_audio:
            audio_result = await tts_module.gerar_audio_roteiro_completo(
                roteiro=roteiro_result["roteiro_formatado"],
            )
            resultado["etapas"].append({"nome": "audio", "resultado": audio_result})

            if not audio_result["sucesso"]:
                resultado["sucesso"] = False
                resultado["erro"] = audio_result.get("erro")
                return resultado

            # 3. Gerar vídeo
            if request.gerar_video:
                template_path = settings.templates_dir / "fundo_padrao.png"
                if not template_path.exists():
                    await video_creator.gerar_template_padrao()

                video_result = await video_creator.criar_video_com_legendas(
                    audio_path=audio_result["caminho_arquivo"],
                    roteiro=roteiro_result["roteiro_formatado"],
                    imagem_fundo=str(template_path),
                )
                resultado["etapas"].append({"nome": "video", "resultado": video_result})

                if not video_result["sucesso"]:
                    resultado["sucesso"] = False
                    resultado["erro"] = video_result.get("erro")
                    return resultado

        # Salvar no banco
        db.save_generation({
            "noticia_titulo": request.noticia_titulo,
            "noticia_fonte": "Manual",
            "roteiro_completo": roteiro_result.get("roteiro_completo", ""),
            "modelo_ia": request.modelo_ia or settings.default_model,
            "tokens_usados": roteiro_result.get("tokens_usados", 0),
            "audio_path": audio_result.get("caminho_arquivo", "") if request.gerar_audio else "",
            "audio_duracao": audio_result.get("duracao_segundos", 0) if request.gerar_audio else 0,
            "video_path": video_result.get("caminho_arquivo", "") if request.gerar_video else "",
            "video_duracao": video_result.get("duracao_segundos", 0) if request.gerar_video else 0,
            "status": "success" if resultado["sucesso"] else "error",
        })

        return resultado

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dashboard/generate-daily")
async def trigger_daily_generation():
    """Trigger para geração diária"""
    try:
        # Busca notícia aleatória
        noticia = await news_fetcher.buscar_noticia_aleatoria()

        if not noticia:
            return {"sucesso": False, "erro": "Nenhuma notícia encontrada"}

        # Gera roteiro
        roteiro_result = await ia_generator.gerar_roteiro(
            noticia_titulo=noticia["titulo"],
            noticia_descricao=noticia["descricao"],
            noticia_link=noticia["link"],
        )

        if not roteiro_result["sucesso"]:
            return {"sucesso": False, "erro": roteiro_result.get("erro")}

        # Gera áudio
        audio_result = await tts_module.gerar_audio_roteiro_completo(
            roteiro=roteiro_result["roteiro_formatado"],
        )

        if not audio_result["sucesso"]:
            return {"sucesso": False, "erro": audio_result.get("erro")}

        # Gera vídeo
        template_path = settings.templates_dir / "fundo_padrao.png"
        if not template_path.exists():
            await video_creator.gerar_template_padrao()

        video_result = await video_creator.criar_video_com_legendas(
            audio_path=audio_result["caminho_arquivo"],
            roteiro=roteiro_result["roteiro_formatado"],
            imagem_fundo=str(template_path),
        )

        # Salvar no banco
        db.save_generation({
            "noticia_titulo": noticia["titulo"],
            "noticia_fonte": noticia["fonte"],
            "roteiro_completo": roteiro_result.get("roteiro_completo", ""),
            "modelo_ia": settings.default_model,
            "tokens_usados": roteiro_result.get("tokens_usados", 0),
            "audio_path": audio_result["caminho_arquivo"],
            "audio_duracao": audio_result["duracao_segundos"],
            "video_path": video_result["caminho_arquivo"],
            "video_duracao": video_result.get("duracao_segundos", 0),
            "status": "success" if video_result["sucesso"] else "error",
        })

        return {
            "sucesso": True,
            "noticia": noticia,
            "video": video_result.get("caminho_arquivo"),
            "duracao": video_result.get("duracao_segundos", 0),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# ROTAS DE UPLOAD
# =============================================================================


@router.post("/dashboard/upload")
async def manual_upload(request: UploadManualRequest):
    """Faz upload manual de vídeo"""
    try:
        agendar_para = None
        if request.agendar_para:
            agendar_para = datetime.fromisoformat(request.agendar_para)

        resultado = await tiktok_uploader_module.upload_video(
            video_path=request.video_path,
            titulo=request.titulo,
            agendar_para=agendar_para,
        )

        # Salvar no banco
        db.save_upload({
            "video_path": request.video_path,
            "video_titulo": request.titulo,
            "status": "success" if resultado["sucesso"] else "error",
            "erro": resultado.get("erro", ""),
            "agendado_para": request.agendar_para,
        })

        return resultado

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/uploads")
async def get_uploads(limit: int = 50):
    """Lista uploads"""
    try:
        uploads = db.get_uploads(limit=limit)
        return {"sucesso": True, "uploads": uploads}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/generations")
async def get_generations(limit: int = 50):
    """Lista gerações"""
    try:
        generations = db.get_generations(limit=limit)
        return {"sucesso": True, "generations": generations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# ROTAS DE CONFIGURAÇÃO
# =============================================================================


@router.get("/dashboard/settings")
async def get_settings():
    """Obtém configurações"""
    try:
        all_settings = db.get_all_settings()

        # Adiciona configurações do sistema
        all_settings["tiktok_configurado"] = bool(tiktok_uploader.sessionid)
        all_settings["openrouter_configurado"] = bool(ia_generator.api_key)
        all_settings["default_model"] = settings.default_model
        all_settings["default_voice"] = settings.default_tts_voice

        return {"sucesso": True, "configuracoes": all_settings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dashboard/settings")
async def update_setting(request: SettingsUpdateRequest):
    """Atualiza uma configuração"""
    try:
        db.save_setting(request.key, request.value)
        return {"sucesso": True, "mensagem": f"Configuração {request.key} atualizada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# ROTAS DE ATIVIDADE
# =============================================================================


@router.get("/dashboard/activity")
async def get_activity(limit: int = 100):
    """Obtém logs de atividade"""
    try:
        logs = db.get_activity_logs(limit=limit)
        return {"sucesso": True, "logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dashboard/activity/log")
async def log_activity(event_type: str, event_data: Dict[str, Any], level: str = "INFO"):
    """Registra uma atividade"""
    try:
        db.log_activity(event_type, event_data, level)
        return {"sucesso": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# ROTAS DE TESTE
# =============================================================================


@router.get("/dashboard/test-ia")
async def test_ia_models():
    """Testa modelos de IA disponíveis"""
    try:
        resultado = await ia_generator.testar_modelos_gratuitos()
        return {"sucesso": True, "teste": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/test-tts")
async def test_tts_voices():
    """Testa vozes TTS disponíveis"""
    try:
        vozes = await tts_module.listar_vozes()
        return {"sucesso": True, "vozes": vozes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/test-sessionid")
async def test_sessionid():
    """Testa SessionID do TikTok"""
    try:
        resultado = await tiktok_uploader_module.validar_sessionid()
        return {"sucesso": True, "validacao": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/news")
async def get_news(limit: int = 20):
    """Obtém notícias atuais"""
    try:
        noticias = await news_fetcher.buscar_todas_noticias()
        return {"sucesso": True, "noticias": noticias[:limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# ROTAS DE UTILITÁRIOS
# =============================================================================


@router.post("/dashboard/reset-database")
async def reset_database():
    """Reseta o banco de dados (cuidado!)"""
    try:
        db.reset_database()
        return {"sucesso": True, "mensagem": "Database resetado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/export-data")
async def export_data():
    """Exporta todos os dados"""
    try:
        data = db.get_dashboard_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
