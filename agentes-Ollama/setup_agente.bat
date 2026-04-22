@echo off
echo =========================
echo SETUP AGENTE IA (OLLAMA)
echo =========================

:: -------------------------
:: 1. Verificar Python
:: -------------------------
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python no está instalado o no está en PATH
    pause
    exit /b
)

:: -------------------------
:: 2. Crear entorno virtual
:: -------------------------
if not exist venv (
    echo Creando entorno virtual...
    python -m venv venv
)

:: -------------------------
:: 3. Activar entorno
:: -------------------------
call venv\Scripts\activate

:: -------------------------
:: 4. Actualizar pip
:: -------------------------
echo Actualizando pip...
python -m pip install --upgrade pip

:: -------------------------
:: 5. Instalar dependencias
:: -------------------------
echo Instalando dependencias...
pip install flask requests pyodbc

:: -------------------------
:: 6. Verificar Ollama
:: -------------------------
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Ollama no está instalado
    echo Descargar desde: https://ollama.com
    pause
    exit /b
)

:: -------------------------
:: 7. Descargar modelo liviano
:: -------------------------
echo Verificando modelo phi3:mini...
ollama pull phi3:mini

:: -------------------------
:: 8. Levantar Ollama
:: -------------------------
echo Iniciando servidor Ollama...
start "" ollama serve

timeout /t 3 > nul

:: -------------------------
:: 9. Levantar agente IA
:: -------------------------
echo Iniciando agente IA...
start "" cmd /k "call venv\Scripts\activate && python agente_productos.py"

echo =========================
echo AGENTE LISTO 🚀
echo Endpoint: http://localhost:5001/productos-ia
echo =========================

pause