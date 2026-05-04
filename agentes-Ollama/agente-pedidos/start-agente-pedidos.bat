@echo off
chcp 65001 >nul
color 0A

echo ===============================
echo 🤖 Iniciando Agente de Pedidos
echo ===============================

echo.

REM Crear entorno virtual si no existe
if not exist .venv (
    echo 📦 Creando entorno virtual...
    python -m venv .venv
)

REM Activar entorno
call .venv\Scripts\activate.bat

echo.
echo 🔍 Verificando dependencias...

REM Verificar si pyodbc está instalado
python -c "import pyodbc" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ pyodbc no encontrado. Instalando dependencias...
    pip install -r requirements.txt
) else (
    echo ✅ pyodbc ya está instalado
)

echo.
echo 🚀 Iniciando servidor...
echo Endpoint: http://localhost:5005/chat
echo Health:   http://localhost:5005/health
echo.

python agente_pedidos.py

pause