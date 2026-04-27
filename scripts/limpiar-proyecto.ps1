# ============================================================
# ANÁLISIS Y LIMPIEZA DE PROYECTO
# ============================================================
# Fecha: 22 de abril de 2026
# Objetivo: Identificar archivos obsoletos, tests y duplicados
# ============================================================

Write-Host "🔍 ANALIZANDO PROYECTO AI PRINT STUDIO" -ForegroundColor Cyan
Write-Host "=" * 60

$projectRoot = "C:\projects\ai-print-studio"
$archiveDir = "$projectRoot\_archive_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# ============================================================
# ARCHIVOS A ARCHIVAR (mover, no eliminar)
# ============================================================

$filesToArchive = @{
    "Tests y Scripts de Prueba" = @(
        # Tests en database/source
        "database\source\test_auth_flow.py",
        "database\source\test_insert_login.py",
        "database\source\test_login.py",
        "database\source\test_register.py",
        "database\source\test_register_complete.py",
        "database\source\check_orders.py",
        "database\source\create_test_orders.py",
        "database\source\verify_tables.py",
        "database\source\recreate_db.py",
        
        # Tests en raíz
        "test-agente-completo.py",
        "test-circuito.ps1",
        "verificar-base-datos.py",
        "verificar-sistema.py",
        "generar-usuarios-prueba.py"
    )
    
    "Documentación Obsoleta" = @(
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
        "README-EJECUTAR.txt"
    )
    
    "Scripts SQL Obsoletos" = @(
        "database\insertar-usuarios-prueba.sql",
        "database\insertar-clientes-ejemplo.sql",
        "database\crear-admin-manual.sql",
        "database\source\crear_clientes_ejemplo.py"
    )
    
    "Scripts de Diagnóstico" = @(
        "diagnostico.ps1",
        "diagnostico-completo.ps1",
        "setup-usuarios.ps1"
    )
    
    "Backend PHP (Ya no usado)" = @(
        "backend"  # Carpeta completa
    )
    
    "Backend FastAPI Vacío" = @(
        "backend_fastapi"  # Solo tiene .venv
    )
    
    "Entorno Virtual Antiguo" = @(
        "database\env"  # Entorno virtual viejo
    )
    
    "Archivos Duplicados" = @(
        "database\source\conexion.py",  # Duplicado de db.py
        "database\source\init_db.py",   # Ya no necesario con nueva estructura
        "database\productos.txt"        # Lista hardcoded de productos
    )
    
    "Scripts de Inicio Antiguos" = @(
        "start-all.bat",
        "start-all.ps1",
        "start-backend.ps1",
        "start-frontend.ps1",
        "stop.bat",
        "RUN.bat"
    )
    
    "Archivos Git Sin Usar" = @(
        "git",     # Archivo vacío?
        "main"     # Archivo vacío?
    )
}

# ============================================================
# ARCHIVOS A MANTENER
# ============================================================

$filesToKeep = @(
    # Documentación esencial
    "README.md",
    "PROPUESTA_MEJORAS_BD.md",
    "ESTADO_Y_TAREAS_PENDIENTES.md",
    "MIGRACION_COMPLETA_RESUMEN.md",
    
    # Scripts de migración (NUEVOS)
    "database\01-backup-bd-actual.sql",
    "database\02-nueva-estructura-bd.sql",
    "database\03-datos-iniciales.sql",
    "database\04-migrar-datos-antiguos.sql",
    "database\migrar-imagenes.py",
    "database\GUIA_EJECUCION_MIGRACION.md",
    
    # Backend funcional
    "database\source\app.py",
    "database\source\app_v2.py",
    "database\source\db.py",
    "database\source\requirements.txt",
    "database\source\README_BACKEND_V2.md",
    "database\source\test_api_v2.py",  # Test nuevo, mantener
    "database\source\start-fastapi.bat",
    "database\source\start-fastapi.ps1",
    
    # Frontend completo
    "frontend\",
    
    # Agentes Ollama
    "agentes-Ollama\",
    
    # Configuración
    ".gitignore",
    ".editorconfig",
    "install-dependencies.ps1",
    "descargar-modelo-ia.bat",
    
    # Estructura antigua de BD (referencia)
    "database\estructura-BDD-Prendete-Rock.sql"
)

# ============================================================
# RESUMEN
# ============================================================

Write-Host "`n📊 RESUMEN DEL ANÁLISIS:`n" -ForegroundColor Yellow

$totalToArchive = 0
foreach ($category in $filesToArchive.Keys) {
    $count = $filesToArchive[$category].Count
    $totalToArchive += $count
    Write-Host "  ❌ $category : " -NoNewline -ForegroundColor Red
    Write-Host "$count archivos" -ForegroundColor White
}

Write-Host "`n  📂 Total archivos/carpetas a archivar: $totalToArchive" -ForegroundColor Cyan

# ============================================================
# DETALLES DE ARCHIVOS
# ============================================================

Write-Host "`n📋 DETALLE DE ARCHIVOS A ARCHIVAR:`n" -ForegroundColor Yellow

foreach ($category in $filesToArchive.Keys) {
    Write-Host "  📁 $category" -ForegroundColor Cyan
    foreach ($file in $filesToArchive[$category]) {
        $fullPath = Join-Path $projectRoot $file
        if (Test-Path $fullPath) {
            Write-Host "    ✓ $file" -ForegroundColor Green
        } else {
            Write-Host "    ⚠ $file (no existe)" -ForegroundColor Yellow
        }
    }
    Write-Host ""
}

