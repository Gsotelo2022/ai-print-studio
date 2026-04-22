# Script para instalar todas las dependencias del proyecto
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Instalando Dependencias" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

# 1. Instalación de dependencias Python (FastAPI Backend)
Write-Host "`n[1/2] Instalando dependencias Python (FastAPI)..." -ForegroundColor Yellow
Set-Location "database\source"

# Activar ambiente virtual
Write-Host "Activando ambiente virtual..." -ForegroundColor Cyan
& "..\env\Scripts\Activate.ps1"

Write-Host "Instalando paquetes Python..." -ForegroundColor Cyan
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Write-Host "✓ Dependencias Python instaladas" -ForegroundColor Green

# 2. Instalación de dependencias Node.js (Vue Frontend)
Write-Host "`n[2/2] Instalando dependencias Node.js (Vue)..." -ForegroundColor Yellow
Set-Location "..\..\frontend"

Write-Host "Instalando paquetes Node.js..." -ForegroundColor Cyan
npm install

Write-Host "✓ Dependencias Node.js instaladas" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "✓ Todas las dependencias instaladas!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nPuedes ejecutar: .\start-all.bat`n" -ForegroundColor Yellow
