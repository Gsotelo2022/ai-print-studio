# Script para generar hashes de contraseñas y crear usuarios en la BD
# Ejecuta esto en PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuración Inicial de la BD" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

# Activar el ambiente virtual
Write-Host "`nActivando ambiente virtual..." -ForegroundColor Yellow
Set-Location "database\source"
& "..\env\Scripts\Activate.ps1"

# Crear un script Python que inserte los usuarios
$pythonScript = @'
import sys
sys.path.insert(0, '.')

from db import get_connection
from app import hash_password

try:
    conn = get_connection()
    cur = conn.cursor()
    
    # Contraseña para los usuarios de prueba
    test_password = "password123"
    hashed = hash_password(test_password)
    
    print("\n[1] Insertando usuario cliente...")
    try:
        cur.execute(
            "INSERT INTO Usuarios (Nombre, Email, telefono, password_user, Tipo) VALUES (?, ?, ?, ?, ?)",
            ('Juan Cliente', 'cliente@test.com', '1234567890', hashed, 'cliente')
        )
        conn.commit()
        print("✓ Usuario cliente@test.com creado")
    except Exception as e:
        print(f"⚠ No se pudo crear cliente@test.com: {e}")
    
    print("\n[2] Insertando usuario admin...")
    try:
        cur.execute(
            "INSERT INTO Usuarios (Nombre, Email, telefono, password_user, Tipo) VALUES (?, ?, ?, ?, ?)",
            ('Admin Rock', 'admin@test.com', '1234567890', hashed, 'admin')
        )
        conn.commit()
        print("✓ Usuario admin@test.com creado")
    except Exception as e:
        print(f"⚠ No se pudo crear admin@test.com: {e}")
    
    print("\n[3] Listando usuarios:")
    cur.execute("SELECT id_usuario, Nombre, Email, Tipo FROM Usuarios")
    rows = cur.fetchall()
    for row in rows:
        print(f"   - ID: {row[0]} | Nombre: {row[1]} | Email: {row[2]} | Tipo: {row[3]}")
    
    cur.close()
    conn.close()
    
    print("\n========================================")
    print("✓ Configuración completada")
    print("========================================")
    print("\nPuedes hacer login con:")
    print("Email: cliente@test.com | Contraseña: password123")
    print("Email: admin@test.com | Contraseña: password123")
    print("")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
'@

# Guardar el script Python temporalmente
$pythonScript | Out-File -FilePath "setup_usuarios.py" -Encoding UTF8

# Ejecutar el script Python
Write-Host "`nInsertando usuarios de prueba..." -ForegroundColor Yellow
python setup_usuarios.py

# Limpiar el archivo temporal
Remove-Item "setup_usuarios.py" -Force

Write-Host "`nVolviendo al directorio principal..." -ForegroundColor Yellow
Set-Location "..\.."

Write-Host "`n✓ Listo para usar!" -ForegroundColor Green
