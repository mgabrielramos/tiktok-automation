"""
Módulo de Upload para TikTok usando tiktok-uploader

Upload automatizado de vídeos para TikTok usando autenticação
por cookies (sessionid).
"""

import asyncio
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import settings


class TikTokUploaderModule:
    """Módulo de upload para TikTok"""

    def __init__(self, sessionid: Optional[str] = None):
        self.sessionid = sessionid or settings.tiktok_sessionid
        self.base_url = settings.tiktok_base_url
        self.privacy = settings.video_privacy
        self.allow_comments = settings.allow_comments
        self.allow_duet = settings.allow_duet
        self.allow_stitch = settings.allow_stitch
        self.ai_label = settings.ai_label

        # Valida sessionid
        if not self.sessionid:
            logger.warning("TIKTOK_SESSIONID não configurado!")
        else:
            logger.info("TikTokUploaderModule inicializado")

    def _map_privacy(self) -> int:
        """Mapeia privacidade para valor numérico da API"""
        mapping = {
            "public": 0,
            "private": 1,
            "friends": 2,
        }
        return mapping.get(self.privacy, 0)

    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=1, min=5, max=30),
    )
    async def upload_video(
        self,
        video_path: str,
        titulo: str,
        agendar_para: Optional[datetime] = None,
        sessionid: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Faz upload de vídeo para TikTok

        Args:
            video_path: Caminho do arquivo de vídeo
            titulo: Título/descrição do vídeo
            agendar_para: Data/hora para agendar (opcional)
            sessionid: Session ID override (opcional)

        Returns:
            Dicionário com resultado do upload
        """
        sessionid = sessionid or self.sessionid

        if not sessionid:
            return {
                "sucesso": False,
                "erro": "SessionID não configurado. Configure TIKTOK_SESSIONID no .env",
                "timestamp": datetime.now().isoformat(),
            }

        if not os.path.exists(video_path):
            return {
                "sucesso": False,
                "erro": f"Arquivo de vídeo não encontrado: {video_path}",
                "timestamp": datetime.now().isoformat(),
            }

        try:
            logger.info(f"Iniciando upload: {video_path}")
            logger.info(f"Título: {titulo[:100]}...")

            # Importa tiktok-uploader
            from tiktok_uploader.upload import upload_video

            # Prepara parâmetros
            kwargs = {
                "filename": video_path,
                "description": titulo,
                "sessionid": sessionid,
                "comment": self.allow_comments,
                "duet": self.allow_duet,
                "stitch": self.allow_stitch,
                "privacy": self._map_privacy(),
            }

            # Adiciona agendamento se fornecido
            if agendar_para:
                # TikTok requer agendamento entre 15 minutos e 10 dias
                agora = datetime.now()
                diferenca = agendar_para - agora

                if diferenca.total_seconds() < 900:  # 15 minutos
                    logger.warning("Agendamento muito próximo, upload imediato")
                elif diferenca.total_seconds() > 864000:  # 10 dias
                    logger.warning("Agendamento muito distante, upload imediato")
                else:
                    kwargs["schedule"] = agendar_para

            # Adiciona label de IA se configurado
            if self.ai_label:
                kwargs["ai_label"] = True

            # Executa upload
            logger.info("Enviando para TikTok...")

            # Executa em thread pool para não bloquear
            loop = asyncio.get_event_loop()
            resultado = await loop.run_in_executor(
                None,
                lambda: upload_video(**kwargs),
            )

            logger.success(f"Upload concluído: {resultado}")

            return {
                "sucesso": True,
                "mensagem": "Upload realizado com sucesso!",
                "video_path": video_path,
                "titulo": titulo,
                "agendado": agendar_para.isoformat() if agendar_para else None,
                "resultado": str(resultado),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Erro no upload: {e}")
            return {
                "sucesso": False,
                "erro": str(e),
                "video_path": video_path,
                "titulo": titulo,
                "timestamp": datetime.now().isoformat(),
            }

    async def upload_com_cookies_file(
        self,
        video_path: str,
        titulo: str,
        cookies_file: str,
        agendar_para: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Upload usando arquivo de cookies

        Args:
            video_path: Caminho do vídeo
            titulo: Título do vídeo
            cookies_file: Caminho do arquivo cookies.txt
            agendar_para: Data/hora para agendar

        Returns:
            Dicionário com resultado
        """
        if not os.path.exists(cookies_file):
            return {
                "sucesso": False,
                "erro": f"Arquivo de cookies não encontrado: {cookies_file}",
            }

        try:
            from tiktok_uploader.upload import TikTokUploader

            logger.info(f"Upload com cookies: {cookies_file}")

            uploader = TikTokUploader(cookies=cookies_file)

            loop = asyncio.get_event_loop()
            resultado = await loop.run_in_executor(
                None,
                lambda: uploader.upload_video(
                    video_path,
                    description=titulo,
                    schedule=agendar_para,
                ),
            )

            return {
                "sucesso": True,
                "mensagem": "Upload realizado com cookies!",
                "resultado": str(resultado),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Erro no upload com cookies: {e}")
            return {
                "sucesso": False,
                "erro": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def validar_sessionid(self, sessionid: Optional[str] = None) -> Dict[str, Any]:
        """
        Valida se o sessionid está funcionando

        Args:
            sessionid: Session ID para validar

        Returns:
            Dicionário com status da validação
        """
        sessionid = sessionid or self.sessionid

        if not sessionid:
            return {
                "valido": False,
                "erro": "SessionID não fornecido",
            }

        try:
            # Tenta fazer uma requisição simples para validar
            import httpx

            headers = {
                "Cookie": f"sessionid={sessionid}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.tiktok.com/api/user/detail/",
                    headers=headers,
                    timeout=10,
                )

                if response.status_code == 200:
                    return {
                        "valido": True,
                        "mensagem": "SessionID válido!",
                        "timestamp": datetime.now().isoformat(),
                    }
                else:
                    return {
                        "valido": False,
                        "erro": f"Status code: {response.status_code}",
                        "timestamp": datetime.now().isoformat(),
                    }

        except Exception as e:
            return {
                "valido": False,
                "erro": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def gerar_cookies_file(self, output_path: str) -> bool:
        """
        Gera arquivo de cookies a partir do sessionid

        Args:
            output_path: Caminho para salvar o arquivo

        Returns:
            True se sucesso, False caso contrário
        """
        if not self.sessionid:
            logger.error("SessionID não configurado")
            return False

        try:
            cookies_content = f"""# Netscape HTTP Cookie File
# https://curl.haxx.se/docs/http-cookies.html
# This file was generated by TikTok Automation

.tiktok.com	TRUE	/	FALSE	2147483647	sessionid	{self.sessionid}
"""

            with open(output_path, "w") as f:
                f.write(cookies_content)

            logger.info(f"Cookies file gerado: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Erro ao gerar cookies file: {e}")
            return False

    async def upload_multiplos(
        self,
        videos: List[Dict[str, Any]],
        intervalo_minutos: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Faz upload de múltiplos vídeos com intervalo

        Args:
            videos: Lista de dicts com video_path e titulo
            intervalo_minutos: Intervalo entre uploads

        Returns:
            Lista de resultados
        """
        resultados = []

        for i, video_info in enumerate(videos):
            logger.info(f"Upload {i+1}/{len(videos)}")

            resultado = await self.upload_video(
                video_path=video_info["video_path"],
                titulo=video_info["titulo"],
            )

            resultados.append(resultado)

            # Aguarda intervalo antes do próximo (exceto o último)
            if i < len(videos) - 1:
                aguardar = intervalo_minutos * 60
                logger.info(f"Aguardando {intervalo_minutos} minutos...")
                await asyncio.sleep(aguardar)

        return resultados


# Instância global
tiktok_uploader_module = TikTokUploaderModule()
