# 🎨 Guia de Customização de Templates

> Personalize os templates de humor para criar vídeos únicos!

---

## 📝 Entendendo os Templates

Os templates são estruturas pré-definidas que guiam a IA na criação de roteiros.

### Estrutura de um Template

```python
{
    "name": "Nome do Template",
    "hook": "🎭 Frase de impacto inicial",
    "style": "estilo_do_template",
    "tone": "tom_de_voz",
}
```

---

## 🎭 Templates Incluídos

### 1. Ironia da Realidade

```python
{
    "name": "Ironia da Realidade",
    "hook": "🎭 VOCÊ NÃO VAI ACREDITAR!",
    "style": "irônico",
    "tone": "sarcástico",
}
```

**Exemplo de uso:**
```
🎭 VOCÊ NÃO VAI ACREDITAR!

📰 Ministério anuncia que brasileiro agora precisa de 
   37 formulários para tirar RG

😂 É... meus amigos, a realidade superou a ficção de 
   novo! Enquanto isso nos comentários: "mas que país 
   é esse?" 😂
```

### 2. Pergunta Retórica

```python
{
    "name": "Pergunta Retórica",
    "hook": "🤔 SÉRIO ISSO MESMO?",
    "style": "questionador",
    "tone": "incrédulo",
}
```

### 3. Comparação Engraçada

```python
{
    "name": "Comparação Engraçada",
    "hook": "😂 ISSO AÍ É TIPO...",
    "style": "comparativo",
    "tone": "descontraído",
}
```

### 4. Plot Twist

```python
{
    "name": "Plot Twist",
    "hook": "🎬 PLOT TWIST DO ANO!",
    "style": "narrativo",
    "tone": "surpreso",
}
```

### 5. Reação Exagerada

```python
{
    "name": "Reação Exagerada",
    "hook": "🚨 ALERTA DE NOTÍCIA BIZARRA!",
    "style": "reativo",
    "tone": "exagerado",
}
```

---

## ✏️ Como Criar Seus Templates

### Passo 1: Edite o config.py

Abra `src/config.py` e localize:

```python
humor_templates: List[dict] = [
    # Seus templates aqui
]
```

### Passo 2: Adicione Novo Template

```python
{
    "name": "Seu Template",
    "hook": "🎯 Sua frase de impacto",
    "style": "seu_estilo",
    "tone": "seu_tom",
}
```

### Passo 3: Atualize o Prompt da IA

Em `src/modules/ia_generator.py`, edite `_criar_system_prompt()`:

```python
def _criar_system_prompt(self, template: Optional[str] = None) -> str:
    base_prompt = """..."""
    
    # Adicione instruções específicas para seu template
    if template == "Seu Template":
        base_prompt += """
        
        TEMPLATE ESPECIAL - SEU TEMPLATE:
        - Use comparações com situações do dia a dia
        - Inclua referências à cultura pop brasileira
        - Termine com uma pergunta retórica
        """
    
    return base_prompt
```

---

## 🎯 Estilos de Humor Disponíveis

| Estilo | Descrição | Exemplo |
|--------|-----------|---------|
| `irônico` | Contraste entre expectativa e realidade | "Que ótimo, mais burocracia!" |
| `sarcástico` | Ironia ácida | "Claro, porque precisávamos disso" |
| `absurdo` | Exagero cômico | "É tipo tentar voar batendo os braços" |
| `auto-depreciativo` | Humor sobre si mesmo | "Eu que sou velho pra essas coisas" |
| `observacional` | Observações do cotidiano | "Repareu que todo mundo...?" |
| `sátira` | Crítica social disfarçada | "Nosso governo é eficiente... ledo engano" |

---

## 🎤 Tons de Voz

| Tom | Uso | Palavras-chave |
|-----|-----|----------------|
| `sarcástico` | Notícias absurdas | "claro", "óbvio", "perfeito" |
| `incrédulo` | Fatos surpreendentes | "sério?", "como assim?" |
| `descontraído` | Notícias leves | "galera", "pessoal", "vem cá" |
| `surpreso` | Plot twists | "não acredito!", "olha isso!" |
| `exagerado` | Notícias bizarras | "INCRÍVEL", "BIZARRO", "ABSURDO" |
| `cansado` | Burocracias | "lá vamos nós", "de novo não" |

---

## 📋 Templates Prontos para Copiar

### Template "Brasileiro Sofredor"

```python
{
    "name": "Brasileiro Sofredor",
    "hook": "🇧🇷 SÓ NO BRASIL MESMO!",
    "style": "auto-depreciativo",
    "tone": "conformado_engraçado",
}
```

