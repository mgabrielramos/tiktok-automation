"""
Módulo de Text-to-Speech usando Edge TTS (Gratuito)

Microsoft Edge TTS oferece vozes neurais de alta qualidade
gratuitamente, sem limites rígidos de uso.
"""

import asyncio
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger
import edge_tts
from edge_tts import VoicesManager, SubMaker
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import settings


class TTSModule:
    """Módulo de Text-to-Speech usando Edge TTS"""

    def __init__(self):
        self.output_dir = settings.audio_dir
        self.default_voice = settings.default_tts_voice
        self.voices = settings.tts_voices
        self.rate = settings.tts_rate
        self.pitch = settings.tts_pitch

        # Garante que o diretório de saída existe
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"TTSModule inicializado com voz padrão: {self.default_voice}")

    async def listar_vozes(self, language: str = "pt-BR") -> List[Dict[str, str]]:
        """
        Lista todas as vozes disponíveis para um idioma

        Args:
            language: Código do idioma (padrão: pt-BR)

        Returns:
            Lista de dicionários com informações das vozes
        """
        try:
            voices_manager = await VoicesManager.create()
            vozes_pt = voices_manager.find(Language=language)

            resultado = []
            for voz in vozes_pt:
                resultado.append({
                    "name": voz["Name"],
                    "gender": voz["Gender"],
                    "language": voz["Language"],
                    "locale": voz["Locale"],
                    "friendly_name": voz.get("FriendlyName", voz["Name"]),
                })

            logger.info(f"Encontradas {len(resultado)} vozes para {language}")
            return resultado

        except Exception as e:
            logger.error(f"Erro ao listar vozes: {e}")
            return []

    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def gerar_audio(
        self,
        texto: str,
        voz: Optional[str] = None,
        nome_arquivo: Optional[str] = None,
        rate: Optional[str] = None,
        pitch: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Gera áudio a partir de texto usando Edge TTS

        Args:
            texto: Texto para converter em fala
            voz: Nome da voz (padrão: voz padrão configurada)
            nome_arquivo: Nome do arquivo de saída (opcional)
            rate: Velocidade (+0%, -10%, +20%, etc.)
            pitch: Tom (+0Hz, -10Hz, +20Hz, etc.)

        Returns:
            Dicionário com caminho do arquivo e metadados
        """
        voz = voz or self.default_voice
        rate = rate or self.rate
        pitch = pitch or self.pitch

        # Gera nome do arquivo se não fornecido
        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"audio_{timestamp}.mp3"

        caminho_saida = self.output_dir / nome_arquivo

        try:
            logger.info(f"Gerando áudio com voz: {voz}")
            logger.debug(f"Texto ({len(texto)} chars): {texto[:100]}...")

            # Cria comunicação Edge TTS
            communicate = edge_tts.Communicate(
                text=texto,
                voice=voz,
                rate=rate,
                pitch=pitch,
            )

            # Salva o áudio
            await communicate.save(str(caminho_saida))

            # Verifica se o arquivo foi criado
            if not caminho_saida.exists():
                raise Exception("Arquivo de áudio não foi criado")

            # Obtém duração do áudio
            duracao = await self._obter_duracao_audio(caminho_saida)

            logger.success(f"Áudio gerado: {caminho_saida} ({duracao:.2f}s)")

            return {
                "sucesso": True,
                "caminho_arquivo": str(caminho_saida),
                "nome_arquivo": nome_arquivo,
                "voz_usada": voz,
                "duracao_segundos": duracao,
                "tamanho_bytes": caminho_saida.stat().st_size,
                "texto_caracteres": len(texto),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Erro ao gerar áudio: {e}")
            return {
                "sucesso": False,
                "erro": str(e),
                "caminho_tentado": str(caminho_saida),
                "voz_tentada": voz,
                "timestamp": datetime.now().isoformat(),
            }

    async def gerar_audio_com_legendas(
        self,
        texto: str,
        voz: Optional[str] = None,
        nome_arquivo: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Gera áudio com arquivo de legendas SRT/VTT

        Args:
            texto: Texto para converter em fala
            voz: Nome da voz
            nome_arquivo: Nome base do arquivo

        Returns:
            Dicionário com caminhos dos arquivos gerados
        """
        voz = voz or self.default_voice

        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"audio_legendas_{timestamp}"

        caminho_audio = self.output_dir / f"{nome_arquivo}.mp3"
        caminho_legendas = self.output_dir / f"{nome_arquivo}.vtt"

        try:
            logger.info(f"Gerando áudio com legendas: {voz}")

            # Cria comunicação
            communicate = edge_tts.Communicate(text=texto, voice=voz)

            # Gera áudio e legendas simultaneamente
            submaker = SubMaker()

            with open(caminho_audio, "wb") as audio_file:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_file.write(chunk["data"])
                    elif chunk["type"] == "WordBoundary":
                        submaker.create_sub(
                            (chunk["offset"], chunk["duration"]),
                            chunk["text"],
                        )

            # Salva legendas
            with open(caminho_legendas, "w", encoding="utf-8") as f:
                f.write(submaker.generate_subs())

            duracao = await self._obter_duracao_audio(caminho_audio)

            logger.success(f"Áudio e legendas gerados com sucesso!")

            return {
                "sucesso": True,
                "caminho_audio": str(caminho_audio),
                "caminho_legendas": str(caminho_legendas),
                "duracao_segundos": duracao,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Erro ao gerar áudio com legendas: {e}")
            return {
                "sucesso": False,
                "erro": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _obter_duracao_audio(self, caminho_audio: Path) -> float:
        """Obtém a duração de um arquivo de áudio usando mutagen ou ffprobe"""
        try:
            # Tenta usar mutagen primeiro
            from mutagen.mp3 import MP3
            audio = MP3(str(caminho_audio))
            return audio.info.length
        except ImportError:
            logger.debug("Mutagen não disponível, usando ffprobe")
        except Exception:
            logger.debug("Erro ao ler duração com mutagen, usando ffprobe")

        # Fallback para ffprobe
        try:
            import subprocess
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    str(caminho_audio),
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return float(result.stdout.strip())
        except Exception as e:
            logger.warning(f"Não foi possível obter duração do áudio: {e}")
            return 0.0

    async def gerar_audio_roteiro_completo(
        self,
        roteiro: Dict[str, str],
        voz: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Gera áudio completo a partir de roteiro formatado

        Args:
            roteiro: Dicionário com seções do roteiro (hook, noticia, piada, cta)
            voz: Nome da voz

        Returns:
            Dicionário com caminho do áudio completo
        """
        # Combina todas as seções do roteiro
        texto_completo = " ".join([
            roteiro.get("hook", ""),
            roteiro.get("noticia", ""),
            roteiro.get("piada", ""),
            roteiro.get("cta", ""),
        ])

        # Remove emojis e caracteres especiais para o TTS
        texto_limpo = self._limpar_texto_tts(texto_completo)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"roteiro_completo_{timestamp}.mp3"

        return await self.gerar_audio(
            texto=texto_limpo,
            voz=voz,
            nome_arquivo=nome_arquivo,
        )

    def _limpar_texto_tts(self, texto: str) -> str:
        """
        Limpa texto para melhor síntese de voz

        Remove emojis excessivos e formatação que pode interferir no TTS
        """
        import re

        # Remove TODOS os emojis (TTS não consegue ler emojis)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # símbolos e pictogramas
            "\U0001F680-\U0001F6FF"  # transporte e símbolos de mapa
            "\U0001F1E0-\U0001F1FF"  # bandeiras
            "\U0001F900-\U0001F9FF"  # símbolos adicionais
            "\U00002702-\U000027B0"  # dingbats
            "\U000024C2-\U0001F251"  # caracteres circulares
            "]+",
            flags=re.UNICODE,
        )
        texto = emoji_pattern.sub(" ", texto)

        # Mantém alguns emojis para expressão, remove excesso
        # Remove múltiplos espaços
        texto = re.sub(r"\s+", " ", texto)

        # Remove hashtags do meio do texto
        texto = re.sub(r"#\w+", "", texto)

        # Remove menções
        texto = re.sub(r"@\w+", "", texto)

        # Remove marcadores de seção do roteiro
        texto = re.sub(r"^(🎭|📰|😂|👆|🎯|⚡)\s*", "", texto, flags=re.MULTILINE)

        # Limpa espaços extras
        texto = texto.strip()

        return texto

    async def testar_vozes(
        self,
        texto_teste: str = "Olá! Este é um teste de voz.",
        vozes_limit: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Testa múltiplas vozes com um texto padrão

        Args:
            texto_teste: Texto para teste
            vozes_limit: Número máximo de vozes para testar

        Returns:
            Lista de resultados dos testes
        """
        vozes_disponiveis = await self.listar_vozes()
        resultados = []

        for voz_info in vozes_disponiveis[:vozes_limit]:
            voz = voz_info["name"]
            logger.info(f"Testando voz: {voz}")

            resultado = await self.gerar_audio(
                texto=texto_teste,
                voz=voz,
                nome_arquivo=f"teste_voz_{voz.replace('-', '_')}.mp3",
            )

            resultado["voz_info"] = voz_info
            resultados.append(resultado)

        return resultados


# Instância global
tts_module = TTSModule()
