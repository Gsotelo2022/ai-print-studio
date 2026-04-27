# ELIMINAR ARCHIVOS OBSOLETOS - AI PRINT STUDIO
# Este script elimina archivos de test y obsoletos antes de la migración

Write-Host ""
Write-Host "======================================================" -ForegroundColor Red
Write-Host "     ELIMINAR ARCHIVOS OBSOLETOS" -ForegroundColor Red
Write-Host "======================================================" -ForegroundColor Red
Write-Host ""

$projectRoot = "C:\projects\ai-print-studio"

# Archivos y carpetas a eliminar
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
        "RUN.bat"
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

# Contar
$totalCount = 0
foreach ($categoria in $archivos.Keys) {
    $totalCount += $archivos[$categoria].Count
}

Write-Host "Se eliminarán $totalCount archivos/carpetas" -ForegroundColor Yellow
Write-Host ""

# Mostrar resumen
foreach ($categoria in $archivos.Keys) {
    $count = $archivos[$categoria].Count
    Write-Host "  - $categoria : $count items" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "======================================================" -ForegroundColor Red
Write-Host ""
Write-Host "ADVERTENCIA:" -ForegroundColor Yellow
Write-Host "Esta acción NO se puede deshacer." -ForegroundColor Yellow
Write-Host "Los archivos serán eliminados permanentemente." -ForegroundColor Yellow
Write-Host ""

$confirmacion = Read-Host "¿Estás seguro de eliminar estos archivos? (S/N)"

if ($confirmacion -eq 'S' -or $confirmacion -eq 's') {
    Write-Host ""
    Write-Host "Eliminando archivos..." -ForegroundColor Red
    Write-Host ""
    
    $eliminados = 0
    $errores = 0
    $noExisten = 0
    
    foreach ($categoria in $archivos.Keys) {
        Write-Host "[$categoria]" -ForegroundColor Cyan
        
        foreach ($archivo in $archivos[$categoria]) {
            $ruta = Join-Path $projectRoot $archivo
            
            if (Test-Path $ruta) {
                try {
                    Remove-Item -Path $ruta -Recurse -Force -ErrorAction Stop
                    Write-Host "  OK   Eliminado: $archivo" -ForegroundColor Green
                    $eliminados++
                }
                catch {
                    Write-Host "  ERR  Error: $archivo - $($_.Exception.Message)" -ForegroundColor Red
                    $errores++
                }
            }
            else {
                Write-Host "  --   No existe: $archivo" -ForegroundColor DarkGray
                $noExisten++
            }
        }
        Write-Host ""
    }
    
    # Resumen final
    Write-Host "======================================================" -ForegroundColor Green
    Write-Host "LIMPIEZA COMPLETADA" -ForegroundColor Green
    Write-Host "======================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Archivos eliminados: $eliminados" -ForegroundColor Green
    Write-Host "  Errores: $errores" -ForegroundColor $(if ($errores -gt 0) {'Red'} else {'Green'})
    Write-Host "  No existían: $noExisten" -ForegroundColor DarkGray
    Write-Host ""
    
    # Guardar log
    $logFile = Join-Path $projectRoot "ELIMINACION_LOG.txt"
    $logContent = @"
LOG DE ELIMINACIÓN - AI PRINT STUDIO
====================================
Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Razón: Limpieza pre-migración de base de datos

RESUMEN:
  Archivos eliminados: $eliminados
  Errores: $errores
  No existían: $noExisten

ARCHIVOS ELIMINADOS:

"@
    
    foreach ($categoria in $archivos.Keys) {
        $logContent += "`n[$categoria]`n"
        foreach ($archivo in $archivos[$categoria]) {
            $logContent += "  $archivo`n"
        }
    }
    
    $logContent | Out-File $logFile -Encoding UTF8
    
    Write-Host "Log guardado en: ELIMINACION_LOG.txt" -ForegroundColor Green
    Write-Host ""
    Write-Host "Proyecto limpio y listo para migración!" -ForegroundColor Green
}
else {
    Write-Host ""
    Write-Host "Eliminación cancelada. No se modificó ningún archivo." -ForegroundColor Yellow
}

Write-Host ""