**Prompt adicional:**
```
TEMPLATE - BRASILEIRO SOFREDOR:
- Comece com "Só no Brasil mesmo!"
- Compare com "países normais"
- Use "a gente aceita" como punchline
- Termine com "mas a gente ama esse país"
```

### Template "Millennial Cansado"

```python
{
    "name": "Millennial Cansado",
    "hook": "😩 A GENTE SÓ QUERIA VIVER",
    "style": "geracional",
    "tone": "cansado_mas_engraçado",
}
```

**Prompt adicional:**
```
TEMPLATE - MILLENNIAL CANSADO:
- Referências a "quando éramos crianças"
- Compare expectativas vs realidade adulta
- Use "ninguém me preparou pra isso"
- Mencione "ansiedade" de forma humorística
```

### Template "Tio do Pavê"

```python
{
    "name": "Tio do Pavê",
    "hook": "👴 NA MINHA ÉPOCA...",
    "style": "nostálgico",
    "tone": "saudosista_engraçado",
}
```

**Prompt adicional:**
```
TEMPLATE - TIO DO PAVÊ:
- Comece com "Na minha época era melhor"
- Compare "antigamente" com "hoje em dia"
- Use "isso não vai dar certo"
- Termine com "mas sou eu que sou velho"
```

### Template "Zoomer Confuso"

```python
{
    "name": "Zoomer Confuso",
    "hook": "💀 NÃO FAZ SENTIDO ALGUM",
    "style": "geracional",
    "tone": "confuso_cômico",
}
```

**Prompt adicional:**
```
TEMPLATE - ZOOMER CONFUSO:
- Use gírias: "cringe", "mid", "nah"
- Expressões de confusão: "?????", "help"
- Compare com "faz 5 minutos atrás"
- Termine com "estou velho aos 20"
```

---

## 🔄 Rotação de Templates

O sistema automaticamente rotaciona templates. Para forçar um template específico:

### Via API

```bash
curl -X POST http://localhost:8000/api/generate-roteiro \
  -H "Content-Type: application/json" \
  -d '{
    "noticia": {...},
    "template": "Nome do Template"
  }'
```

### No Código

```python
resultado = await ia_generator.gerar_roteiro(
    noticia_titulo="...",
    template="Brasileiro Sofredor",  # Template específico
)
```

---

## 📊 Testando Templates

### Script de Teste

Crie `scripts/test_templates.py`:

```python
import asyncio
from src.modules.ia_generator import IAGenerator

async def test_templates():
    generator = IAGenerator()
    
    templates = [
        "Ironia da Realidade",
        "Pergunta Retórica",
        "Brasileiro Sofredor",
    ]
    
    for template in templates:
        print(f"\n=== Testando: {template} ===\n")
        
        resultado = await generator.gerar_roteiro(
            noticia_titulo="Teste de template",
            noticia_descricao="Descrição de teste",
            template=template,
        )
        
        print(resultado.get("roteiro_completo", "Erro"))
        print("-" * 50)

asyncio.run(test_templates())
```

---

## 🎨 Dicas de Ouro

### 1. Hooks Matadores

Os primeiros 3 segundos são cruciais:

```
✅ BOM: "🚨 ALERTA DE NOTÍCIA BIZARRA!"
❌ RUIM: "Aqui está uma notícia"

✅ BOM: "🎭 VOCÊ NÃO VAI ACREDITAR!"
❌ RUIM: "Vou contar uma coisa"
```

### 2. Call-to-Action Eficazes

```
✅ "Comenta aí qual sua opinião!"
✅ "Marca aquele amigo que..."
✅ "Quem mais é assim?"
✅ "Salva pra não esquecer!"
```

### 3. Hashtags Estratégicas

```
Sempre use:
#humor #noticias #brasil

Adicione por tema:
#politica #economia #tecnologia #futebol

Trending (verifique no TikTok):
#viral #fyp #paravoce
```

---

## 📈 Analytics de Templates

Monitore qual template performa melhor:

```python
# Adicione tracking no seu código
template_stats = {
    "Ironia da Realidade": {"views": 0, "likes": 0},
    "Pergunta Retórica": {"views": 0, "likes": 0},
}
```

---

## 🔗 Recursos Adicionais

- **TikTok Creative Center:** https://www.tiktok.com/creativecenter/
- **Trending Hashtags:** https://tokboard.com/
- **Script Analytics:** (futuro)

---

**Agora é só criar e viralizar! 🚀**
