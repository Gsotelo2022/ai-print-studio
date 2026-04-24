@echo off
chcp 65001 >nul
color 0A

REM ========================================
REM Script Maestro - Levanta la Aplicacion
REM ========================================

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ================================================
echo    INICIANDO APLICACION COMPLETA
echo    Prendete Rock - AI Print Studio
echo    [Un clic para todo]
echo ================================================
echo.

REM ========================================
REM [1] VERIFICAR Y INSTALAR PYTHON
REM ========================================
echo.
echo [1] Verificando dependencias Python
echo --------------------------------------------------
cd database\source

REM Crear entorno virtual si no existe
if not exist ".\.venv" (
    echo   [!] Creando entorno virtual
    python -m venv .venv
    echo   [OK] Entorno virtual creado
)

REM Activar environment
if exist ".\.venv\Scripts\activate.bat" (
    call .\.venv\Scripts\activate.bat >nul 2>&1
    echo   [OK] Virtual environment activado
) else (
    echo   [!] No se encontro .venv, usando Python global
)

REM Verificar si todas las dependencias estan instaladas
python -c "import uvicorn, pyodbc, PIL, fastapi" >nul 2>&1
if errorlevel 1 (
    echo   [!] Instalando dependencias desde requirements.txt
    python -m pip install -q --upgrade pip 2>nul
    python -m pip install -q -r requirements.txt 2>nul
    echo   [OK] Dependencias Python instaladas
) else (
    echo   [OK] Dependencias Python OK
)

cd ..\..\

REM ========================================
REM [2] VERIFICAR Y INSTALAR NODE.JS
REM ========================================
echo.
echo [2] Verificando dependencias Node.js
echo --------------------------------------------

if not exist "frontend\node_modules" (
    echo   [!] Instalando dependencias Node.js (primera vez)
    echo.
    cd frontend
    call npm install --silent 2>nul
    echo   [OK] Dependencias Node.js instaladas
    cd ..
) else (
    echo   [OK] Dependencias Node.js OK
)

REM ========================================
REM [3] VERIFICAR PHP Y COMPOSER (Mercado Pago)
REM ========================================
echo.
echo [3] Verificando PHP y Composer
echo --------------------------------------------

php -v >nul 2>&1
if errorlevel 1 (
    echo   [!] PHP no detectado (Mercado Pago puede no funcionar)
    set PHP_AVAILABLE=0
) else (
    echo   [OK] PHP detectado
    set PHP_AVAILABLE=1
    
    if not exist "backend\vendor" (
        echo   [!] Instalando Composer packages
        cd backend
        call composer install --quiet 2>nul
        echo   [OK] Dependencias PHP instaladas
        cd ..
    ) else (
        echo   [OK] Dependencias PHP OK
    )
)

REM ========================================
REM [3B] VERIFICAR OLLAMA Y AGENTE IA
REM ========================================
echo.
echo [3B] Verificando Agente IA (OLLAMA)
echo --------------------------------------------

ollama --version >nul 2>&1
if errorlevel 1 (
    echo   [!] OLLAMA no detectado
    echo       Descargar desde: https://ollama.com
    set OLLAMA_AVAILABLE=0
) else (
    echo   [OK] OLLAMA detectado
    set OLLAMA_AVAILABLE=1
    
    REM Verificar si OLLAMA esta corriendo en puerto 11434
    netstat -ano | findstr "11434" >nul 2>&1
    if errorlevel 1 (
        echo   [!] OLLAMA no esta corriendo, sera levantado automaticamente
        set OLLAMA_RUNNING=0
    ) else (
        echo   [OK] OLLAMA ya esta corriendo (puerto 11434)
        set OLLAMA_RUNNING=1
    )
    
    if not exist "agentes-Ollama\.venv\Scripts\activate.bat" (
        echo   [!] Configurando entorno virtual del agente
        cd agentes-Ollama
        python -m venv .venv
        call .\.venv\Scripts\activate.bat
        python -m pip install -q flask requests pyodbc flask-cors >nul 2>&1
        echo   [OK] Agente IA configurado
        cd ..
    ) else (
        echo   [OK] Agente IA ya configurado
    )
    
    REM Verificar que el modelo qwen2.5:1.5b este descargado
    echo   [~] Verificando modelo qwen2.5:1.5b
    ollama list | findstr "qwen2.5:1.5b" >nul 2>&1
    if errorlevel 1 (
        echo   [!] Modelo qwen2.5:1.5b no descargado
        echo       Se descargara automaticamente (primera ejecucion, puede tardar)
        set MODELO_MISSING=1
    ) else (
        echo   [OK] Modelo qwen2.5:1.5b encontrado
        set MODELO_MISSING=0
    )
)

