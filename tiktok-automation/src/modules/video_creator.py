"""
Módulo de Criação de Vídeo usando MoviePy e FFmpeg (Gratuito)

Cria vídeos para TikTok combinando:
- Áudio TTS
- Imagens de fundo ou templates
- Legendas automáticas
- Efeitos visuais
"""

import asyncio
import os
import random
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from loguru import logger
from moviepy import (
    VideoFileClip,
    AudioFileClip,
    ImageClip,
    TextClip,
    CompositeVideoClip,
    ColorClip,
    CompositeAudioClip,
    vfx,
)
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential
import httpx

from ..config import settings


class VideoCreator:
    """Criador de vídeos para TikTok usando MoviePy"""

    def __init__(self):
        self.output_dir = settings.videos_dir
        self.templates_dir = settings.templates_dir
        self.width = settings.video_width
        self.height = settings.video_height
        self.fps = settings.video_fps
        self.format = settings.video_format

        # Garante diretórios
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # Fontes para legendas
        self.fontes_disponiveis = self._detectar_fontes()

        logger.info(f"VideoCreator inicializado ({self.width}x{self.height}@{self.fps}fps)")

    def _detectar_fontes(self) -> List[str]:
        """Detecta fontes disponíveis no sistema"""
        fontes_comuns = [
            "Arial",
            "Helvetica",
            "Verdana",
            "Impact",
            "Comic-Sans",
            "Times-New-Roman",
            "Georgia",
            "Courier-New",
        ]

        # Tenta encontrar fontes no sistema
        fontes_encontradas = []
        caminhos_fontes = [
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            "/windows/Fonts",
            "C:/Windows/Fonts",
        ]

        for caminho in caminhos_fontes:
            if os.path.exists(caminho):
                for root, _, files in os.walk(caminho):
                    for file in files:
                        if file.lower().endswith((".ttf", ".otf")):
                            fontes_encontradas.append(os.path.join(root, file))

        logger.info(f"Fontes encontradas: {len(fontes_encontradas)}")
        return fontes_encontradas if fontes_encontradas else fontes_comuns

    async def baixar_imagem_tema(
        self,
        tema: str,
        largura: int = 1080,
        altura: int = 1920,
    ) -> Optional[str]:
        """
        Baixa imagem relacionada ao tema usando múltiplas APIs gratuitas

        Estratégias (em ordem):
        1. Pexels API (mais confiável)
        2. Pixabay API (backup)
        3. Unsplash Source (fallback)
        4. Templates locais (último recurso)

        Args:
            tema: Tema/palavra-chave para buscar imagem
            largura: Largura da imagem
            altura: Altura da imagem

        Returns:
            Caminho da imagem baixada ou None se falhar
        """
        # Extrai palavras-chave
        palavras = tema.lower().split()
        palavras_chave = [
            p for p in palavras
            if len(p) > 3 and p not in ["para", "com", "uma", "esse", "esta", "como", "sobre"]
        ]

        if not palavras_chave:
            palavras_chave = ["news", "brazil"]

        query = "+".join(palavras_chave[:3])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_tema = hashlib.md5(tema.encode()).hexdigest()[:8]

        # 1. Tentar Pexels API
        imagem = await self._buscar_pexels(query, largura, altura, timestamp, hash_tema)
        if imagem:
            return imagem

        # 2. Tentar Pixabay API
        imagem = await self._buscar_pixabay(query, largura, altura, timestamp, hash_tema)
        if imagem:
            return imagem

        # 3. Tentar Unsplash Source
        imagem = await self._buscar_unsplash(query, largura, altura, timestamp, hash_tema)
        if imagem:
            return imagem

        # 4. Gerar template local
        return await self.gerar_template_variado(tema, largura, altura)

    async def _buscar_pexels(
        self,
        query: str,
        largura: int,
        altura: int,
        timestamp: str,
        hash_tema: str,
    ) -> Optional[str]:
        """Busca imagem na API do Pexels"""
        try:
            # Pexels requer API key, mas tem endpoint público limitado
            url = f"https://www.pexels.com/search/{query}/"
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, follow_redirects=True)
                
                if response.status_code == 200:
                    # Extrair URL da primeira imagem (simplificado)
                    import re
                    matches = re.findall(r'https://images\.pexels\.com/photos/\d+/[\w-]+\.jpeg', response.text)
                    
                    if matches:
                        img_url = matches[0]
                        # Baixar imagem
                        img_response = await client.get(img_url)
                        if img_response.status_code == 200:
                            caminho = self.output_dir / f"fundo_pexels_{hash_tema}_{timestamp}.jpg"
                            with open(caminho, "wb") as f:
                                f.write(img_response.content)
                            logger.info(f"Pexels: Imagem baixada {caminho}")
                            return str(caminho)
        except Exception as e:
            logger.debug(f"Pexels falhou: {e}")
        
        return None

    async def _buscar_pixabay(
        self,
        query: str,
        largura: int,
        altura: int,
        timestamp: str,
        hash_tema: str,
    ) -> Optional[str]:
        """Busca imagem na API do Pixabay"""
        try:
            # Pixabay tem API pública sem auth para buscas limitadas
            url = f"https://pixabay.com/api/?q={query}&image_type=photo&orientation=vertical&per_page=3"
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("hits"):
                        # Pega imagem com melhor score
                        hit = max(data["hits"], key=lambda x: x.get("likes", 0))
                        img_url = hit.get("largeImageURL") or hit.get("webformatURL")
                        
                        if img_url:
                            img_response = await client.get(img_url)
                            if img_response.status_code == 200:
                                caminho = self.output_dir / f"fundo_pixabay_{hash_tema}_{timestamp}.jpg"
                                with open(caminho, "wb") as f:
                                    f.write(img_response.content)
                                logger.info(f"Pixabay: Imagem baixada {caminho}")
                                return str(caminho)
        except Exception as e:
            logger.debug(f"Pixabay falhou: {e}")
        
        return None

    async def _buscar_unsplash(
        self,
        query: str,
        largura: int,
        altura: int,
        timestamp: str,
        hash_tema: str,
    ) -> Optional[str]:
        """Busca imagem no Unsplash Source"""
        try:
            url = f"https://source.unsplash.com/{largura}x{altura}/?{query}"
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, follow_redirects=True)
                
                if response.status_code == 200 and response.content:
                    caminho = self.output_dir / f"fundo_unsplash_{hash_tema}_{timestamp}.jpg"
                    with open(caminho, "wb") as f:
                        f.write(response.content)
                    logger.info(f"Unsplash: Imagem baixada {caminho}")
                    return str(caminho)
        except Exception as e:
            logger.debug(f"Unsplash falhou: {e}")
        
        return None

    async def gerar_template_variado(
        self,
        tema: str,
        largura: int = 1080,
        altura: int = 1920,
    ) -> str:
        """
        Gera template de fundo variado e animado

        Cria gradientes, padrões geométricos e texturas
        para evitar o "fundo roxo estático"

        Args:
            tema: Tema para variar o template
            largura: Largura da imagem
            altura: Altura da imagem

        Returns:
            Caminho do template gerado
        """
        # Usa hash do tema para variar cores de forma consistente
        hash_tema = hashlib.md5(tema.encode()).hexdigest()
        seed = int(hash_tema[:8], 16)
        random.seed(seed)

        # Escolhe tipo de template
        tipos = ["gradiente", "gradiente_diagonal", "padrao_geometrico", "textura"]
        tipo = random.choice(tipos)

        logger.info(f"Gerando template {tipo} para tema: {tema[:50]}")

        # Cria imagem
        img = Image.new("RGB", (largura, altura))
        draw = ImageDraw.Draw(img)

        if tipo == "gradiente":
            # Gradiente vertical com cores variadas
            cores = [
                (random.randint(0, 100), random.randint(0, 100), random.randint(100, 200)),
                (random.randint(50, 150), random.randint(0, 100), random.randint(100, 200)),
                (random.randint(0, 100), random.randint(50, 150), random.randint(100, 200)),
            ]
            for y in range(altura):
                r = int(cores[0][0] + (cores[1][0] - cores[0][0]) * y / altura)
                g = int(cores[0][1] + (cores[1][1] - cores[0][1]) * y / altura)
                b = int(cores[0][2] + (cores[2][2] - cores[0][2]) * y / altura)
                draw.line([(0, y), (largura, y)], fill=(r, g, b))

        elif tipo == "gradiente_diagonal":
            # Gradiente diagonal
            cores = [
                (random.randint(0, 100), random.randint(0, 100), random.randint(150, 255)),
                (random.randint(100, 200), random.randint(0, 100), random.randint(100, 200)),
            ]
            for y in range(altura):
                for x in range(largura):
                    fator = (x + y) / (largura + altura)
                    r = int(cores[0][0] + (cores[1][0] - cores[0][0]) * fator)
                    g = int(cores[0][1] + (cores[1][1] - cores[0][1]) * fator)
                    b = int(cores[0][2] + (cores[1][2] - cores[0][2]) * fator)
                    img.putpixel((x, y), (r, g, b))

        elif tipo == "padrao_geometrico":
            # Padrão geométrico com círculos
            cor_fundo = (random.randint(20, 60), random.randint(20, 60), random.randint(60, 120))
            draw.rectangle([0, 0, largura, altura], fill=cor_fundo)
            
            for _ in range(50):
                x = random.randint(0, largura)
                y = random.randint(0, altura)
                r = random.randint(50, 300)
                alpha = random.randint(20, 80)
                cor = (
                    random.randint(100, 200),
                    random.randint(50, 150),
                    random.randint(150, 255),
                    alpha
                )
                # Círculo semi-transparente
                circulo = Image.new("RGBA", (r*2, r*2), (0, 0, 0, 0))
                draw_circulo = ImageDraw.Draw(circulo)
                draw_circulo.ellipse([0, 0, r*2-1, r*2-1], fill=cor)
                img.paste(circulo, (x-r, y-r), circulo)

        elif tipo == "textura":
            # Textura com ruído e sobreposição
            cor_base = (random.randint(30, 80), random.randint(30, 80), random.randint(80, 150))
            draw.rectangle([0, 0, largura, altura], fill=cor_base)
            
            # Adiciona ruído
            pixels = img.load()
            for y in range(altura):
                for x in range(largura):
                    r, g, b = pixels[x, y]
                    ruido = random.randint(-20, 20)
                    pixels[x, y] = (
                        max(0, min(255, r + ruido)),
                        max(0, min(255, g + ruido)),
                        max(0, min(255, b + ruido))
                    )

        # Salva imagem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"template_{tipo}_{hash_tema}_{timestamp}.png"
        caminho = self.output_dir / nome_arquivo
        img.save(caminho, "PNG")
        
        logger.info(f"Template gerado: {caminho}")
        return str(caminho)

    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def criar_video_simples(
        self,
        audio_path: str,
        imagem_fundo: Optional[str] = None,
        cor_fundo: Tuple[int, int, int] = (50, 50, 100),
        titulo: Optional[str] = None,
        texto_principal: Optional[str] = None,
        nome_arquivo: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Cria vídeo simples com áudio e fundo

        Args:
            audio_path: Caminho do arquivo de áudio
            imagem_fundo: Caminho da imagem de fundo (opcional)
            cor_fundo: Cor de fundo RGB se não houver imagem
            titulo: Título para exibir no topo
            texto_principal: Texto principal para exibir
            nome_arquivo: Nome do arquivo de saída

        Returns:
            Dicionário com caminho do vídeo e metadados
        """
        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"video_{timestamp}.{self.format}"

        caminho_saida = self.output_dir / nome_arquivo

        try:
            logger.info("Criando vídeo simples...")

            # Carrega áudio
            audio = AudioFileClip(audio_path)
            duracao = audio.duration

            logger.info(f"Duração do áudio: {duracao:.2f}s")

            # Cria clip de vídeo
            if imagem_fundo and os.path.exists(imagem_fundo):
                # Usa imagem de fundo
                video = self._criar_clip_imagem(
                    imagem_fundo, duracao, audio
                )
            else:
                # Usa cor sólida
                video = self._criar_clip_cor(
                    cor_fundo, duracao, audio
                )

            # Adiciona título se fornecido
            if titulo:
                video = self._adicionar_titulo(video, titulo)

            # Adiciona texto principal se fornecido
            if texto_principal:
                video = self._adicionar_texto_principal(video, texto_principal)

            # Escreve arquivo final
            video.write_videofile(
                str(caminho_saida),
                fps=self.fps,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile="temp-audio.m4a",
                remove_temp=True,
                preset="medium",
                threads=4,
            )

            # Limpa recursos
            video.close()
            audio.close()

            logger.success(f"Vídeo criado: {caminho_saida}")

            return {
                "sucesso": True,
                "caminho_arquivo": str(caminho_saida),
                "nome_arquivo": nome_arquivo,
                "duracao_segundos": duracao,
                "tamanho_bytes": caminho_saida.stat().st_size,
                "resolucao": f"{self.width}x{self.height}",
                "fps": self.fps,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Erro ao criar vídeo: {e}")
            return {
                "sucesso": False,
                "erro": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _criar_clip_imagem(
        self,
        imagem_path: str,
        duracao: float,
        audio: AudioFileClip,
    ) -> CompositeVideoClip:
        """Cria clip de vídeo a partir de imagem com leve zoom"""
        # Abre imagem original
        img_original = Image.open(imagem_path)
        w_orig, h_orig = img_original.size
        
        # Calcula dimensões para zoom (15% maior para evitar bordas)
        zoom_factor = 1.15
        w_zoom = int(w_orig * zoom_factor)
        h_zoom = int(h_orig * zoom_factor)
        
        # Redimensiona imagem para ser maior
        img_resized = img_original.resize((w_zoom, h_zoom), Image.Resampling.LANCZOS)
        
        # Salva imagem redimensionada temporária
        caminho_temp = str(imagem_path).replace(".jpg", "_zoom.jpg").replace(".png", "_zoom.png")
        img_resized.save(caminho_temp)
        
        # Cria clip com a imagem maior e cropa para o formato TikTok
        img_clip = ImageClip(caminho_temp).with_duration(duracao)
        img_clip = img_clip.with_audio(audio)
        
        # Crop centralizado
        img_clip = img_clip.with_effects([
            vfx.Crop(
                x1=(w_zoom - self.width) // 2,
                y1=(h_zoom - self.height) // 2,
                width=self.width,
                height=self.height
            )
        ])
        
        return CompositeVideoClip([img_clip])

    def _criar_clip_cor(
        self,
        cor: Tuple[int, int, int],
        duracao: float,
        audio: AudioFileClip,
    ) -> CompositeVideoClip:
        """Cria clip de vídeo com cor sólida"""
        clip = (
            ColorClip(size=(self.width, self.height), color=cor)
            .with_duration(duracao)
            .with_audio(audio)
        )
        return CompositeVideoClip([clip])

    def _adicionar_titulo(
        self,
        video: CompositeVideoClip,
        titulo: str,
    ) -> CompositeVideoClip:
        """Adiciona título no topo do vídeo"""
        try:
            txt_clip = TextClip(
                text=titulo,
                font_size=48,
                color="white",
                font="Arial-Bold",
                method="caption",
                size=(self.width - 40, None),
            )
        except Exception:
            # Fallback se fonte não disponível
            txt_clip = TextClip(
                text=titulo,
                font_size=48,
                color="white",
                size=(self.width - 40, None),
            )

        txt_clip = (
            txt_clip.with_position(("center", 50))
            .with_duration(video.duration)
        )

        return CompositeVideoClip([video, txt_clip])

    def _adicionar_texto_principal(
        self,
        video: CompositeVideoClip,
        texto: str,
    ) -> CompositeVideoClip:
        """Adiciona texto principal no centro do vídeo"""
        try:
            txt_clip = TextClip(
                text=texto,
                font_size=36,
                color="white",
                font="Arial",
                method="caption",
                size=(self.width - 80, None),
            )
        except Exception:
            txt_clip = TextClip(
                text=texto,
                font_size=36,
                color="white",
                size=(self.width - 80, None),
            )

        txt_clip = (
            txt_clip.with_position(("center", "center"))
            .with_duration(video.duration)
        )

        return CompositeVideoClip([video, txt_clip])

    async def criar_video_com_legendas(
        self,
        audio_path: str,
        roteiro: Dict[str, str],
        imagem_fundo: Optional[str] = None,
        cor_fundo: Tuple[int, int, int] = (50, 50, 100),
        estilo_legendas: str = "tiktok",
        nome_arquivo: Optional[str] = None,
        tema: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Cria vídeo com legendas sincronizadas

        Args:
            audio_path: Caminho do áudio
            roteiro: Roteiro com seções (hook, noticia, piada, cta)
            imagem_fundo: Imagem de fundo
            cor_fundo: Cor de fundo alternativa
            estilo_legendas: Estilo das legendas
            nome_arquivo: Nome do arquivo de saída
            tema: Tema para buscar imagem de fundo relacionada

        Returns:
            Dicionário com informações do vídeo
        """
        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"video_legendas_{timestamp}.{self.format}"

        caminho_saida = self.output_dir / nome_arquivo

        try:
            logger.info("Criando vídeo com legendas...")

            # Carrega áudio
            audio = AudioFileClip(audio_path)
            duracao = audio.duration

            # Tenta baixar imagem de fundo relacionada se não foi fornecida
            imagem_usada = imagem_fundo
            
            # SEMPRE gera template variado se não houver imagem específica
            if not imagem_usada and tema:
                logger.info(f"Gerando template variado para tema: {tema[:50]}")
                imagem_usada = await self.gerar_template_variado(tema, self.width, self.height)
                if imagem_usada:
                    logger.info(f"Template gerado: {imagem_usada}")
            elif not imagem_usada:
                # Sem tema, usa template genérico
                logger.info("Gerando template genérico...")
                imagem_usada = await self.gerar_template_variado("default", self.width, self.height)

            # Cria vídeo base
            if imagem_usada and os.path.exists(imagem_usada):
                video = self._criar_clip_imagem(imagem_usada, duracao, audio)
                logger.info(f"Usando imagem: {imagem_usada}")
            else:
                # Emergency fallback
                logger.warning("Nenhuma imagem disponível, gerando template de emergência")
                imagem_usada = await self.gerar_template_variado("emergency", self.width, self.height)
                video = self._criar_clip_imagem(imagem_usada, duracao, audio)

            # Adiciona legendas
            clips_legendas = self._criar_clips_legendas(
                roteiro, duracao, estilo_legendas
            )

            video_final = CompositeVideoClip([video] + clips_legendas)

            # Escreve arquivo
            video_final.write_videofile(
                str(caminho_saida),
                fps=self.fps,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile="temp-audio.m4a",
                remove_temp=True,
                preset="medium",
                threads=4,
            )

            video_final.close()
            audio.close()

            logger.success(f"Vídeo com legendas criado: {caminho_saida}")

            return {
                "sucesso": True,
                "caminho_arquivo": str(caminho_saida),
                "nome_arquivo": nome_arquivo,
                "duracao_segundos": duracao,
                "tamanho_bytes": caminho_saida.stat().st_size,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Erro ao criar vídeo com legendas: {e}")
            return {
                "sucesso": False,
                "erro": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _criar_clips_legendas(
        self,
        roteiro: Dict[str, str],
        duracao_total: float,
        estilo: str = "tiktok",
    ) -> List[TextClip]:
        """Cria clips de texto para legendas"""
        clips = []

        # Divide tempo entre seções
        secoes = ["hook", "noticia", "piada", "cta"]
        tempo_por_secao = duracao_total / len(secoes)

        # Tenta encontrar uma fonte que suporte UTF-8
        fonte_principal = None
        fonte_fallback = None
        
        # Caminhos de fontes que suportam UTF-8 (Linux e Windows)
        fontes_possiveis = [
            # Debian/Ubuntu
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeMono.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            # Docker (fonts-liberation)
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
            # Windows
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
        ]
        
        for fonte_path in fontes_possiveis:
            if os.path.exists(fonte_path):
                logger.info(f"Fonte encontrada: {fonte_path}")
                if fonte_principal is None:
                    fonte_principal = fonte_path
                else:
                    fonte_fallback = fonte_path
                    break
        
        if fonte_principal is None:
            logger.warning("Nenhuma fonte TrueType encontrada! Acentos podem não funcionar.")
        else:
            logger.info(f"Usando fonte principal: {fonte_principal}")

        for i, secao in enumerate(secoes):
            texto = roteiro.get(secao, "")
            if not texto:
                continue

            # Remove emojis para o texto da legenda
            texto_limpo = self._limpar_texto_legenda(texto)

            # Cria TextClip com fonte que suporta UTF-8
            if fonte_principal:
                txt_clip = TextClip(
                    text=texto_limpo,
                    font_size=32,
                    color="white",
                    stroke_color="black",
                    stroke_width=2,
                    font=fonte_principal,
                    method="caption",
                    size=(self.width - 60, None),
                )
            elif fonte_fallback:
                txt_clip = TextClip(
                    text=texto_limpo,
                    font_size=32,
                    color="white",
                    stroke_color="black",
                    stroke_width=2,
                    font=fonte_fallback,
                    method="caption",
                    size=(self.width - 60, None),
                )
            else:
                # Fallback sem fonte específica (pode ter problemas com acentos)
                txt_clip = TextClip(
                    text=texto_limpo,
                    font_size=32,
                    color="white",
                    stroke_color="black",
                    stroke_width=2,
                    method="caption",
                    size=(self.width - 60, None),
                )

            # Posiciona no centro inferior
            y_pos = int(self.height * 0.7)

            txt_clip = (
                txt_clip.with_position(("center", y_pos))
                .with_start(i * tempo_por_secao)
                .with_duration(tempo_por_secao)
            )

            clips.append(txt_clip)

        return clips

    def _limpar_texto_legenda(self, texto: str) -> str:
        """Limpa texto para legendas - REMOVE COMPLETAMENTE emojis"""
        import re

        # Remove TODOS os emojis e símbolos
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # símbolos e pictogramas
            "\U0001F680-\U0001F6FF"  # transporte
            "\U0001F1E0-\U0001F1FF"  # bandeiras
            "\U0001F900-\U0001F9FF"  # símbolos adicionais
            "\U00002702-\U000027B0"  # dingbats
            "\U000024C2-\U0001F251"  # caracteres circulares
            "\U0001F004-\U0001F004"  # mahjong
            "\U0001F0CF-\U0001F0CF"  # playing card
            "\U0001F170-\U0001F251"  # mais símbolos
            "]+",
            flags=re.UNICODE,
        )
        texto_limpo = emoji_pattern.sub(" ", texto)

        # Remove marcadores de seção do roteiro
        texto_limpo = re.sub(r"^(🎭|📰|😂|👆|🎯|⚡|🎣|🏟️|🤣|🐓|🐰)\s*", "", texto_limpo, flags=re.MULTILINE)

        # Remove múltiplos espaços
        texto_limpo = re.sub(r"\s+", " ", texto_limpo)
        texto_limpo = texto_limpo.strip()

        return texto_limpo

    async def criar_template_gradiente(
        self,
        cores: List[Tuple[int, int, int]] = None,
        nome_arquivo: str = "template_gradiente.png",
    ) -> str:
        """
        Cria um template de gradiente para fundo

        Args:
            cores: Lista de cores RGB para o gradiente
            nome_arquivo: Nome do arquivo de saída

        Returns:
            Caminho do template criado
        """
        if cores is None:
            # Cores padrão estilo TikTok
            cores = [
                (128, 0, 128),    # Roxo
                (255, 0, 128),    # Rosa
                (0, 255, 255),    # Ciano
            ]

        caminho_saida = self.templates_dir / nome_arquivo

        # Cria imagem com gradiente
        img = Image.new("RGB", (self.width, self.height))
        draw = ImageDraw.Draw(img)

        for y in range(self.height):
            r = int(
                cores[0][0] + (cores[1][0] - cores[0][0]) * y / self.height
            )
            g = int(
                cores[0][1] + (cores[1][1] - cores[0][1]) * y / self.height
            )
            b = int(
                cores[0][2] + (cores[1][2] - cores[0][2]) * y / self.height
            )
            draw.line((0, y, self.width, y), fill=(r, g, b))

        img.save(str(caminho_saida))
        logger.info(f"Template gradiente criado: {caminho_saida}")

        return str(caminho_saida)

    async def gerar_template_padrao(self) -> str:
        """Gera template padrão para o projeto"""
        return await self.criar_template_gradiente(
            cores=[
                (60, 20, 80),     # Roxo escuro
                (120, 40, 100),   # Roxo médio
                (180, 60, 120),   # Rosa
            ],
            nome_arquivo="fundo_padrao.png",
        )


# Instância global
video_creator = VideoCreator()
