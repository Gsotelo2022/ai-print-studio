# Script para iniciar el servidor FastAPI (Base de Datos)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Iniciando Servidor FastAPI" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

# Ir a la carpeta del backend
Set-Location "database\source"

# Activar ambiente virtual
Write-Host "`nActivando ambiente virtual..." -ForegroundColor Yellow
& "..\env\Scripts\Activate.ps1"

# Verificar si uvicorn está instalado, si no instalar dependencias
Write-Host "`nVerificando dependencias..." -ForegroundColor Yellow
python -m pip show uvicorn >$null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Instalando dependencias... esto puede tomar un momento" -ForegroundColor Yellow
    python -m pip install -r requirements.txt
}

# Ejecutar servidor
Write-Host "`nIniciando servidor en http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Presiona Ctrl+C para detener el servidor`n" -ForegroundColor Yellow

python -m uvicorn app:app --host 127.0.0.1 --port 8000
