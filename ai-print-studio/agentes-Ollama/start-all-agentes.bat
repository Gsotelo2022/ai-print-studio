@echo off
chcp 65001 >nul
color 0A

echo.
echo ╔═══════════════════════════════════════════════╗
echo ║   INICIANDO AGENTES IA                       ║
echo ║   Sistema modular de agentes con OLLAMA      ║
echo ╚═══════════════════════════════════════════════╝
echo.

REM Activar entorno virtual
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo ✓ Entorno virtual activado
) else (
    echo ❌ Error: No se encontró el entorno virtual
    echo    Ejecuta: python -m venv .venv
    pause
    exit /b 1
)

echo.
echo 🚀 Iniciando agentes en puertos independientes...
echo.

REM Agente 1: Productos (puerto 5001)
start "Agente Productos - http://localhost:5001" cmd /k "color 0B && python agente_productos.py"
echo    [✓] Agente Productos --------- http://localhost:5001

timeout /t 1 /nobreak >nul

REM Agente 2: Precios (puerto 5002)
start "Agente Precios - http://localhost:5002" cmd /k "color 0E && python agente_precios.py"
echo    [✓] Agente Precios ----------- http://localhost:5002

timeout /t 1 /nobreak >nul

echo ╔═══════════════════════════════════════════════╗
echo ║   ✅ TODOS LOS AGENTES INICIADOS             ║
echo ╚═══════════════════════════════════════════════╝
echo.
echo  Los agentes están corriendo en ventanas separadas.
echo  Usa stop.bat para detenerlos.
echo.