REM ========================================
REM [4] MOSTRAR CONFIGURACION
REM ========================================
echo.
echo [4] Configuracion del Proyecto:
echo --------------------------------------------

echo.
echo   BASE DE DATOS:
echo    - Servidor: localhost\SQLEXPRESS01
echo    - BD: PrendeteRock
echo    - Estructura: 13 tablas (Productos, Variantes, Pedidos, Items)
echo    - Auth: Windows Authentication
echo.
echo   SERVIDORES A INICIAR:
echo    - FastAPI Backend ----------- http://127.0.0.1:8000
echo       * Registro, Login, Pedidos
echo       * Catalogo con variantes
echo       * Control de stock
echo    - Vue.js Frontend ----------- http://localhost:5173
echo       * Interfaz de Usuario
echo    - Agente IA (OLLAMA) -------- http://localhost:5001
echo       * Consultas inteligentes (opcional)
echo    - PHP Backend (Mercado Pago) http://localhost:8080
echo       * Procesamiento de pagos (opcional)
echo.
echo   DATOS DE PRUEBA:
echo    - Email: maria.gonzalez@email.com     Pwd: password123
echo    - Email: lucas.rodriguez@email.com    Pwd: password123
echo    - Email: ana.vazquez@email.com        Pwd: password123
echo    - (Hay 5 usuarios de prueba disponibles)
echo.
echo   PRODUCTOS DISPONIBLES:
echo    - 5 productos base (Remera, Taza, Buzo, Gorra, Bolsa)
echo    - 32 variantes con SKU
echo    - Stock controlado por variante
echo.

REM ========================================
REM [5] LEVANTAR SERVIDORES (3-5 ventanas)
REM ========================================
echo.
echo [5] Iniciando servidores
echo --------------------------------------------
echo.

REM â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
REM Server 1: FastAPI Backend (CRITICO)
REM â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
echo   [START] Iniciando FastAPI Backend V2
start "FastAPI Backend V2 - http://127.0.0.1:8000" cmd /k "cd /d "%cd%\database\source" && (if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat) && python -m uvicorn app_v2:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

REM â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
REM Server 1B: OLLAMA (si esta instalado y no corre)
REM â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if %OLLAMA_AVAILABLE% equ 1 (
    if %OLLAMA_RUNNING% equ 0 (
        echo   [START] Inicializando OLLAMA
        start "OLLAMA - http://localhost:11434" cmd /k "ollama serve"
        echo   [~] Esperando que OLLAMA se inicie completamente
        timeout /t 10 /nobreak >nul
        echo   [OK] OLLAMA iniciado
    ) else (
        echo   [OK] OLLAMA ya estaba corriendo
    )
    
    REM Descargar el modelo si falta (OLLAMA debe estar corriendo)
    if %MODELO_MISSING% equ 1 (
        echo   [~] Descargando modelo qwen2.5:1.5b (puede tardar varios minutos)
        echo       El modelo se descargara en segundo plano
        start "Descargando modelo OLLAMA" cmd /k "ollama pull qwen2.5:1.5b && echo. && echo [OK] Modelo descargado exitosamente! && echo Puedes cerrar esta ventana && timeout /t 10"
    )
)

