@echo off
chcp 65001 >nul
color 0C

REM ========================================
REM Script para Detener Todos los Servidores
REM ========================================

cd /d "%~dp0"

echo.
echo ╔═══════════════════════════════════════════════╗
echo ║   DETENIENDO APLICACIÓN COMPLETA             ║
echo ║   Prendete Rock - AI Print Studio            ║
echo ╚═══════════════════════════════════════════════╝
echo.

echo Cerrando servidores...
echo ────────────────────────────────────────

REM Cerrar las ventanas de cmd por su título
REM Los títulos deben coincidir con los definidos en RUN.bat

echo   [X] Cerrando FastAPI Backend...
taskkill /FI "WindowTitle eq FastAPI Backend - http://127.0.0.1:8000" /F >nul 2>&1

echo   [X] Cerrando Vue Frontend...
taskkill /FI "WindowTitle eq Vue Frontend - http://localhost:5173" /F >nul 2>&1

echo   [X] Cerrando PHP Backend...
taskkill /FI "WindowTitle eq PHP Backend - http://localhost:8080" /F >nul 2>&1

echo   [X] Cerrando OLLAMA...
taskkill /FI "WindowTitle eq OLLAMA - http://localhost:11434" /F >nul 2>&1
taskkill /FI "WindowTitle eq OLLAMA Setup" /F >nul 2>&1

echo   [X] Cerrando Agente IA...
taskkill /FI "WindowTitle eq Agente IA - http://localhost:5001/productos-ia" /F >nul 2>&1

REM También intentar cerrar los procesos por nombre (método alternativo)
echo.
echo Cerrando procesos residuales...
echo ────────────────────────────────────────

REM Cerrar procesos de Node.js (Vite)
taskkill /IM node.exe /F >nul 2>&1
if %errorlevel% equ 0 (
    echo   [X] Procesos Node.js cerrados
) else (
    echo   [✓] No hay procesos Node.js activos
)

REM Cerrar procesos de Python (uvicorn/FastAPI)
taskkill /IM python.exe /F >nul 2>&1
if %errorlevel% equ 0 (
    echo   [X] Procesos Python cerrados
) else (
    echo   [✓] No hay procesos Python activos
)

REM Cerrar procesos de PHP
taskkill /IM php.exe /F >nul 2>&1
if %errorlevel% equ 0 (
    echo   [X] Procesos PHP cerrados
) else (
    echo   [✓] No hay procesos PHP activos
)

REM Cerrar procesos de OLLAMA
taskkill /IM ollama.exe /F >nul 2>&1
if %errorlevel% equ 0 (
    echo   [X] Procesos OLLAMA cerrados
) else (
    echo   [✓] No hay procesos OLLAMA activos
)

echo.
echo ╔═══════════════════════════════════════════════╗
echo ║          ✅ APLICACIÓN DETENIDA              ║
echo ╚═══════════════════════════════════════════════╝
echo.
echo Todos los servidores han sido cerrados.
echo.

timeout /t 3 /nobreak >nul
exit
