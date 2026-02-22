"""
Módulo de Busca de Notícias via RSS

Busca notícias atuais de múltiplas fontes em português
para gerar conteúdo de humor.
"""

import asyncio
import aiohttp
import feedparser
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from bs4 import BeautifulSoup

from ..config import settings


class NewsFetcher:
    """Buscador de notícias via RSS"""

    def __init__(self):
        self.sources = [s for s in settings.news_sources if s.get("enabled", True)]
        self.blocklist = settings.news_keywords_blocklist
        self.filter_keywords = settings.news_keywords_filter
        self.max_news = settings.max_news_per_day

        logger.info(f"NewsFetcher inicializado com {len(self.sources)} fontes")

    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def buscar_noticias(self, fonte: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Busca notícias de uma fonte RSS específica

        Args:
            fonte: Dicionário com informações da fonte

        Returns:
            Lista de notícias
        """
        noticias = []

        try:
            logger.debug(f"Buscando notícias de: {fonte['name']}")

            async with aiohttp.ClientSession() as session:
                async with session.get(fonte["url"], timeout=15) as response:
                    if response.status != 200:
                        logger.warning(f"Fonte {fonte['name']} retornou status {response.status}")
                        return []

                    rss_content = await response.text()

            # Parse do RSS
            feed = feedparser.parse(rss_content)

            for entry in feed.entries[:20]:  # Limite por segurança
                noticia = self._processar_entry(entry, fonte["name"])

                if noticia:
                    noticias.append(noticia)

            logger.info(f"{fonte['name']}: {len(noticias)} notícias encontradas")

        except Exception as e:
            logger.error(f"Erro ao buscar notícias de {fonte['name']}: {e}")

        return noticias

    def _processar_entry(
        self,
        entry: feedparser.FeedParserDict,
        fonte_nome: str,
    ) -> Optional[Dict[str, Any]]:
        """Processa uma entrada RSS"""

        titulo = getattr(entry, "title", "")
        if not titulo:
            return None

        # Limpa título
        titulo = self._limpar_html(titulo)

        # Verifica blocklist
        if self._esta_na_blocklist(titulo):
            logger.debug(f"Notícia na blocklist: {titulo[:50]}")
            return None

        # Verifica filtro (se configurado)
        if self.filter_keywords and not self._esta_no_filtro(titulo):
            return None

        # Descrição
        descricao = getattr(entry, "description", "")
        descricao = self._limpar_html(descricao) if descricao else ""

        # Link
        link = getattr(entry, "link", "")

        # Data de publicação
        data_pub = getattr(entry, "published_parsed", None)
        if data_pub:
            data_pub = datetime(*data_pub[:6])
        else:
            data_pub = datetime.now()

        return {
            "titulo": titulo,
            "descricao": descricao[:500],  # Limite de tamanho
            "link": link,
            "fonte": fonte_nome,
            "data_publicacao": data_pub.isoformat(),
            "categoria": getattr(entry, "category", ""),
        }

    def _limpar_html(self, texto: str) -> str:
        """Limpa HTML do texto"""
        if not texto:
            return ""

        try:
            soup = BeautifulSoup(texto, "html.parser")
            texto_limpo = soup.get_text(separator=" ", strip=True)
            return " ".join(texto_limpo.split())
        except Exception:
            return texto

    def _esta_na_blocklist(self, texto: str) -> bool:
        """Verifica se texto contém palavras da blocklist"""
        texto_lower = texto.lower()
        return any(palavra.lower() in texto_lower for palavra in self.blocklist)

    def _esta_no_filtro(self, texto: str) -> bool:
        """Verifica se texto contém palavras do filtro"""
        if not self.filter_keywords:
            return True

        texto_lower = texto.lower()
        return any(palavra.lower() in texto_lower for palavra in self.filter_keywords)

    async def buscar_todas_noticias(self) -> List[Dict[str, Any]]:
        """
        Busca notícias de todas as fontes simultaneamente

        Returns:
            Lista consolidada de notícias
        """
        logger.info("Buscando notícias de todas as fontes...")

        # Busca paralela
        tasks = [self.buscar_noticias(fonte) for fonte in self.sources]
        resultados = await asyncio.gather(*tasks, return_exceptions=True)

        # Consolida resultados
        todas_noticias = []
        for resultado in resultados:
            if isinstance(resultado, list):
                todas_noticias.extend(resultado)

        # Remove duplicatas por título
        todas_noticias = self._remover_duplicatas(todas_noticias)

        # Ordena por data (mais recentes primeiro)
        todas_noticias.sort(
            key=lambda x: x.get("data_publicacao", ""),
            reverse=True,
        )

        logger.info(f"Total de notícias únicas: {len(todas_noticias)}")

        return todas_noticias

    def _remover_duplicatas(
        self,
        noticias: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Remove notícias duplicadas por título"""
        vistas = set()
        unicas = []

        for noticia in noticias:
            titulo_normalizado = self._normalizar_titulo(noticia["titulo"])

            if titulo_normalizado not in vistas:
                vistas.add(titulo_normalizado)
                unicas.append(noticia)

        return unicas

    def _normalizar_titulo(self, titulo: str) -> str:
        """Normaliza título para comparação"""
        # Remove acentos, lowercase, remove espaços extras
        import unicodedata

        titulo = titulo.lower().strip()
        titulo = "".join(
            c
            for c in unicodedata.normalize("NFD", titulo)
            if unicodedata.category(c) != "Mn"
        )
        return " ".join(titulo.split())

    async def buscar_noticia_aleatoria(self) -> Optional[Dict[str, Any]]:
        """
        Busca uma notícia aleatória para gerar conteúdo

        Returns:
            Uma notícia aleatória ou None
        """
        todas = await self.buscar_todas_noticias()

        if not todas:
            return None

        import random
        return random.choice(todas)

    async def buscar_noticias_por_tema(
        self,
        tema: str,
        limite: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Busca notícias relacionadas a um tema específico

        Args:
            tema: Palavra-chave do tema
            limite: Número máximo de notícias

        Returns:
            Lista de notícias relacionadas
        """
        todas = await self.buscar_todas_noticias()

        # Filtra por tema
        relacionadas = [
            n for n in todas
            if tema.lower() in n["titulo"].lower()
            or tema.lower() in n.get("descricao", "").lower()
        ]

        return relacionadas[:limite]

    async def buscar_resumo_diario(self) -> Dict[str, Any]:
        """
        Busca resumo das principais notícias do dia

        Returns:
            Dicionário com resumo diário
        """
        noticias = await self.buscar_todas_noticias()

        # Pega top 10
        top_10 = noticias[:10]

        # Agrupa por fonte
        por_fonte = {}
        for noticia in top_10:
            fonte = noticia["fonte"]
            if fonte not in por_fonte:
                por_fonte[fonte] = []
            por_fonte[fonte].append(noticia)

        return {
            "data": datetime.now().isoformat(),
            "total_noticias": len(noticias),
            "top_10": top_10,
            "por_fonte": por_fonte,
            "fontes_ativas": list(por_fonte.keys()),
        }


# Instância global
news_fetcher = NewsFetcher()
