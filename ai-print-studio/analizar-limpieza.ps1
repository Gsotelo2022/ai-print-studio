# Análisis de limpieza de proyecto AI Print Studio
# Este script identifica archivos para archivar antes de la migración

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "     ANÁLISIS DE LIMPIEZA - AI PRINT STUDIO" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = "C:\projects\ai-print-studio"

# Archivos a archivar
$archivos = @{
    "Tests database/source" = @(
        "database\source\test_auth_flow.py",
        "database\source\test_insert_login.py",
        "database\source\test_login.py",
        "database\source\test_register.py",
        "database\source\test_register_complete.py",
        "database\source\check_orders.py",
        "database\source\create_test_orders.py",
        "database\source\verify_tables.py"
    )
    
    "Tests raiz" = @(
        "test-agente-completo.py",
        "test-circuito.ps1",
        "verificar-base-datos.py",
        "verificar-sistema.py",
        "generar-usuarios-prueba.py"
    )
    
    "Docs obsoletos" = @(
        "FLUJO_ANTERIOR_AGENTE.md",
        "FLUJO_NUEVO_AGENTE.md",
        "MODO-PRUEBA-AGENTE.md",
        "REGISTRO_CAMBIOS.md",
        "REGISTRO_QUICKSTART.md",
        "REGISTRO_SOLUCION.md",
        "RESUMEN_TESTS_Y_CONFIG.md",
        "RUN_BAT_GUIA.md",
        "SISTEMA_LISTO.md",
        "LEEME.txt",
        "README-EJECUTAR.txt",
        "database\source\REGISTRO_USUARIOS.md"
    )
    
    "SQL obsoletos" = @(
        "database\insertar-usuarios-prueba.sql",
        "database\insertar-usuarios-prueba-FINAL.sql",
        "database\insertar-clientes-ejemplo.sql",
        "database\crear-admin-manual.sql"
    )
    
    "Scripts viejos" = @(
        "database\source\conexion.py",
        "database\source\init_db.py",
        "database\source\recreate_db.py",
        "database\source\create_admin.py",
        "diagnostico.ps1",
        "diagnostico-completo.ps1",
        "setup-usuarios.ps1"
    )
    
    "Scripts inicio viejos" = @(
        "start-all.bat",
        "start-all.ps1",
        "start-backend.ps1",
        "start-frontend.ps1",
        "stop.bat",
        "RUN.bat",
        "restart-fastapi.bat"
    )
    
    "Carpetas grandes" = @(
        "database\env",
        "database\source\.venv",
        "database\source\__pycache__",
        "backend_fastapi",
        "backend"
    )
    
    "Archivos vacios" = @(
        "git",
        "main",
        "database\productos.txt"
    )
}

# Contar y mostrar
Write-Host "RESUMEN:" -ForegroundColor Yellow
Write-Host ""

$totalCount = 0
$existCount = 0

foreach ($categoria in $archivos.Keys) {
    $count = $archivos[$categoria].Count
    $totalCount += $count
    
    Write-Host "  $categoria" -NoNewline -ForegroundColor Cyan
    Write-Host " : $count archivos" -ForegroundColor White
}

Write-Host ""
Write-Host "  Total a archivar: $totalCount archivos/carpetas" -ForegroundColor Magenta
Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# Mostrar detalle
Write-Host "DETALLE DE ARCHIVOS:" -ForegroundColor Yellow
Write-Host ""

foreach ($categoria in $archivos.Keys) {
    Write-Host "  [$categoria]" -ForegroundColor Cyan
    
    foreach ($archivo in $archivos[$categoria]) {
        $ruta = Join-Path $projectRoot $archivo
        if (Test-Path $ruta) {
            Write-Host "    OK   $archivo" -ForegroundColor Green
            $existCount++
        } else {
            Write-Host "    --   $archivo (no existe)" -ForegroundColor DarkGray
        }
    }
    Write-Host ""
}

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Archivos encontrados: $existCount de $totalCount" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# Guardar reporte
$reportFile = Join-Path $projectRoot "REPORTE_LIMPIEZA.txt"
$report = @"
REPORTE DE LIMPIEZA - AI PRINT STUDIO
======================================
Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

Total de archivos a archivar: $totalCount
Archivos existentes: $existCount

CATEGORÍAS:

"@

foreach ($categoria in $archivos.Keys) {
    $report += "`n$categoria`n"
    foreach ($archivo in $archivos[$categoria]) {
        $ruta = Join-Path $projectRoot $archivo
        $existe = if (Test-Path $ruta) { "OK" } else { "NO EXISTE" }
        $report += "  [$existe] $archivo`n"
    }
}

$report | Out-File $reportFile -Encoding UTF8
Write-Host "Reporte guardado en: REPORTE_LIMPIEZA.txt" -ForegroundColor Green
Write-Host ""
