# Script para iniciar ambos servidores (Backend FastAPI + Frontend Vue)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Iniciando TODOS los Servidores" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

$projectRoot = Get-Location

# Iniciar servidor FastAPI en una nueva ventana
Write-Host "`n[1/2] Abriendo servidor FastAPI..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$projectRoot'; & '.\start-backend.ps1'"

# Esperar un momento antes de iniciar el segundo servidor
Start-Sleep -Seconds 3

# Iniciar servidor Vue en una nueva ventana
Write-Host "[2/2] Abriendo servidor Vue.js..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$projectRoot'; & '.\start-frontend.ps1'"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "✓ Ambos servidores están iniciando..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nFastAPI (Backend):  http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Vue.js (Frontend):  http://localhost:5173" -ForegroundColor Cyan
Write-Host "`nCierra las ventanas PowerShell para detener los servidores.`n" -ForegroundColor Yellow
