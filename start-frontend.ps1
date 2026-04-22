# Script para iniciar el servidor Vue (Frontend)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Iniciando Servidor Vue.js" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

# Ir a la carpeta del frontend
Set-Location "frontend"

# Verificar si node_modules existe
if (-Not (Test-Path "node_modules")) {
    Write-Host "`nInstalando dependencias Node.js..." -ForegroundColor Yellow
    npm install
} else {
    Write-Host "`nDependencias Node.js encontradas" -ForegroundColor Green
}

# Ejecutar servidor de desarrollo
Write-Host "`nIniciando servidor en http://localhost:5173" -ForegroundColor Green
Write-Host "Presiona Ctrl+C para detener el servidor`n" -ForegroundColor Yellow

npm run dev
