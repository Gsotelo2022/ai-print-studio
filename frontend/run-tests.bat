@echo off
:: ============================================
:: SCRIPT PARA EJECUTAR TESTS DE PEDIDO
:: AI Print Studio
:: ============================================

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║  🧪 AI Print Studio - Test de Flujo de Pedido            ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

:: Verificar si Node.js está instalado
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Error: Node.js no está instalado
    echo.
    echo Por favor instala Node.js desde: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo ✅ Node.js instalado
node --version
echo.

:: Verificar si node-fetch está instalado
if not exist "node_modules\node-fetch" (
    echo ⚠️ node-fetch no está instalado
    echo.
    echo 📦 Instalando dependencias...
    call npm install
    echo.
)

:: Verificar si el backend está corriendo
echo 🔍 Verificando que el backend esté corriendo...
curl http://localhost:8000/api/health >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ❌ Error: El backend no está corriendo en http://localhost:8000
    echo.
    echo Por favor inicia el backend antes de ejecutar los tests:
    echo    python database\source\app_v2.py
    echo.
    pause
    exit /b 1
)

echo ✅ Backend está activo
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

:: Ejecutar los tests
echo 🚀 Ejecutando tests...
echo.
node tests\order-flow.test.js

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

if %errorlevel% equ 0 (
    echo ✅ Tests completados exitosamente
) else (
    echo ❌ Tests fallaron
)

echo.
pause
