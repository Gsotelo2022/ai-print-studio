@echo off
REM Script para iniciar el servidor FastAPI de registro de usuarios
REM 

echo =========================================
echo Iniciando servidor FastAPI
echo =========================================

cd /d "c:\projects\ai-print-studio\database\source"

echo.
echo Verificando que la BD PrendeteRock exista...
powershell -Command "Get-Date -Format 'HH:mm:ss'"

REM Activar el environment si existe
if exist ".\.venv\Scripts\activate.bat" (
    call .\.venv\Scripts\activate.bat
    echo ✓ Virtual environment activado
) else (
    echo ⚠ Virtual environment no encontrado en .\.venv
)

echo.
echo Iniciando FastAPI en http://127.0.0.1:8000
echo.
echo Presiona CTRL+C para detener el servidor
echo.

python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000

pause
