@echo off
REM =============================================================================
REM SCRIPT DE INICIALIZAÇÃO - TIKTOK AUTOMATION (Windows)
REM =============================================================================

echo ╔════════════════════════════════════════════════════════╗
echo ║     TIKTOK AUTOMATION - Script de Inicializacao       ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Verifica Docker
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Docker nao encontrado! Instale o Docker Desktop.
    pause
    exit /b 1
)

REM Verifica docker-compose
where docker-compose >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] docker-compose nao encontrado!
    pause
    exit /b 1
)

echo [INFO] Docker: %docker --version%
echo.

REM Verifica .env
if not exist ".env" (
    echo [AVISO] Arquivo .env nao encontrado!
    
    if exist ".env.example" (
        echo [INFO] Criando .env a partir do exemplo...
        copy .env.example .env
        echo [OK] .env criado!
        echo.
        echo [AVISO] EDITE O ARQUIVO .env E CONFIGURE:
        echo    - OPENROUTER_API_KEY
        echo    - TIKTOK_SESSIONID
        echo    - N8N_HOST
        echo.
        pause
    ) else (
        echo [ERRO] .env.example nao encontrado!
        pause
        exit /b 1
    )
)

echo [INFO] Verificando configuracoes...

REM Carrega .env
for /f "tokens=1,* delims==" %%a in (.env) do (
    if "%%a"=="OPENROUTER_API_KEY" set "OPENROUTER_API_KEY=%%b"
    if "%%a"=="TIKTOK_SESSIONID" set "TIKTOK_SESSIONID=%%b"
)

if "%OPENROUTER_API_KEY%"=="" (
    echo [AVISO] OPENROUTER_API_KEY nao configurada
) else (
    echo [OK] OpenRouter API configurada
)

if "%TIKTOK_SESSIONID%"=="" (
    echo [AVISO] TIKTOK_SESSIONID nao configurada
) else (
    echo [OK] TikTok SessionID configurado
)

echo.
echo [INFO] Parando servicos existentes...
docker-compose down 2>nul

echo [INFO] Build das imagens...
docker-compose build

echo.
echo [INFO] Iniciando servicos...
docker-compose up -d

echo.
echo [OK] Servicos iniciados!
echo.

REM Aguarda
timeout /t 10 /nobreak >nul

echo [INFO] Status dos containers:
docker-compose ps

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║           INICIALIZACAO CONCLUIDA!                    ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo Servicos disponiveis:
echo    - API de Automacao: http://localhost:8000
echo    - n8n Workflow:     http://localhost:5678
echo    - Swagger Docs:     http://localhost:8000/docs
echo.
echo Para ver logs: docker-compose logs -f
echo Para parar:    docker-compose down
echo.

pause
