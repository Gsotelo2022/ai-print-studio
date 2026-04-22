@echo off
chcp 65001 >nul
color 0A

REM ========================================
REM Script Maestro - Levanta la Aplicación
REM ========================================

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ╔═══════════════════════════════════════════════╗
echo ║   INICIANDO APLICACIÓN COMPLETA              ║
echo ║   Prendete Rock - AI Print Studio            ║
echo ║   [Un clic para todo]                        ║
echo ╚═══════════════════════════════════════════════╝
echo.

REM ========================================
REM [1] VERIFICAR Y INSTALAR PYTHON
REM ========================================
echo.
echo [1] Verificando dependencias Python...
echo ──────────────────────────────────────────────
cd database\source

REM Crear entorno virtual si no existe
if not exist ".\.venv" (
    echo   ⚠ Creando entorno virtual...
    python -m venv .venv
    echo   ✓ Entorno virtual creado
)

REM Activar environment
if exist ".\.venv\Scripts\activate.bat" (
    call .\.venv\Scripts\activate.bat >nul 2>&1
    echo   ✓ Virtual environment activado
) else (
    echo   ⚠ No se encontró .venv, usando Python global
)

REM Verificar si todas las dependencias están instaladas
python -c "import uvicorn, pyodbc, PIL, rembg" >nul 2>&1
if errorlevel 1 (
    echo   ⚠ Instalando dependencias desde requirements.txt...
    python -m pip install -q --upgrade pip 2>nul
    python -m pip install -q -r requirements.txt 2>nul
    echo   ✓ Dependencias Python instaladas
) else (
    echo   ✓ Dependencias Python OK
)

cd ..\..\

REM ========================================
REM [2] VERIFICAR Y INSTALAR NODE.JS
REM ========================================
echo.
echo [2] Verificando dependencias Node.js...
echo ────────────────────────────────────────

if not exist "frontend\node_modules" (
    echo   ⚠ Instalando dependencias Node.js ^(primera vez^)...
    echo.
    cd frontend
    call npm install --silent 2>nul
    echo   ✓ Dependencias Node.js instaladas
    cd ..
) else (
    echo   ✓ Dependencias Node.js OK
)

REM ========================================
REM [3] VERIFICAR PHP Y COMPOSER (Mercado Pago)
REM ========================================
echo.
echo [3] Verificando PHP y Composer...
echo ────────────────────────────────────────

php -v >nul 2>&1
if errorlevel 1 (
    echo   ⚠ PHP no detectado ^(Mercado Pago puede no funcionar^)
    set PHP_AVAILABLE=0
) else (
    echo   ✓ PHP detectado
    set PHP_AVAILABLE=1
    
    if not exist "backend\vendor" (
        echo   ⚠ Instalando Composer packages...
        cd backend
        call composer install --quiet 2>nul
        echo   ✓ Dependencias PHP instaladas
        cd ..
    ) else (
        echo   ✓ Dependencias PHP OK
    )
)

REM ========================================
REM [3B] VERIFICAR OLLAMA Y AGENTE IA
REM ========================================
echo.
echo [3B] Verificando Agente IA ^(OLLAMA^)...
echo ────────────────────────────────────────

ollama --version >nul 2>&1
if errorlevel 1 (
    echo   ⚠ OLLAMA no detectado
    echo   └─ Descargar desde: https://ollama.com
    set OLLAMA_AVAILABLE=0
) else (
    echo   ✓ OLLAMA detectado
    set OLLAMA_AVAILABLE=1
    
    REM Verificar si OLLAMA está corriendo en puerto 11434
    netstat -ano | findstr "11434" >nul 2>&1
    if errorlevel 1 (
        echo   ⚠ OLLAMA no está corriendo, será levantado automáticamente
        set OLLAMA_RUNNING=0
    ) else (
        echo   ✓ OLLAMA ya está corriendo ^(puerto 11434^)
        set OLLAMA_RUNNING=1
    )
    
    if not exist "agentes-Ollama\.venv\Scripts\activate.bat" (
        echo   ⚠ Configurando entorno virtual del agente...
        cd agentes-Ollama
        python -m venv .venv
        call .\.venv\Scripts\activate.bat
        python -m pip install -q flask requests pyodbc flask-cors >nul 2>&1
        echo   ✓ Agente IA configurado
        cd ..
    ) else (
        echo   ✓ Agente IA ya configurado
    )
    
    REM Verificar que el modelo qwen2.5:1.5b esté descargado
    echo   ⏳ Verificando modelo qwen2.5:1.5b...
    ollama list | findstr "qwen2.5:1.5b" >nul 2>&1
    if errorlevel 1 (
        echo   ⚠ Modelo qwen2.5:1.5b no descargado
        echo   └─ Se descargará automáticamente ^(primera ejecución, puede tardar^)
        set MODELO_MISSING=1
    ) else (
        echo   ✓ Modelo qwen2.5:1.5b encontrado
        set MODELO_MISSING=0
    )
)

