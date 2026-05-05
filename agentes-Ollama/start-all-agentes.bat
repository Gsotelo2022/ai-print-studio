@echo off
chcp 65001 >nul
color 0A

echo Inciando agentes...

start "Agente Cupones" cmd /k "cd agente-cupones && call start-agente-descuentos.bat"
start "Agente Prompts"  cmd /k "cd agente-prompts  && call start-agente-prompts.bat"
start "Agente Pedidos"  cmd /k "cd agente-pedidos  && call start-agente-pedidos.bat"
