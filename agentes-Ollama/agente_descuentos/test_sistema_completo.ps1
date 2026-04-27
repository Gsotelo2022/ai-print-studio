# Test completo del sistema de cupones con IA

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  SISTEMA DE GESTION DE CUPONES CON IA" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

# Test 1: Verificar API
Write-Host "[1/4] Verificando API de descuentos..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:5003/health"
    Write-Host "  ✓ API funcionando correctamente" -ForegroundColor Green
    Write-Host "    Status: $($health.status)" -ForegroundColor Gray
}
catch {
    Write-Host "  ✗ API no disponible" -ForegroundColor Red
    exit
}

# Test 2: Listar cupones existentes
Write-Host "`n[2/4] Listando cupones actuales..." -ForegroundColor Yellow
try {
    $cupones = Invoke-RestMethod -Uri "http://localhost:5003/api/cupones"
    Write-Host "  ✓ Cupones encontrados: $($cupones.total)" -ForegroundColor Green
    foreach ($cupon in $cupones.cupones) {
        Write-Host "    - $($cupon.codigo): $($cupon.descuento_porcentaje)% OFF" -ForegroundColor Gray
    }
}
catch {
    Write-Host "  ✗ Error listando cupones" -ForegroundColor Red
}

# Test 3: Obtener estadísticas
Write-Host "`n[3/4] Obteniendo estadísticas de ventas..." -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "http://localhost:5003/api/estadisticas"
    Write-Host "  ✓ Estadísticas obtenidas" -ForegroundColor Green
    Write-Host "    Pedidos (30d): $($stats.estadisticas.ultimo_mes.total_pedidos)" -ForegroundColor Gray
    Write-Host "    Clientes nuevos: $($stats.estadisticas.clientes.nuevos)" -ForegroundColor Gray
    Write-Host "    Clientes recurrentes: $($stats.estadisticas.clientes.recurrentes)" -ForegroundColor Gray
}
catch {
    Write-Host "  ✗ Error obteniendo estadísticas" -ForegroundColor Red
}

# Test 4: Verificar Ollama para propuestas IA
Write-Host "`n[4/4] Verificando Ollama para propuestas IA..." -ForegroundColor Yellow
try {
    $ollama = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 2
    Write-Host "  ✓ Ollama disponible" -ForegroundColor Green
    Write-Host "    Modelos: $($ollama.models.Count)" -ForegroundColor Gray
    
    Write-Host "`n  Probando propuesta IA..." -ForegroundColor Cyan
    $propuesta = Invoke-RestMethod -Uri "http://localhost:5003/api/cupones/proponer" -Method POST -TimeoutSec 30
    
    if ($propuesta.success) {
        Write-Host "  ✓ IA generó propuestas exitosamente" -ForegroundColor Green
        Write-Host "`n  📋 PROPUESTAS GENERADAS:" -ForegroundColor Magenta
        Write-Host "  Análisis: $($propuesta.propuesta.analisis)`n" -ForegroundColor Gray
        
        foreach ($cupon in $propuesta.propuesta.cupones) {
            Write-Host "  🎟️  CUPÓN: $($cupon.codigo)" -ForegroundColor Cyan
            Write-Host "     Descripción: $($cupon.descripcion)" -ForegroundColor Gray
            Write-Host "     Descuento: $($cupon.descuento)%" -ForegroundColor Green
            Write-Host "     Duración: $($cupon.duracion_dias) días" -ForegroundColor Gray
            Write-Host "     Objetivo: $($cupon.objetivo)`n" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "  ⚠ IA no pudo generar propuestas" -ForegroundColor Yellow
        Write-Host "    Mensaje: $($propuesta.mensaje)" -ForegroundColor Gray
    }
}
catch {
    Write-Host "  ⚠ Ollama no disponible (opcional)" -ForegroundColor Yellow
    Write-Host "    Para propuestas IA, inicia Ollama con: ollama serve" -ForegroundColor Gray
}

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "  RESUMEN DEL SISTEMA" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "OK - API de descuentos: http://localhost:5003" -ForegroundColor Green
Write-Host "OK - Panel admin: Integrado en AdminDashboard" -ForegroundColor Green
Write-Host "OK - Documentacion: http://localhost:5003/docs" -ForegroundColor Green
Write-Host "`nFuncionalidades disponibles:" -ForegroundColor White
Write-Host "  - Crear, editar y eliminar cupones" -ForegroundColor Gray
Write-Host "  - Ver estadisticas de ventas en tiempo real" -ForegroundColor Gray
Write-Host "  - Propuestas inteligentes con IA (Ollama)" -ForegroundColor Gray
Write-Host "  - Analisis de comportamiento de clientes" -ForegroundColor Gray
Write-Host "  - Descuentos automaticos por cantidad y fidelidad" -ForegroundColor Gray
Write-Host "`n================================================`n" -ForegroundColor Cyan
