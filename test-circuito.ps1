# ========================================
# TEST CIRCUITO COMPLETO - AI Print Studio
# ========================================
# Verifica que todo el flujo funcione:
# BD SQL Server → Python → OLLAMA → Agente IA → Frontend
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🧪 TEST CIRCUITO COMPLETO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: SQL Server
Write-Host "[1/5] Verificando SQL Server..." -ForegroundColor Yellow
try {
    $conn = New-Object System.Data.SqlClient.SqlConnection
    $conn.ConnectionString = "Server=.\SQLEXPRESS01;Database=PrendeteRock;Integrated Security=True;"
    $conn.Open()
    $cmd = $conn.CreateCommand()
    $cmd.CommandText = "SELECT COUNT(*) FROM Productos"
    $count = $cmd.ExecuteScalar()
    $conn.Close()
    Write-Host "   ✅ SQL Server OK - $count productos en BD" -ForegroundColor Green
} catch {
    Write-Host "   ❌ SQL Server NO responde" -ForegroundColor Red
    exit 1
}

# Test 2: OLLAMA
Write-Host "[2/5] Verificando OLLAMA..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:11434/" -Method Get -TimeoutSec 3 -ErrorAction Stop
    if ($response -match "Ollama is running") {
        Write-Host "   ✅ OLLAMA respondiendo" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ OLLAMA no responde (debe estar corriendo en puerto 11434)" -ForegroundColor Red
    Write-Host "   💡 Ejecutar: ollama serve" -ForegroundColor Yellow
}

# Test 3: Modelo qwen2.5:1.5b
Write-Host "[3/5] Verificando modelo qwen2.5:1.5b..." -ForegroundColor Yellow
$modelos = ollama list 2>&1 | Out-String
if ($modelos -match "qwen2.5:1.5b") {
    Write-Host "   ✅ Modelo qwen2.5:1.5b instalado" -ForegroundColor Green
} else {
    Write-Host "   ❌ Modelo qwen2.5:1.5b NO encontrado" -ForegroundColor Red
    Write-Host "   💡 Ejecutar: ollama pull qwen2.5:1.5b" -ForegroundColor Yellow
}

# Test 4: Agente IA (puerto 5001)
Write-Host "[4/5] Verificando Agente IA..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:5001/productos-ia" -Method Get -TimeoutSec 90 -ErrorAction Stop
    $productosIA = $response | ConvertFrom-Json
    Write-Host "   ✅ Agente IA OK - Retornó $($productosIA.Count) productos agrupados" -ForegroundColor Green
    
    # Mostrar muestra
    Write-Host "   📦 Muestra de productos:" -ForegroundColor Cyan
    $productosIA | Select-Object -First 3 | ForEach-Object {
        Write-Host "      • $($_.producto): Talles[$($_.talles -join ',')] Colores[$($_.colores -join ',')]" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ❌ Agente IA no responde (puerto 5001)" -ForegroundColor Red
    Write-Host "   💡 Iniciar con: cd agentes-Ollama; python agente_productos.py" -ForegroundColor Yellow
}

# Test 5: FastAPI Backend
Write-Host "[5/5] Verificando FastAPI Backend..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/docs" -Method Get -TimeoutSec 3 -ErrorAction Stop
    Write-Host "   ✅ FastAPI Backend OK (http://127.0.0.1:8000)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ FastAPI Backend no responde" -ForegroundColor Red
    Write-Host "   💡 Iniciar con RUN.bat" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ TEST COMPLETADO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔗 ENDPOINTS DISPONIBLES:" -ForegroundColor Cyan
Write-Host "   • Frontend:  http://localhost:5173" -ForegroundColor White
Write-Host "   • Agente IA: http://localhost:5001/productos-ia" -ForegroundColor White
Write-Host "   • FastAPI:   http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "   • OLLAMA:    http://localhost:11434" -ForegroundColor White
Write-Host ""
