"""
Script utilitário para obter SessionID do TikTok

Execute este script após fazer login no TikTok no seu navegador.
"""

import httpx
import asyncio


async def testar_sessionid(sessionid: str) -> bool:
    """Testa se um sessionid é válido"""
    
    headers = {
        "Cookie": f"sessionid={sessionid}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.tiktok.com/api/user/detail/",
                headers=headers,
                timeout=10,
            )
            
            if response.status_code == 200:
                print("✅ SessionID VÁLIDO!")
                return True
            else:
                print(f"❌ SessionID INVÁLIDO (status: {response.status_code})")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao testar: {e}")
        return False


def main():
    print("=" * 60)
    print("TIKTOK SESSIONID TESTER")
    print("=" * 60)
    print()
    
    print("Como obter seu SessionID:")
    print("1. Acesse https://www.tiktok.com e faça login")
    print("2. Pressione F12 para abrir Developer Tools")
    print("3. Vá em 'Application' > 'Cookies' > 'https://www.tiktok.com'")
    print("4. Encontre 'sessionid' e copie o valor")
    print()
    
    sessionid = input("Cole seu SessionID aqui: ").strip()
    
    if not sessionid:
        print("❌ SessionID não fornecido!")
        return
    
    print()
    print("Testando...")
    print()
    
    valido = asyncio.run(testar_sessionid(sessionid))
    
    print()
    print("=" * 60)
    
    if valido:
        print("✅ SessionID válido! Adicione ao seu .env:")
        print(f"TIKTOK_SESSIONID={sessionid}")
    else:
        print("❌ SessionID inválido ou expirado.")
        print("Obtenha um novo seguindo as instruções acima.")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
