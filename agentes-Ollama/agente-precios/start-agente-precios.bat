@echo off
title Agente IA - Precios (Puerto 5002)

echo ===============================================
echo  AGENTE IA - ACTUALIZACION DE PRECIOS
echo ===============================================
echo.
echo [1/3] Activando entorno virtual Python...

if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: No existe el entorno virtual .venv
    echo Ejecuta primero: python -m venv .venv
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

echo [2/3] Verificando dependencias...
echo - Flask
echo - Flask-CORS
echo - requests
echo - pyodbc
echo.

echo [3/3] Iniciando agente de precios en puerto 5002...
echo.
echo ===============================================
echo  AGENTE INICIADO
echo ===============================================
echo  URL: http://localhost:5002
echo  Endpoints:
echo    - POST /actualizar-precio (consulta en lenguaje natural)
echo    - GET /health (verificar estado)
echo.
echo  Ejemplos de uso:
echo    {"consulta": "cambiar precio del buzo a 15000"}
echo    {"detalle": "Buzo", "precio": 15000}
echo.
echo  Presiona Ctrl+C para detener
echo ===============================================
echo.

python agente_precios.py

pause
