@echo off
echo ========================================
echo AGENTE IA - ACTUALIZACION DE PRECIOS
echo ========================================
echo.

:: Verificar que existe el entorno virtual
if not exist venv (
    echo ERROR: No existe entorno virtual
    echo Ejecuta primero setup_agente.bat
    pause
    exit /b
)

:: Activar entorno virtual
call venv\Scripts\activate

:: Verificar que Ollama está corriendo
echo Verificando Ollama...
curl -s http://localhost:11434/api/version >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ============================================
    echo ADVERTENCIA: Ollama no esta corriendo
    echo ============================================
    echo Inicia Ollama con: ollama serve
    echo El agente usara fallback sin IA
    echo ============================================
    echo.
    timeout /t 3 >nul
)

:: Iniciar agente
echo.
echo Iniciando agente de precios en puerto 5002...
echo.
python agente_precios.py

pause
