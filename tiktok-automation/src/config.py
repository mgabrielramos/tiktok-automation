"""
Configurações do projeto
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """Configurações principais da aplicação"""

    # =============================================================================
    # GERAIS
    # =============================================================================
    app_name: str = "TikTok Automation"
    version: str = "1.0.0"
    debug: bool = False
    timezone: str = "America/Sao_Paulo"
    log_level: str = "INFO"

    # =============================================================================
    # OPENROUTER (IA GRATUITA)
    # =============================================================================
    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    # Modelos gratuitos disponíveis (fevereiro 2026)
    openrouter_free_models: List[str] = [
        "meta-llama/llama-3.3-70b-instruct:free",
        "google/gemma-3-27b-it:free",
        "mistralai/mistral-small-3.1-24b-instruct:free",
        "qwen/qwen3-coder:free",
        "stepfun/step-3.5-flash:free",
        "nvidia/nemotron-3-nano-30b-a3b:free",
        "deepseek/deepseek-r1-0528:free",
    ]
    # Modelo padrão para humor em português
    default_model: str = "meta-llama/llama-3.3-70b-instruct:free"
    # Modelo para raciocínio mais elaborado
    reasoning_model: str = "deepseek/deepseek-r1-0528:free"

    # =============================================================================
    # TIKTOK
    # =============================================================================
    tiktok_sessionid: Optional[str] = None
    tiktok_base_url: str = "https://www.tiktok.com"
    video_privacy: str = "public"  # public, private, friends
    allow_comments: bool = True
    allow_duet: bool = True
    allow_stitch: bool = True
    ai_label: bool = False  # Marcar como conteúdo gerado por IA

    # =============================================================================
    # VÍDEO E ÁUDIO
    # =============================================================================
    video_width: int = 1080
    video_height: int = 1920
    video_fps: int = 30
    video_format: str = "mp4"
    audio_format: str = "mp3"
    audio_sample_rate: int = 44100
    max_video_duration: int = 60  # segundos
    min_video_duration: int = 15  # segundos

    # =============================================================================
    # TTS (EDGE TTS)
    # =============================================================================
    # Vozes em português do Brasil disponíveis no Edge TTS
    tts_voices: List[str] = [
        "pt-BR-FranciscaNeural",  # Feminina, recomendada
        "pt-BR-AntonioNeural",    # Masculina
        "pt-BR-BrendaNeural",     # Feminina emocional
        "pt-BR-DonatoNeural",     # Masculina
        "pt-BR-ElzaNeural",       # Feminina
        "pt-BR-FabioNeural",      # Masculina
        "pt-BR-GiovannaNeural",   # Feminina
        "pt-BR-HumbertoNeural",   # Masculina
        "pt-BR-JulioNeural",      # Masculina
        "pt-BR-LeilaNeural",      # Feminina
    ]
    default_tts_voice: str = "pt-BR-FranciscaNeural"
    tts_rate: str = "+0%"  # Velocidade: -50% a +100%
    tts_pitch: str = "+0Hz"  # Tom: -50Hz a +50Hz

    # =============================================================================
    # NOTÍCIAS
    # =============================================================================
    news_sources: List[dict] = [
        {
            "name": "G1",
            "url": "https://rss.globo.com/rss/feeds/ultimas-noticias.xml",
            "language": "pt-BR",
            "enabled": True,
        },
        {
            "name": "BBC Brasil",
            "url": "https://feeds.bbci.co.uk/portuguese/rss.xml",
            "language": "pt-BR",
            "enabled": True,
        },
        {
            "name": "UOL",
            "url": "https://noticias.uol.com.br/rss/ultimas-noticias.xml",
            "language": "pt-BR",
            "enabled": True,
        },
        {
            "name": "R7",
            "url": "https://feeds.r7.com/r7/ultimas-noticias/feed/",
            "language": "pt-BR",
            "enabled": True,
        },
        {
            "name": "CNN Brasil",
            "url": "https://www.cnnbrasil.com.br/feed/",
            "language": "pt-BR",
            "enabled": True,
        },
    ]
    news_keywords_filter: List[str] = []  # Palavras-chave para filtrar (opcional)
    news_keywords_blocklist: List[str] = [
        "tragédia",
        "morte",
        "assassinato",
        "violência",
        "estupro",
        "suicídio",
    ]
    max_news_per_day: int = 5

    # =============================================================================
    # HUMOR - TEMPLATES
    # =============================================================================
    humor_templates: List[dict] = [
        {
            "name": "Ironia da Realidade",
            "hook": "🎭 VOCÊ NÃO VAI ACREDITAR!",
            "style": "irônico",
            "tone": "sarcástico",
        },
        {
            "name": "Pergunta Retórica",
            "hook": "🤔 SÉRIO ISSO MESMO?",
            "style": "questionador",
            "tone": "incrédulo",
        },
        {
            "name": "Comparação Engraçada",
            "hook": "😂 ISSO AÍ É TIPO...",
            "style": "comparativo",
            "tone": "descontraído",
        },
        {
            "name": "Plot Twist",
            "hook": "🎬 PLOT TWIST DO ANO!",
            "style": "narrativo",
            "tone": "surpreso",
        },
        {
            "name": "Reação Exagerada",
            "hook": "🚨 ALERTA DE NOTÍCIA BIZARRA!",
            "style": "reativo",
            "tone": "exagerado",
        },
    ]

    # =============================================================================
    # DIRETÓRIOS
    # =============================================================================
    base_dir: Path = Path("/app")
    output_dir: Path = Path("/app/output")
    videos_dir: Path = Path("/app/output/videos")
    audio_dir: Path = Path("/app/output/audio")
    scripts_dir: Path = Path("/app/output/scripts")
    templates_dir: Path = Path("/app/templates")
    config_dir: Path = Path("/app/config")
    logs_dir: Path = Path("/app/logs")

    # =============================================================================
    # AGENDAMENTO
    # =============================================================================
    generate_time: str = "09:00"  # Horário para gerar roteiro
    upload_time: str = "18:00"    # Horário para postar (horário de pico)
    schedule_timezone: str = "America/Sao_Paulo"

    # =============================================================================
    # N8N INTEGRATION
    # =============================================================================
    n8n_webhook_url: Optional[str] = None
    n8n_callback_enabled: bool = False

    # =============================================================================
    # RETRY CONFIG
    # =============================================================================
    max_retries: int = 3
    retry_delay: int = 5  # segundos
    request_timeout: int = 30  # segundos

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def create_directories(self):
        """Cria todos os diretórios necessários"""
        for directory in [
            self.output_dir,
            self.videos_dir,
            self.audio_dir,
            self.scripts_dir,
            self.templates_dir,
            self.config_dir,
            self.logs_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)


# Instância global de configurações
settings = Settings()
