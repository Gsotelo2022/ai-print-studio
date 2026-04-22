#!/usr/bin/env pwsh
# Script PowerShell para iniciar el servidor FastAPI

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Iniciando servidor FastAPI" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$sourceDir = "c:\projects\ai-print-studio\database\source"
Set-Location $sourceDir

Write-Host "Directorio: $sourceDir" -ForegroundColor Green
Write-Host ""

# Verificar si existe virtual environment
$venvPath = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "Activando virtual environment..." -ForegroundColor Yellow
    & $venvPath
    Write-Host "✓ Virtual environment activado" -ForegroundColor Green
} else {
    Write-Host "⚠ Virtual environment no encontrado en .\.venv" -ForegroundColor Yellow
    Write-Host "  (Pero continuando de todas formas)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Iniciando FastAPI en http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Presiona CTRL+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000

Read-Host "Presiona ENTER para cerrar"
