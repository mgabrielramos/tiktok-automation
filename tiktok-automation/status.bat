@echo off
echo ============================================
echo TikTok Automation - Build Status
echo ============================================
echo.

cd /d "%~dp0"

echo Verificando status dos containers...
docker-compose ps

echo.
echo ============================================
echo Verificando imagens...
echo ============================================
docker images | findstr tiktok

echo.
echo ============================================
echo Ultimos logs...
echo ============================================
docker-compose logs --tail=20

echo.
echo ============================================
echo Para acompanhar em tempo real:
echo   docker-compose logs -f
echo ============================================

pause