REM ========================================
REM [4] MOSTRAR CONFIGURACION
REM ========================================
echo.
echo [4] Configuración del Proyecto:
echo ────────────────────────────────────────

echo.
echo   BASE DE DATOS:
echo   ├─ Servidor: SQLEXPRESS01
echo   ├─ BD: PrendeteRock
echo   └─ Pool: SQL Server (Windows Auth)
echo.
echo   SERVIDORES A INICIAR:
echo   ├─ FastAPI Backend ........... http://127.0.0.1:8000
echo   │  └─ Registro, Login, Órdenes, Pagos
echo   ├─ Agente IA ^(OLLAMA^) ........ http://localhost:5001
echo   │  ├─ Consulta SQL → OLLAMA → JSON agrupado
echo   │  └─ TODOS los productos ^(85 en BD PrendeteRock^)
echo   ├─ Vue.js Frontend ........... http://localhost:5173
echo   │  └─ Interfaz de Usuario
echo   └─ PHP Backend ^(Mercado Pago^) http://localhost:8080
echo      └─ Procesamiento de pagos
echo.
echo   DATOS DE PRUEBA:
echo   ├─ Email: cliente@test.com    Pwd: password123
echo   └─ Email: admin@test.com      Pwd: password123
echo.

REM ========================================
REM [5] LEVANTAR SERVIDORES (4-5 ventanas)
REM ========================================
echo.
echo [5] Iniciando servidores...
echo ────────────────────────────────────────
echo.

REM ─────────────────────────────────────────
REM Server 1: FastAPI Backend (CRÍTICO)
REM ─────────────────────────────────────────
echo   [►] Iniciando FastAPI Backend...
start "FastAPI Backend - http://127.0.0.1:8000" cmd /k ^
    "cd /d ""%cd%\database\source"" && python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

REM ─────────────────────────────────────────
REM Server 1B: OLLAMA (si está instalado y no corre)
REM ─────────────────────────────────────────
if %OLLAMA_AVAILABLE% equ 1 (
    if %OLLAMA_RUNNING% equ 0 (
        echo   [►] Inicializando OLLAMA ^(modelo: qwen2.5:1.5b^)...
        
        REM Si el modelo no está descargado, descargarlo
        if %MODELO_MISSING% equ 1 (
            echo   ⏳ Descargando modelo qwen2.5:1.5b ^(primera vez, esto toma tiempo^)...
            start "OLLAMA Setup" cmd /k ^
                "ollama pull qwen2.5:1.5b && ollama serve"
            timeout /t 5 /nobreak >nul
        ) else (
            start "OLLAMA - http://localhost:11434" cmd /k ^
                "ollama serve"
        )
        echo   ⏳ Esperando que OLLAMA cargue completamente...
        echo      ^(Esto puede tardar 20-40 seg en i3, verificar ventana OLLAMA^)
        timeout /t 20 /nobreak >nul
        echo   ✓ OLLAMA listo ^(si no responde, el agente usará fallback^)
    ) else (
        echo   ✓ OLLAMA ya estaba corriendo
    )
)

REM ─────────────────────────────────────────
REM Server 1C: Agente IA ^(OLLAMA^)
REM ─────────────────────────────────────────
if %OLLAMA_AVAILABLE% equ 1 (
    echo   [►] Iniciando Agente IA ^(Python + OLLAMA^)...
    echo      • Consulta BD SQL Server ^(PrendeteRock^)
    echo      • Procesa con qwen2.5:1.5b
    echo      • Procesando TODOS los productos ^(85 en BD^)
    start "Agente IA - http://localhost:5001/productos-ia" cmd /k ^
        "cd /d ""%cd%\agentes-Ollama"" && call .\.venv\Scripts\activate.bat && python agente_productos.py"
    timeout /t 3 /nobreak >nul
    echo   ✓ Agente IA iniciado
)

timeout /t 1 /nobreak >nul

