# ============================================
# SCRIPT PARA EJECUTAR TESTS DE PEDIDO
# AI Print Studio
# ============================================

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🧪 AI Print Studio - Test de Flujo de Pedido            ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Verificar si Node.js está instalado
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js instalado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Node.js no está instalado" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor instala Node.js desde: https://nodejs.org/" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""

# Verificar si node-fetch está instalado
if (-not (Test-Path "node_modules\node-fetch")) {
    Write-Host "⚠️  node-fetch no está instalado" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📦 Instalando dependencias..." -ForegroundColor Cyan
    npm install
    Write-Host ""
}

# Verificar si el backend está corriendo
Write-Host "🔍 Verificando que el backend esté corriendo..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Backend está activo" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "❌ Error: El backend no está corriendo en http://localhost:8000" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor inicia el backend antes de ejecutar los tests:" -ForegroundColor Yellow
    Write-Host "   python database\source\app_v2.py" -ForegroundColor White
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""

# Ejecutar los tests
Write-Host "🚀 Ejecutando tests..." -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"
node tests\order-flow.test.js
$testResult = $LASTEXITCODE

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""

if ($testResult -eq 0) {
    Write-Host "✅ Tests completados exitosamente" -ForegroundColor Green
} else {
    Write-Host "❌ Tests fallaron" -ForegroundColor Red
}

Write-Host ""
Read-Host "Presiona Enter para salir"
