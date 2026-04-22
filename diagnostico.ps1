# Script de diagnostico para verificar conexion backend-BD
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Diagnóstico del Sistema" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

$projectRoot = "c:\projects\ai-print-studio"

Write-Host "`n[1] Verificando archivo configuración..." -ForegroundColor Yellow
$dbFile = "$projectRoot\database\source\db.py"
if (Test-Path $dbFile) {
    Write-Host "✓ Archivo db.py existe" -ForegroundColor Green
    Get-Content $dbFile
} else {
    Write-Host "✗ db.py no encontrado" -ForegroundColor Red
}

Write-Host "`n[2] Verificando dependencias Python..." -ForegroundColor Yellow
$reqFile = "$projectRoot\database\source\requirements.txt"
if (Test-Path $reqFile) {
    Write-Host "✓ requirements.txt encontrado" -ForegroundColor Green
    Write-Host "Contenido:" -ForegroundColor Cyan
    Get-Content $reqFile
}

Write-Host "`n[3] Configuración del frontend..." -ForegroundColor Yellow
$apiFile = "$projectRoot\frontend\src\composables\useApi.js"
if (Test-Path $apiFile) {
    Write-Host "✓ useApi.js encontrado" -ForegroundColor Green
    Write-Host "BaseAPI configurada como:" -ForegroundColor Cyan
    Select-String "const baseApi" $apiFile
}

Write-Host "`n[4] Intentando conectar a http://localhost:8000/api/health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -ErrorAction Stop
    Write-Host "✓ Servidor FastAPI está ACTIVO" -ForegroundColor Green
    $response.StatusCode
} catch {
    Write-Host "✗ Servidor FastAPI NO ESTÁ ACTIVO" -ForegroundColor Red
    Write-Host "   Por favor ejecuta: .\start-backend.ps1" -ForegroundColor Yellow
}

Write-Host "`n[5] Verificando SQL Server..." -ForegroundColor Yellow
try {
    $conn = [System.Data.SqlClient.SqlConnection]::new("Server=localhost\SQLEXPRESS01;Integrated Security=true;Connection Timeout=3;")
    $conn.Open()
    Write-Host "✓ SQL Server ACCESIBLE" -ForegroundColor Green
    $conn.Close()
} catch {
    Write-Host "✗ No se puede conectar a SQL Server" -ForegroundColor Red
    Write-Host "   Verifica que SQLEXPRESS01 esté corriendo" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Diagnóstico completado" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