# ============================================================
# PREGUNTAR SI EJECUTAR
# ============================================================

Write-Host "`n⚠️  IMPORTANTE:" -ForegroundColor Yellow
Write-Host "  Los archivos NO se eliminarán, se moverán a:" -ForegroundColor White
Write-Host "  $archiveDir`n" -ForegroundColor Cyan

$response = Read-Host "¿Deseas ejecutar la limpieza ahora? (S/N)"

if ($response -eq 'S' -or $response -eq 's') {
    Write-Host "`n🚀 INICIANDO LIMPIEZA...`n" -ForegroundColor Green
    
    # Crear directorio de archivos
    New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
    Write-Host "✓ Creado directorio: $archiveDir" -ForegroundColor Green
    
    $movedCount = 0
    $errorCount = 0
    
    foreach ($category in $filesToArchive.Keys) {
        Write-Host "`n📁 Procesando: $category" -ForegroundColor Cyan
        
        foreach ($file in $filesToArchive[$category]) {
            $sourcePath = Join-Path $projectRoot $file
            
            if (Test-Path $sourcePath) {
                try {
                    # Crear estructura de carpetas en archive
                    $relativePath = $file
                    $destPath = Join-Path $archiveDir $relativePath
                    $destDir = Split-Path $destPath -Parent
                    
                    if (-not (Test-Path $destDir)) {
                        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                    }
                    
                    # Mover archivo o carpeta
                    Move-Item -Path $sourcePath -Destination $destPath -Force
                    Write-Host "  ✓ Movido: $file" -ForegroundColor Green
                    $movedCount++
                }
                catch {
                    Write-Host "  ❌ Error al mover: $file - $($_.Exception.Message)" -ForegroundColor Red
                    $errorCount++
                }
            }
            else {
                Write-Host "  ⚠ No existe: $file" -ForegroundColor Yellow
            }
        }
    }
    
    # Resumen final
    Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
    Write-Host "✅ LIMPIEZA COMPLETADA" -ForegroundColor Green
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host "  📦 Archivos movidos: $movedCount" -ForegroundColor Green
    Write-Host "  ❌ Errores: $errorCount" -ForegroundColor $(if ($errorCount -gt 0) {'Red'} else {'Green'})
    Write-Host "  📂 Ubicación archivo: $archiveDir`n" -ForegroundColor Cyan
    
    # Crear archivo de registro
    $logFile = Join-Path $archiveDir "ARCHIVADO_LOG.txt"
    $logContent = @"
REGISTRO DE ARCHIVOS ARCHIVADOS
================================
Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Proyecto: AI Print Studio
Razón: Limpieza pre-migración de base de datos

Archivos movidos: $movedCount
Errores: $errorCount

CATEGORÍAS ARCHIVADAS:
"@
    $logContent | Out-File $logFile

    foreach ($category in $filesToArchive.Keys) {
        Add-Content -Path $logFile -Value "`n$category :"
        foreach ($file in $filesToArchive[$category]) {
            Add-Content -Path $logFile -Value "  - $file"
        }
    }
    
    Write-Host "✓ Log creado: ARCHIVADO_LOG.txt`n" -ForegroundColor Green
    
    # Mostrar estructura resultante
    Write-Host "📊 ESTRUCTURA DEL PROYECTO (simplificada):`n" -ForegroundColor Yellow
    Write-Host "ai-print-studio/" -ForegroundColor Cyan
    Write-Host "  ├── database/" -ForegroundColor White
    Write-Host "  │   ├── 01-backup-bd-actual.sql ✨" -ForegroundColor Green
    Write-Host "  │   ├── 02-nueva-estructura-bd.sql ✨" -ForegroundColor Green
    Write-Host "  │   ├── 03-datos-iniciales.sql ✨" -ForegroundColor Green
    Write-Host "  │   ├── 04-migrar-datos-antiguos.sql ✨" -ForegroundColor Green
    Write-Host "  │   ├── migrar-imagenes.py ✨" -ForegroundColor Green
    Write-Host "  │   └── source/" -ForegroundColor White
    Write-Host "  │       ├── app_v2.py ✨" -ForegroundColor Green
    Write-Host "  │       ├── db.py" -ForegroundColor White
    Write-Host "  │       └── test_api_v2.py ✨" -ForegroundColor Green
    Write-Host "  ├── frontend/" -ForegroundColor White
    Write-Host "  ├── agentes-Ollama/" -ForegroundColor White
    Write-Host "  ├── README.md" -ForegroundColor White
    Write-Host "  ├── PROPUESTA_MEJORAS_BD.md" -ForegroundColor White
    Write-Host "  └── MIGRACION_COMPLETA_RESUMEN.md ✨" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "🎉 ¡Proyecto limpio y listo para migración!" -ForegroundColor Green
}
else {
    Write-Host "`n❌ Limpieza cancelada. No se modificó ningún archivo." -ForegroundColor Yellow
}

Write-Host "`n📝 NOTA: Puedes ejecutar este script nuevamente en cualquier momento." -ForegroundColor Cyan
Write-Host "Presiona cualquier tecla para salir..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
