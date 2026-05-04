@echo off
chcp 65001 >nul
color 0A
echo Iniciando Agente de Prompts (puerto 5004)...
if not exist .venv python -m venv .venv
call .venv\Scripts\activate.bat
pip install -r requirements.txt 2>nul
python agente_prompts.py
pause