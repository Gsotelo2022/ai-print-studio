@echo off
echo ================================================
echo   AGENTE DE DESCUENTOS - PRENDETE ROCK
echo ================================================
echo.

cd /d "%~dp0"

echo [1/3] Activando entorno virtual...
call ..\.venv\Scripts\activate.bat

echo.
echo [2/3] Verificando dependencias...
pip install -r requirements.txt --quiet

echo.
echo [3/3] Iniciando API de Descuentos en puerto 5003...
echo.
echo ================================================
echo   API: http://localhost:5003
echo   Docs: http://localhost:5003/docs
echo ================================================
echo.

uvicorn api_descuentos:app --host 0.0.0.0 --port 5003 --reload

pause
