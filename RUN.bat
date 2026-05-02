@echo off
chcp 65001 >nul
color 0A

cd /d "%~dp0"

echo ================================================
echo INICIANDO AI PRINT STUDIO
echo ================================================

REM ---------- DEPENDENCIAS ----------

REM Crear entorno virtual si no existe
if not exist "backend\api_python\.venv" (
    echo [Python] Creando venv...
    python -m venv backend\api_python\.venv
)

REM Instalar dependencias Python (SIEMPRE importante)
echo [Python] Instalando dependencias...
cd backend\api_python
call .venv\Scripts\activate.bat

if exist requirements.txt (
    pip install -r requirements.txt
) else (
    echo ⚠️ No existe requirements.txt → instalando mínimo necesario
    pip install fastapi uvicorn psycopg2-binary python-dotenv
)

cd ..\..

REM Node frontend
if not exist "frontend\node_modules" (
    echo [Node] Instalando frontend...
    cd frontend && call npm install && cd ..
)

REM Node backend
if not exist "backend\node_modules" (
    echo [Node] Instalando backend...
    cd backend && call npm install && cd ..
)

REM ---------- OLLAMA ----------
echo [Iniciando IA] Ollama
ollama --version >nul 2>&1
if %errorlevel%==0 (
    start "Ollama" cmd /k "ollama serve"
)

REM ---------- SERVIDORES ----------
echo [Iniciando Servidores] FastAPI, Node y PHP

REM FastAPI (con debug)
start "FastAPI Backend" cmd /k "cd backend\api_python && call .venv\Scripts\activate.bat && python -m uvicorn app_v2:app --reload --port 8000 || pause"

REM Node Backend
start "Node Backend" cmd /k "cd backend && node server.js"

REM PHP Backend (opcional)
php -v >nul 2>&1 
if %errorlevel%==0 (
    start "PHP Backend" cmd /k "cd backend && php -S localhost:8080"
)

REM Frontend Vue
start "Vue Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ================================================
echo TODO INICIADO
echo Frontend: http://localhost:5173
echo FastAPI: http://localhost:8000/docs
echo ================================================
echo.

start http://localhost:5173

pause