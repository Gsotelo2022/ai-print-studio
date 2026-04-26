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
echo ╔═══════════════════════════════════════════════╗
echo ║          ✅ APLICACIÓN DETENIDA              ║
echo ╚═══════════════════════════════════════════════╝
echo.
echo  Todos los servidores han sido detenidos.
echo  Puedes ejecutar RUN.bat para iniciar nuevamente.
echo.
pause
