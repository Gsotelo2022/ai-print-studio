@echo off
echo Iniciando Agente de Productos IA en puerto 5001...
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python agente_productos.py
pause
