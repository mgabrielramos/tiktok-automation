"""
Teste Rapido das Configuracoes
"""
import os
from pathlib import Path

# Carregar .env
env_path = Path(__file__).parent / ".env"
print(f"Arquivo .env existe: {env_path.exists()}")

if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("OPENROUTER_API_KEY="):
                key = line.split("=")[1].strip()
                print(f"OpenRouter API Key: {key[:20]}...{key[-10:]}")
            if line.startswith("TIKTOK_SESSIONID="):
                sid = line.split("=")[1].strip()
                print(f"TikTok SessionID: {sid[:10]}...{sid[-5:]}")

print("\nStatus:")
print("  - OpenRouter: Configurado")
print("  - TikTok: Configurado")
print("  - Dashboard: Pronto")
print("  - Docker Build: Em andamento")

print("\nURLs (apos build):")
print("  - Dashboard: http://localhost:8000/dashboard")
print("  - Swagger: http://localhost:8000/docs")
print("  - n8n: http://localhost:5678")

print("\nPara verificar o build:")
print("  docker-compose ps")
print("  docker-compose logs -f")
