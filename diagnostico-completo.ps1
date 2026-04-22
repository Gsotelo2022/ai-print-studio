# Script avanzado de diagnóstico
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Diagnóstico Completo del Sistema" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n[1] Verificando conexión a SQL Server..." -ForegroundColor Yellow
try {
    $conn = New-Object System.Data.SqlClient.SqlConnection
    $conn.ConnectionString = "Server=localhost\SQLEXPRESS01;Integrated Security=true;Connection Timeout=3;"
    $conn.Open()
    Write-Host "✓ SQL Server CONECTADO" -ForegroundColor Green
    
    # Verificar base de datos
    Write-Host "`n[2] Verificando base de datos 'PrendeteRock'..." -ForegroundColor Yellow
    $cmd = $conn.CreateCommand()
    $cmd.CommandText = "SELECT COUNT(*) FROM sys.databases WHERE name='PrendeteRock'"
    $result = $cmd.ExecuteScalar()
    
    if ($result -gt 0) {
        Write-Host "✓ Base de datos 'PrendeteRock' EXISTE" -ForegroundColor Green
        
        # Cambiar a la BD
        $conn.Close()
        $conn = New-Object System.Data.SqlClient.SqlConnection
        $conn.ConnectionString = "Server=localhost\SQLEXPRESS01;Database=PrendeteRock;Integrated Security=true;Connection Timeout=3;"
        $conn.Open()
        
        # Verificar tabla Usuarios
        Write-Host "`n[3] Verificando tabla 'Usuarios'..." -ForegroundColor Yellow
        $cmd = $conn.CreateCommand()
        $cmd.CommandText = "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='Usuarios'"
        $result = $cmd.ExecuteScalar()
        
        if ($result -gt 0) {
            Write-Host "✓ Tabla 'Usuarios' EXISTE" -ForegroundColor Green
            
            # Contar usuarios
            Write-Host "`n[4] Usuarios en la base de datos..." -ForegroundColor Yellow
            $cmd = $conn.CreateCommand()
            $cmd.CommandText = "SELECT COUNT(*) FROM Usuarios"
            $userCount = $cmd.ExecuteScalar()
            Write-Host "   Total de usuarios: $userCount" -ForegroundColor Cyan
            
            if ($userCount -gt 0) {
                Write-Host "`n   Listado de usuarios:" -ForegroundColor Cyan
                $cmd.CommandText = "SELECT id_usuario, Nombre, Email, Tipo FROM Usuarios"
                $reader = $cmd.ExecuteReader()
                while ($reader.Read()) {
                    Write-Host "   - ID: $($reader[0]) | Nombre: $($reader[1]) | Email: $($reader[2]) | Tipo: $($reader[3])" -ForegroundColor Cyan
                }
                $reader.Close()
            } else {
                Write-Host "   ⚠ No hay usuarios en la BD" -ForegroundColor Yellow
            }
        } else {
            Write-Host "✗ Tabla 'Usuarios' NO EXISTE" -ForegroundColor Red
            Write-Host "   Necesitas ejecutar el script: estructura-BDD-Prendete-Rock.sql" -ForegroundColor Yellow
        }
        
        $conn.Close()
    } else {
        Write-Host "✗ Base de datos 'PrendeteRock' NO EXISTE" -ForegroundColor Red
        Write-Host "   Necesitas ejecutar el script: estructura-BDD-Prendete-Rock.sql" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "✗ No se pudo conectar a SQL Server" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`n   Soluciones:" -ForegroundColor Yellow
    Write-Host "   1. Verifica que SQL Server está corriendo" -ForegroundColor Yellow
    Write-Host "   2. Verifica que la instancia se llama 'SQLEXPRESS01'" -ForegroundColor Yellow
    Write-Host "   3. Verifica que tienes permisos de acceso" -ForegroundColor Yellow
}

Write-Host "`n[5] Verificando Backend FastAPI..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -ErrorAction Stop
    Write-Host "✓ FastAPI ACTIVO y respondiendo" -ForegroundColor Green
} catch {
    Write-Host "✗ FastAPI NO ESTÁ ACTIVO" -ForegroundColor Red
    Write-Host "   Ejecuta: .\start-all.bat" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Diagnóstico completado" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
