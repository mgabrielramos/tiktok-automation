# 🤝 Contribuindo com o TikTok Automation

Obrigado pelo interesse em contribuir! Este guia explica como participar do projeto.

---

## 📋 Índice

- [Como Contribuir](#como-contribuir)
- [Reportar Bugs](#reportar-bugs)
- [Sugerir Melhorias](#sugerir-melhorias)
- [Enviar Pull Requests](#enviar-pull-requests)
- [Padrões de Código](#padrões-de-código)
- [Roadmap e Sugestões](#roadmap-e-sugestões)

---

## Como Contribuir

1. **Fork** o repositório
2. Crie uma branch para sua funcionalidade: `git checkout -b feature/minha-funcionalidade`
3. Faça suas alterações seguindo os [padrões de código](#padrões-de-código)
4. Teste as mudanças localmente
5. Commit com mensagens claras: `git commit -m 'Adiciona suporte a múltiplas contas TikTok'`
6. Push para sua branch: `git push origin feature/minha-funcionalidade`
7. Abra um **Pull Request** com descrição detalhada

---

## Reportar Bugs

Ao abrir uma issue para reportar um bug, inclua:

- **Versão** do Python, Docker e sistema operacional
- **Passos para reproduzir** o problema
- **Comportamento esperado** vs. comportamento atual
- **Logs relevantes** (`docker-compose logs tiktok-automation`)
- **Screenshots** se aplicável

---

## Sugerir Melhorias

Sugestões são bem-vindas! Abra uma issue com:

- Descrição clara da melhoria proposta
- Caso de uso / motivação
- Exemplos de implementação (opcional)

---

## Enviar Pull Requests

### Requisitos

- O código deve funcionar com Python 3.11+
- Seguir o estilo de código existente (PEP 8)
- Não quebrar funcionalidades existentes
- Documentar novas funcionalidades no README ou nos arquivos `docs/`

### Estrutura de Branches

| Branch | Propósito |
|--------|-----------|
| `master` | Código estável e em produção |
| `feature/*` | Novas funcionalidades |
| `fix/*` | Correções de bugs |
| `docs/*` | Melhorias de documentação |

---

## Padrões de Código

### Python

```python
# ✅ Bom: docstrings, type hints, logging com loguru
from loguru import logger

async def gerar_roteiro(noticia: dict) -> dict:
    """Gera roteiro de humor a partir de uma notícia.

    Args:
        noticia: Dicionário com título e descrição da notícia.

    Returns:
        Dicionário com as seções do roteiro (hook, notícia, piada, cta).
    """
    logger.info(f"Gerando roteiro para: {noticia['titulo']}")
    # ...

# ❌ Evitar: sem tipos, sem documentação, print() ao invés de logger
def gerar(n):
    print("gerando")
    # ...
```

### Commits

Use mensagens de commit claras no imperativo:

```
✅ Adiciona suporte a múltiplas contas TikTok
✅ Corrige erro de encoding no TTS
✅ Melhora tratamento de erros na busca de notícias
❌ fix
❌ changes
❌ update stuff
```

---

## Roadmap e Sugestões

Abaixo estão as melhorias planejadas e sugestões abertas para contribuição. Sinta-se livre para implementar qualquer item!

### 🔵 Versões Futuras (v1.3.0+)

| Funcionalidade | Dificuldade | Descrição |
|----------------|-------------|-----------|
| **Gráficos no Dashboard** | Média | Integrar Chart.js para visualizar métricas ao longo do tempo |
| **Exportação de Relatórios** | Média | Gerar relatórios em PDF ou CSV com estatísticas de conteúdo |
| **Analytics de Vídeos** | Alta | Buscar métricas de views/likes dos vídeos postados via TikTok API |
| **Múltiplas Contas TikTok** | Alta | Gerenciar e rotacionar entre diferentes contas TikTok |
| **Editor Visual de Templates** | Alta | Interface drag-and-drop para criar novos templates de vídeo |
| **Agendamento Visual** | Média | Calendário de postagens no Dashboard |

### 🟢 Integrações Sugeridas

| Integração | Descrição |
|------------|-----------|
| **Instagram Reels** | Postar automaticamente no Instagram Reels além do TikTok |
| **YouTube Shorts** | Publicar vídeos como YouTube Shorts |
| **WhatsApp Business API** | Notificações via WhatsApp ao invés de Telegram |
| **Discord Webhook** | Notificações em canais Discord |
| **Google Sheets** | Exportar métricas automaticamente para planilha |

### 🟡 Melhorias de Qualidade

| Melhoria | Descrição |
|----------|-----------|
| **Testes Automatizados** | Adicionar pytest com cobertura para os módulos principais |
| **CI/CD Pipeline** | GitHub Actions para lint, testes e build automático |
| **Thumbnails Automáticos** | Gerar thumbnails atraentes com Pillow/DALL-E |
| **A/B Testing de Roteiros** | Testar diferentes estilos de humor e medir engajamento |
| **Transcrição Automática** | Gerar legendas via Whisper (OpenAI) para maior precisão |
| **Detecção de Tendências** | Buscar trending topics no Twitter/X ou Google Trends |

### 🔴 Melhorias de Infraestrutura

| Melhoria | Descrição |
|----------|-----------|
| **Autenticação no Dashboard** | Login/senha ou OAuth para proteger o painel |
| **Rate Limiting na API** | Limitar requisições para evitar abuso |
| **Suporte a PostgreSQL** | Migrar opcionalmente de SQLite para PostgreSQL |
| **Cache com Redis** | Cache de notícias e roteiros para reduzir requisições |
| **Healthcheck Avançado** | Monitoramento detalhado de cada módulo |

---

## 📞 Dúvidas?

Abra uma [issue](https://github.com/mgabrielramos/tiktok-automation/issues) com o label `question`.

---

**Obrigado por contribuir! 🎉**
