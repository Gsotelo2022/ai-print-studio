@echo off
chcp 65001 >nul
color 0A

setlocal
cd /d "%~dp0"

echo ================================================
echo INICIANDO APP
echo ================================================

REM ---------- PYTHON ----------
echo [1] Python

if exist "database\source" (
    cd database\source

    if not exist ".venv" (
        echo Creando venv...
        python -m venv .venv
    )

    if exist ".venv\Scripts\activate.bat" (
        call .venv\Scripts\activate.bat
    )

    cd ..\..
) else (
    echo ERROR: No existe database\source
)

REM ---------- NODE ----------
echo [2] Node

if exist "frontend" (
    cd frontend
    if not exist node_modules npm install
    cd ..
) else (
    echo ERROR: no existe frontend
)

if exist "backend" (
    cd backend
    if not exist node_modules npm install
    cd ..
) else (
    echo ERROR: no existe backend
)

REM ---------- OLLAMA ----------
echo [3] Ollama

ollama --version >nul 2>&1
if %errorlevel%==0 (
    start cmd /k "ollama serve"
    timeout /t 5 >nul

    if exist "agentes-Ollama" (
        start cmd /k "cd agentes-Ollama && start-all-agentes.bat"
    )
)

REM ---------- SERVERS ----------
echo [4] Servidores

REM FastAPI
if exist "database\source" (
    start cmd /k "cd database\source && call .venv\Scripts\activate.bat && python -m uvicorn app_v2:app --reload --port 8000"
)

REM 🔥 BACKEND NODE (IMÁGENES IA)
if exist "backend" (
    start cmd /k "cd /d %cd%\backend && node server.js"
)

REM Frontend Vue
if exist "frontend" (
    start cmd /k "cd /d %cd%\frontend && npm run dev"
)

REM PHP
php -v >nul 2>&1
if %errorlevel%==0 (
    start cmd /k "cd /d %cd%\backend && php -S localhost:8080"
)

echo.
echo ================================================
echo TODO INICIADO
echo ================================================
echo Frontend: http://localhost:5173
echo IA Imagenes: http://localhost:3000
echo.

start http://localhost:5173

pause