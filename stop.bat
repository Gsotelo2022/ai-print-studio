@echo off
chcp 65001 >nul
color 0C

cd /d "%~dp0"

echo ========================================
echo DETENIENDO APLICACION
echo ========================================

echo Deteniendo por puertos: 8000(FastAPI) 5173(Vue)  3000(Node)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do taskkill /F /PID %%a >nul 2>&1

echo Deteniendo Agentes (5003, 5004 , 5005) y Ollama (11434)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5003') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5004') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5005') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :11434') do taskkill /F /PID %%a >nul 2>&1

echo Cerrando procesos por nombre...
powershell -NoProfile -Command "Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -like '*uvicorn*' }          | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
powershell -NoProfile -Command "Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -like '*node server.js*' }    | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
powershell -NoProfile -Command "Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -like '*npm*run*dev*' }        | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
powershell -NoProfile -Command "Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -like '*vite*' }              | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
powershell -NoProfile -Command "Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -like '*php*-S*' }            | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
powershell -NoProfile -Command "Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -like '*api_descuentos.py*'  } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
powershell -NoProfile -Command "Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -like '*agente_prompts.py*'  } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
powershell -NoProfile -Command "Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -like '*agente_pedidos.py*'  } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
powershell -NoProfile -Command "Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -like '*ollama*serve*' }      | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"

taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM ollama.exe >nul 2>&1

echo Cerrando consolas...
taskkill /F /FI "WINDOWTITLE eq Ollama*" /T >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Agente*" /T >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq FastAPI*" /T >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Node Backend*" /T >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq PHP Backend*" /T >nul 2>&1

echo.
echo ========================================
echo TODO DETENIDO CORRECTAMENTE
echo ========================================
echo.
pause
