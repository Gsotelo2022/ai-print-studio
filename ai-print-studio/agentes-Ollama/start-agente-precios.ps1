Write-Host "===============================================" -ForegroundColor Cyan
Write-Host " AGENTE IA - ACTUALIZACION DE PRECIOS" -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Activando entorno virtual Python..." -ForegroundColor Green

if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: No existe el entorno virtual .venv" -ForegroundColor Red
    Write-Host "Ejecuta primero: python -m venv .venv" -ForegroundColor Yellow
    pause
    exit 1
}

& .\.venv\Scripts\Activate.ps1

Write-Host "[2/3] Verificando dependencias..." -ForegroundColor Green
Write-Host "  - Flask"
Write-Host "  - Flask-CORS"
Write-Host "  - requests"
Write-Host "  - pyodbc"
Write-Host ""

Write-Host "[3/3] Iniciando agente de precios en puerto 5002..." -ForegroundColor Green
Write-Host ""

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host " AGENTE INICIADO" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host " URL: http://localhost:5002" -ForegroundColor White
Write-Host " Endpoints:" -ForegroundColor White
Write-Host "   - POST /actualizar-precio (consulta lenguaje natural)" -ForegroundColor Gray
Write-Host "   - GET /health (verificar estado)" -ForegroundColor Gray
Write-Host ""
Write-Host " Ejemplos de uso:" -ForegroundColor White
Write-Host '   {"consulta": "cambiar precio del buzo a 15000"}' -ForegroundColor Gray
Write-Host '   {"detalle": "Buzo", "precio": 15000}' -ForegroundColor Gray
Write-Host ""
Write-Host " Presiona Ctrl+C para detener" -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

python agente_precios.py