REM ─────────────────────────────────────────
REM Server 2: Vue.js Frontend
REM ─────────────────────────────────────────
echo   [►] Iniciando Vue.js Frontend...
start "Vue Frontend - http://localhost:5173" cmd /k ^
    "cd /d ""%cd%\frontend"" && npm run dev"

timeout /t 2 /nobreak >nul

REM ─────────────────────────────────────────
REM Server 3: PHP Backend (Opcional, Mercado Pago)
REM ─────────────────────────────────────────
if %PHP_AVAILABLE% equ 1 (
    echo   [►] Iniciando PHP Backend...
    start "PHP Backend - http://localhost:8080" cmd /k ^
        "cd /d ""%cd%\backend"" && php -S localhost:8080"
) else (
    echo   [⚠] PHP no detectado - Mercado Pago no funcionará
)

REM ========================================
REM [6] RESUMEN FINAL
REM ========================================
echo.
echo ╔═══════════════════════════════════════════════╗
echo ║          ✅ APLICACIÓN INICIADA              ║
echo ╠═══════════════════════════════════════════════╣
echo ║                                               ║
echo ║  Se abrieron 4-5 ventanas automáticamente:   ║
echo ║                                               ║
echo ║  ① FastAPI Backend                            ║
echo ║     http://127.0.0.1:8000                    ║
echo ║     ✓ Login, Registro, Pedidos               ║
echo ║     ✓ Generación de imágenes con IA          ║
echo ║     ✓ Procesamiento de órdenes               ║
echo ║                                               ║
echo ║  ② OLLAMA ^(Backend IA^)                       ║
echo ║     http://localhost:11434                   ║
echo ║     ✓ Motor de IA con modelo qwen2.5:1.5b    ║
echo ║     ✓ Se inicia automáticamente              ║
echo ║                                               ║
echo ║  ③ Agente IA ^(Productos dinámicos^)          ║
echo ║     http://localhost:5001/productos-ia       ║
echo ║     ✓ Consulta BD SQL Server                 ║
echo ║     ✓ Procesa con OLLAMA qwen2.5:1.5b        ║
echo ║     ✓ Agrupa por producto/talle/color        ║
echo ║     ✓ Procesando TODOS los productos ^(85^)  ║
echo ║                                               ║
echo ║  ④ Vue.js Frontend ^(ABRE AQUÍ^)              ║
echo ║     http://localhost:5173                    ║
echo ║     ✓ Interfaz de usuario web                ║
echo ║     ✓ Formularios y galería                  ║
echo ║     ✓ Carrito de compras                     ║
echo ║                                               ║
echo ║  ⑤ PHP Backend ^(si PHP está disponible^)     ║
echo ║     http://localhost:8080                    ║
echo ║     ✓ Integración Mercado Pago               ║
echo ║     ✓ Procesamiento de pagos                 ║
echo ║                                               ║
echo ║  PRÓXIMO PASO:                                ║
echo ║  └─ El navegador se abrirá automáticamente   ║
echo ║     en: http://localhost:5173                ║
echo ║                                               ║
echo ║  BASE DE DATOS:                               ║
echo ║  └─ SQL Server PrendeteRock                  ║
echo ║                                               ║
echo ║  PARA DETENER: Ejecuta stop.bat              ║
echo ║                                               ║
echo ║  CIRCUITO COMPLETO:                           ║
echo ║  Frontend → Agente IA → BD SQL Server        ║
echo ║           ↓                                   ║
echo ║         OLLAMA procesa → JSON agrupado       ║
echo ║           ↓                                   ║
echo ║  Mostrar productos/talles/colores            ║
echo ║                                               ║
echo ║  IMPORTANTE:                                  ║
echo ║  └─ 1era vez: OLLAMA descarga qwen2.5:1.5b   ║
echo ║     ^(~986MB, tarda 2-5 min según conexión^)  ║
echo ║                                               ║
echo ╚═══════════════════════════════════════════════╝
echo.
echo  ⏳ Esperando a que los servidores se inicialicen...
echo  ⏳ ^(OLLAMA puede tomar 10-20 segundos en la 1era ejecución^)
echo.

REM Esperar más tiempo para que OLLAMA se inicialice
timeout /t 15 /nobreak >nul
start http://localhost:5173

REM Mantener esta ventana abierta para referencia
echo.
echo  ✓ Navegador abierto!
echo.
echo  Esta ventana mostrará los status de los servidores.
echo  Ciérralos para detener la aplicación.
echo.
pause

exit /b 0