REM â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
REM Server 1C: Agente IA (OLLAMA)
REM â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if %OLLAMA_AVAILABLE% equ 1 (
    echo   [START] Iniciando Agente IA (Python + OLLAMA)
    echo       * Consulta BD SQL Server (PrendeteRock)
    echo       * Procesa con qwen2.5:1.5b
    start "Agente IA - http://localhost:5001" cmd /k "cd /d "%cd%\agentes-Ollama" && call .\.venv\Scripts\activate.bat && python agente_productos.py"
    timeout /t 3 /nobreak >nul
    echo   [OK] Agente IA iniciado
)

timeout /t 1 /nobreak >nul

REM â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
REM Server 2: Vue.js Frontend
REM â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
echo   [START] Iniciando Vue.js Frontend
start "Vue Frontend - http://localhost:5173" cmd /k "cd /d "%cd%\frontend" && npm run dev"

timeout /t 2 /nobreak >nul

REM â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
REM Server 3: PHP Backend (Opcional, Mercado Pago)
REM â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if %PHP_AVAILABLE% equ 1 (
    echo   [START] Iniciando PHP Backend
    start "PHP Backend - http://localhost:8080" cmd /k "cd /d "%cd%\backend" && php -S localhost:8080"
) else (
    echo   [!] PHP no detectado - Mercado Pago no funcionara
)

REM ========================================
REM [6] RESUMEN FINAL
REM ========================================
echo.
echo ================================================
echo           APLICACION INICIADA
echo ================================================
echo.
echo  Se abrieron 3-5 ventanas automaticamente:
echo.
echo  (1) FastAPI Backend
echo      http://127.0.0.1:8000
echo      [OK] Endpoints:
echo        - POST /api/register
echo        - POST /api/login
echo        - GET  /api/productos
echo        - POST /api/create-order
echo.
echo  (2) Vue.js Frontend (ABRE AQUI)
echo      http://localhost:5173
echo      [OK] Interfaz web completa
echo      [OK] Catalogo de productos
echo      [OK] Carrito de compras
echo.
echo  (3) Agente IA (si OLLAMA instalado)
echo      http://localhost:5001
echo      [OK] Consultas inteligentes
echo.
echo  (4) PHP Backend (si PHP disponible)
echo      http://localhost:8080
echo      [OK] Mercado Pago
echo.
echo  PROXIMO PASO:
echo   - El navegador se abrira automaticamente
echo     en: http://localhost:5173
echo.
echo  BASE DE DATOS:
echo   - SQL Server: localhost\SQLEXPRESS01
echo   - Database: PrendeteRock
echo   - Productos: 5 base + 32 variantes
echo   - Usuarios: 2 de prueba
echo   - Stock: Controlado automaticamente
echo.
echo  CIRCUITO DEL CLIENTE:
echo   [OK] Registro de usuario
echo   [OK] Login con autenticacion
echo   [OK] Catalogo con variantes y stock
echo   [OK] Creacion de pedidos
echo   [OK] Control automatico de stock
echo.
echo  PARA DETENER: Cierra las ventanas CMD
echo.
echo ================================================
echo.
echo  [~] Esperando a que los servidores se inicialicen
echo.

REM Esperar tiempo para que los servidores se inicialicen
timeout /t 10 /nobreak >nul

REM Abrir navegador
echo  [OK] Abriendo navegador en http://localhost:5173
start http://localhost:5173

REM Mantener esta ventana abierta para referencia
echo.
echo  [OK] Navegador abierto!
echo.
echo  Esta ventana muestra el status de los servidores.
echo  Cierra las ventanas CMD para detener la aplicacion.
echo.
echo  APIs disponibles:
echo   * http://127.0.0.1:8000/docs - Documentacion FastAPI
echo   * http://localhost:5173 - Frontend Vue.js
echo.
pause

exit /b 0
