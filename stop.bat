@echo off
chcp 65001 >nul
color 0C

REM ========================================
REM Script para DETENER todos los servidores
REM ========================================

echo.
echo ╔═══════════════════════════════════════════════╗
echo ║   DETENIENDO APLICACIÓN                      ║
echo ║   Prendete Rock - AI Print Studio            ║
echo ╚═══════════════════════════════════════════════╝
echo.

echo  ⏳ Deteniendo servidores...
echo.

REM Detener FastAPI (puerto 8000)
echo  • Deteniendo FastAPI Backend (puerto 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a >nul 2>&1
echo    ✓ FastAPI detenido

REM Detener Vue.js (puerto 5173)
echo  • Deteniendo Vue.js Frontend (puerto 5173)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173') do taskkill /F /PID %%a >nul 2>&1
echo    ✓ Vue.js detenido

REM Detener PHP (puerto 8080)
echo  • Deteniendo PHP Backend (puerto 8080)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080') do taskkill /F /PID %%a >nul 2>&1
echo    ✓ PHP detenido

REM Detener Agente Productos (puerto 5001)
echo  • Deteniendo Agente Productos (puerto 5001)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5001') do taskkill /F /PID %%a >nul 2>&1
echo    ✓ Agente Productos detenido

REM Detener Agente Precios (puerto 5002)
echo  • Deteniendo Agente Precios (puerto 5002)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5002') do taskkill /F /PID %%a >nul 2>&1
echo    ✓ Agente Precios detenido

REM Detener Agente BI (puerto 5003)
echo  • Deteniendo Agente BI (puerto 5003)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5003') do taskkill /F /PID %%a >nul 2>&1
echo    ✓ Agente BI detenido

REM Detener OLLAMA (puerto 11434)
echo  • Deteniendo OLLAMA (puerto 11434)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :11434') do taskkill /F /PID %%a >nul 2>&1
echo    ✓ OLLAMA detenido

echo.
echo  ⏳ Cerrando ventanas de terminal...
echo.

REM Cerrar ventanas cmd que ejecutan uvicorn (FastAPI)
echo  • Cerrando terminal FastAPI...
wmic process where "commandline like '%%uvicorn%%app_v2:app%%'" delete >nul 2>&1
echo    ✓ Terminal FastAPI cerrada

REM Cerrar ventanas cmd que ejecutan node server.js
echo  • Cerrando terminal Backend Node...
wmic process where "commandline like '%%node server.js%%'" delete >nul 2>&1
echo    ✓ Terminal Backend Node cerrada

REM Cerrar ventanas cmd que ejecutan npm run dev
echo  • Cerrando terminal Frontend Vue...
wmic process where "commandline like '%%npm%run%dev%%'" delete >nul 2>&1
wmic process where "commandline like '%%vite%%'" delete >nul 2>&1
echo    ✓ Terminal Frontend cerrada

REM Cerrar ventanas cmd que ejecutan PHP server
echo  • Cerrando terminal PHP...
wmic process where "commandline like '%%php -S%%'" delete >nul 2>&1
echo    ✓ Terminal PHP cerrada

REM Cerrar ventanas cmd de agentes Ollama
echo  • Cerrando terminales Agentes...
wmic process where "commandline like '%%agente_productos.py%%'" delete >nul 2>&1
wmic process where "commandline like '%%agente_precios.py%%'" delete >nul 2>&1
wmic process where "commandline like '%%start-all-agentes.bat%%'" delete >nul 2>&1
echo    ✓ Terminales Agentes cerradas

REM Cerrar ventana de OLLAMA serve
echo  • Cerrando terminal OLLAMA...
wmic process where "commandline like '%%ollama serve%%'" delete >nul 2>&1
echo    ✓ Terminal OLLAMA cerrada

REM Cerrar procesos node/python huérfanos
echo  • Limpiando procesos residuales...
taskkill /F /IM node.exe /FI "MEMUSAGE gt 2" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq python*" >nul 2>&1

echo.
echo ╔═══════════════════════════════════════════════╗
echo ║          ✅ APLICACIÓN DETENIDA              ║
echo ╚═══════════════════════════════════════════════╝
echo.
echo  Todos los servidores y terminales han sido cerrados.
echo  Puedes ejecutar RUN.bat para iniciar nuevamente.
echo.
pause
