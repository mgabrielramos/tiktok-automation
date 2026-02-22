"""
Módulo de Geração de Roteiros com IA (OpenRouter - Gratuito)

Usa modelos gratuitos do OpenRouter para gerar roteiros de humor
baseados em notícias atuais.
"""

import asyncio
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import settings


class IAGenerator:
    """Gerador de roteiros usando IA gratuita do OpenRouter"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openrouter_api_key
        self.base_url = settings.openrouter_base_url
        self.default_model = settings.default_model
        self.reasoning_model = settings.reasoning_model
        self.free_models = settings.openrouter_free_models

        # Cliente OpenAI compatível com OpenRouter
        self.client = AsyncOpenAI(
            api_key=self.api_key if self.api_key else "sk-placeholder",
            base_url=self.base_url,
            timeout=settings.request_timeout,
        )

        logger.info(f"IAGenerator inicializado com modelo padrão: {self.default_model}")

    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def gerar_roteiro(
        self,
        noticia_titulo: str,
        noticia_descricao: str,
        noticia_link: str = "",
        template: Optional[str] = None,
        modelo: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Gera um roteiro de humor baseado em uma notícia

        Args:
            noticia_titulo: Título da notícia
            noticia_descricao: Descrição/resumo da notícia
            noticia_link: Link da notícia original
            template: Template de humor a usar (opcional)
            modelo: Modelo IA a usar (opcional)

        Returns:
            Dicionário com roteiro gerado e metadados
        """
        modelo = modelo or self.default_model

        # Prompt do sistema
        system_prompt = self._criar_system_prompt(template)

        # Prompt do usuário
        user_prompt = self._criar_user_prompt(
            noticia_titulo, noticia_descricao, noticia_link
        )

        try:
            logger.info(f"Gerando roteiro com modelo: {modelo}")
            logger.debug(f"Notícia: {noticia_titulo[:100]}...")

            response = await self.client.chat.completions.create(
                model=modelo,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.8,
                max_tokens=500,
                top_p=1.0,
                frequency_penalty=0.3,
                presence_penalty=0.3,
                extra_headers={
                    "HTTP-Referer": "https://github.com/tiktok-automation",
                    "X-Title": "TikTok Automation BR",
                },
            )

            roteiro_texto = response.choices[0].message.content.strip()

            # Parse do roteiro
            roteiro_formatado = self._parsear_roteiro(roteiro_texto)

            logger.success("Roteiro gerado com sucesso!")

            return {
                "sucesso": True,
                "roteiro_completo": roteiro_texto,
                "roteiro_formatado": roteiro_formatado,
                "modelo_usado": modelo,
                "tokens_usados": response.usage.total_tokens if response.usage else 0,
                "timestamp": datetime.now().isoformat(),
                "noticia_original": {
                    "titulo": noticia_titulo,
                    "descricao": noticia_descricao[:200],
                    "link": noticia_link,
                },
            }

        except Exception as e:
            logger.error(f"Erro ao gerar roteiro: {e}")
            return {
                "sucesso": False,
                "erro": str(e),
                "modelo_tentado": modelo,
                "timestamp": datetime.now().isoformat(),
            }

    def _criar_system_prompt(self, template: Optional[str] = None) -> str:
        """Cria o prompt do sistema baseado no template"""

        base_prompt = """Você é um comediante brasileiro de stand-up especializado em humor sobre atualidades.
Seu estilo é leve, irônico e divertido, similar ao Gregório Duvivier, Paulo Gustavo e Whindersson Nunes.

Sua tarefa é criar roteiros para TikTok (vídeos curtos de 15-60 segundos) baseados em notícias atuais.

ESTRUTURA OBRIGATÓRIA DO ROTEIRO:

🎣 HOOK (3 segundos):
- Frase impactante para prender a atenção imediatamente
- Use emojis chamativos
- Deve fazer a pessoa parar de scrollar

📰 NOTÍCIA (10 segundos):
- Resuma a notícia de forma clara e objetiva
- Use linguagem simples e direta
- Mantenha o contexto necessário

😂 PIADA/COMENTÁRIO (20-30 segundos):
- Faça uma observação engraçada/irônica sobre a situação
- Use comparações do cotidiano brasileiro
- Pode usar exagero, ironia ou sarcasmo (com leveza)
- Evite polêmica desnecessária

👆 CALL-TO-ACTION (5 segundos):
- Peça para comentar, compartilhar ou seguir
- Crie engajamento com uma pergunta
- Use emojis

REGRAS IMPORTANTES:
- Use emojis estrategicamente
- Linguagem casual e coloquial (você, galera, gente, mano)
- Máximo 200-250 caracteres no total
- Inclua 3-5 hashtags relevantes no final
- NUNCA faça piada com: tragédias, mortes, violência, crimes hediondos
- Mantenha o humor leve e positivo
- Se a notícia for muito sensível, recuse gentilmente

FORMATO DE SAÍDA (obrigatório):
🎣 [texto do hook]
📰 [texto da notícia]
😂 [texto da piada]
👆 [texto do CTA]

#hashtag1 #hashtag2 #hashtag3 #hashtag4"""

        if template:
            template_prompt = f"\n\nTEMPLATE ESPECÍFICO: Use o estilo '{template}'"
            return base_prompt + template_prompt

        return base_prompt

    def _criar_user_prompt(
        self, titulo: str, descricao: str, link: str
    ) -> str:
        """Cria o prompt do usuário com a notícia"""

        prompt = f"""Crie um roteiro de humor para TikTok baseado nesta notícia:

TÍTULO: {titulo}

DESCRIÇÃO: {descricao}"""

        if link:
            prompt += f"\n\nLINK: {link}"

        prompt += """

Lembre-se:
- Humor leve e divertido
- Estrutura: 🎣 Hook → 📰 Notícia → 😂 Piada → 👆 CTA
- Máximo 60 segundos de duração
- Hashtags no final

Vamos lá, me faça rir! 😄"""

        return prompt

    def _parsear_roteiro(self, texto: str) -> Dict[str, str]:
        """Parseia o roteiro gerado em seções"""

        secoes = {
            "hook": "",
            "noticia": "",
            "piada": "",
            "cta": "",
            "hashtags": "",
        }

        linhas = texto.split("\n")
        secao_atual = None

        for linha in linhas:
            linha = linha.strip()
            if not linha:
                continue

            if "🎣" in linha or "HOOK" in linha.upper():
                secao_atual = "hook"
                secoes["hook"] = linha.replace("🎣", "").replace("HOOK", "").strip(":").strip()
            elif "📰" in linha or "NOTÍCIA" in linha.upper():
                secao_atual = "noticia"
                secoes["noticia"] = linha.replace("📰", "").replace("NOTÍCIA", "").strip(":").strip()
            elif "😂" in linha or "PIADA" in linha.upper():
                secao_atual = "piada"
                secoes["piada"] = linha.replace("😂", "").replace("PIADA", "").strip(":").strip()
            elif "👆" in linha or "CALL" in linha.upper() or "CTA" in linha.upper():
                secao_atual = "cta"
                secoes["cta"] = linha.replace("👆", "").replace("CALL-TO-ACTION", "").replace("CTA", "").strip(":").strip()
            elif linha.startswith("#"):
                secoes["hashtags"] = linha
            elif secao_atual:
                secoes[secao_atual] += " " + linha

        # Se não conseguiu parsear, usa o texto completo como piada
        if not any(secoes.values()):
            secoes["piada"] = texto

        return secoes

    async def testar_modelos_gratuitos(self) -> List[Dict[str, Any]]:
        """Testa todos os modelos gratuitos disponíveis"""

        resultados = []

        for modelo in self.free_models[:3]:  # Testa apenas 3 para economizar
            logger.info(f"Testando modelo: {modelo}")

            try:
                response = await self.client.chat.completions.create(
                    model=modelo,
                    messages=[
                        {"role": "user", "content": "Olá! Responda apenas 'OK' se estiver funcionando."},
                    ],
                    max_tokens=10,
                )

                resultados.append({
                    "modelo": modelo,
                    "status": "funcionando",
                    "resposta": response.choices[0].message.content,
                })

            except Exception as e:
                resultados.append({
                    "modelo": modelo,
                    "status": "erro",
                    "erro": str(e),
                })

        return resultados

    async def gerar_variacoes(
        self,
        noticia_titulo: str,
        noticia_descricao: str,
        quantidade: int = 3,
    ) -> List[Dict[str, Any]]:
        """Gera múltiplas variações do mesmo roteiro"""

        variacoes = []

        for i in range(quantidade):
            template = settings.humor_templates[i % len(settings.humor_templates)]
            modelo = self.free_models[i % len(self.free_models)]

            logger.info(f"Gerando variação {i+1}/{quantidade}")

            resultado = await self.gerar_roteiro(
                noticia_titulo=noticia_titulo,
                noticia_descricao=noticia_descricao,
                template=template["name"],
                modelo=modelo,
            )

            if resultado["sucesso"]:
                variacoes.append(resultado)

        return variacoes


# Instância global
ia_generator = IAGenerator()
