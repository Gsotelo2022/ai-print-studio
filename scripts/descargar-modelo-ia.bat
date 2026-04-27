@echo off
chcp 65001 >nul
color 0A

echo.
echo ╔════════════════════════════════════════════╗
echo ║     DESCARGAR MODELO IA (qwen2.5:1.5b)     ║
echo ║     Para Agente OLLAMA                     ║
echo ╚════════════════════════════════════════════╝
echo.

REM Verificar si OLLAMA está instalado
ollama --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: OLLAMA no está instalado
    echo.
    echo Descargar desde: https://ollama.com
    echo.
    pause
    exit /b 1
)

echo ✓ OLLAMA detectado
echo.
echo ⏳ Descargando modelo qwen2.5:1.5b...
echo    Esto puede tomar 3-5 minutos según tu conexión
echo    El archivo descargado será ~986 MB
echo.

ollama pull qwen2.5:1.5b

echo.
echo ✓ Modelo descargado exitosamente!
echo.
echo Ahora puedes ejecutar RUN.bat
echo.
pause
