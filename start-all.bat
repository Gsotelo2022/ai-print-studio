@echo off
chcp 65001 >nul
color 0B

echo.
echo ========================================
echo    Iniciando TODOS los Servidores
echo ========================================
echo.

REM Verificar si las dependencias están instaladas
echo Verificando dependencias...
cd database\source
python -c "import uvicorn" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [!] Dependencias faltantes. Instalando...
    echo.
    call ..\env\Scripts\activate.bat
    python -m pip install -r requirements.txt >nul 2>&1
    echo [✓] Dependencias Python instaladas
)
cd ..\..

if not exist "frontend\node_modules" (
    echo.
    echo [!] Dependencias Node.js faltantes. Instalando...
    echo.
    cd frontend
    call npm install >nul 2>&1
    echo [✓] Dependencias Node.js instaladas
    cd ..
)

echo.
echo ========================================
echo Iniciando servidores...
echo ========================================
echo.

REM Iniciar servidor FastAPI
echo [1/2] Abriendo servidor FastAPI...
start "FastAPI Backend" powershell -NoExit -Command "Set-Location '%CD%'; & '.\start-backend.ps1'"

REM Esperar un poco
timeout /t 3 /nobreak >nul

REM Iniciar servidor Vue
echo [2/2] Abriendo servidor Vue.js...
start "Vue Frontend" powershell -NoExit -Command "Set-Location '%CD%'; & '.\start-frontend.ps1'"

echo.
echo ========================================
echo Ambos servidores estan iniciando...
echo ========================================
echo.
echo FastAPI (Backend):  http://127.0.0.1:8000
echo Vue.js (Frontend):  http://localhost:5173
echo.
echo Cierra las ventanas para detener los servidores.
echo.
