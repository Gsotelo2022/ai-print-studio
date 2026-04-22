#!/usr/bin/env python3
"""
Test completo para registro de usuarios
Verifica: conexión BD, inserción, duplicados, contraseñas, endpoint
"""
import urllib.request
import json
import sys
import time
from db import get_connection
import hashlib
import secrets

def hash_password(pw: str) -> str:
    """Hashear contraseña con PBKDF2 (SHA256)"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', pw.encode(), bytes.fromhex(salt), 100000)
    return f"{salt}${hash_obj.hex()}"

def verify_password(plain: str, hashed: str) -> bool:
    """Verificar contraseña hasheada"""
    try:
        salt, hash_hex = hashed.split('$')
        hash_obj = hashlib.pbkdf2_hmac('sha256', plain.encode(), bytes.fromhex(salt), 100000)
        return hash_obj.hex() == hash_hex
    except:
        return False

print("=" * 70)
print("TEST COMPLETO: REGISTRO DE USUARIOS")
print("=" * 70)

# TEST 1: Conexión a BD
print("\n[TEST 1] Verificando conexión a SQL Server...")
try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Usuarios")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    print(f"✓ Conexión exitosa. Total usuarios en BD: {count}")
except Exception as e:
    print(f"✗ ERROR de conexión: {e}")
    sys.exit(1)

# TEST 2: Verificar estructura de tabla Usuarios
print("\n[TEST 2] Verificando estructura de tabla Usuarios...")
try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'Usuarios'
        ORDER BY ORDINAL_POSITION
    """)
    columns = cur.fetchall()
    if not columns:
        print("✗ Tabla 'Usuarios' no encontrada")
        sys.exit(1)
    
    print("Columnas encontradas:")
    for col in columns:
        nullable = "NULL" if col[2] == "YES" else "NOT NULL"
        print(f"  - {col[0]}: {col[1]} ({nullable})")
    
    required_cols = ['id_usuario', 'Nombre', 'Email', 'password_user']
    found_cols = [col[0] for col in columns]
    for req in required_cols:
        if req not in found_cols:
            print(f"✗ Falta columna requerida: {req}")
            sys.exit(1)
    print("✓ Estructura OK")
    cur.close()
    conn.close()
except Exception as e:
    print(f"✗ ERROR: {e}")
    sys.exit(1)

# TEST 3: Inserción directa en BD
print("\n[TEST 3] Probando inserción directa en BD...")
test_email = f"test_direct_{int(time.time())}@test.com"
test_password = "TestPass123!"

try:
    conn = get_connection()
    cur = conn.cursor()
    
    # Limpiar si existe
    cur.execute("DELETE FROM Usuarios WHERE Email = ?", (test_email,))
    conn.commit()
    
    # Insertar
    hashed = hash_password(test_password)
    cur.execute(
        "INSERT INTO Usuarios (Nombre, Email, telefono, password_user, Tipo) VALUES (?, ?, ?, ?, ?)",
        ("Test User Direct", test_email, "+5491234567", hashed, "cliente")
    )
    conn.commit()
    
    # Verificar
    cur.execute("SELECT id_usuario, Nombre, Email FROM Usuarios WHERE Email = ?", (test_email,))
    row = cur.fetchone()
    
    if row:
        print(f"✓ Inserción exitosa")
        print(f"  ID: {row[0]}, Nombre: {row[1]}, Email: {row[2]}")
        user_id_direct = row[0]
        
        # Verificar contraseña
        cur.execute("SELECT password_user FROM Usuarios WHERE id_usuario = ?", (row[0],))
        stored_hash = cur.fetchone()[0]
        if verify_password(test_password, stored_hash):
            print(f"✓ Hash de contraseña verificado correctamente")
        else:
            print(f"✗ ERROR: Hash de contraseña no coincide")
    else:
        print(f"✗ ERROR: No se insertó el registro")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"✗ ERROR en inserción: {e}")
    import traceback
    traceback.print_exc()

# TEST 4: Verificar duplicado
print("\n[TEST 4] Probando detección de email duplicado...")
try:
    conn = get_connection()
    cur = conn.cursor()
    
    # Intentar insertar con email existente
    hashed = hash_password("AnotherPass123!")
    try:
        cur.execute(
            "INSERT INTO Usuarios (Nombre, Email, telefono, password_user, Tipo) VALUES (?, ?, ?, ?, ?)",
            ("Otro Usuario", test_email, "+5491234567", hashed, "cliente")
        )
        conn.commit()
        print("✗ ERROR: Se permitió insertar email duplicado (falta constraint UNIQUE)")
    except Exception as dup_error:
        if 'UNIQUE' in str(dup_error) or 'duplicate' in str(dup_error).lower():
            print("✓ Constraint UNIQUE funcionando correctamente")
        else:
            print(f"✗ Otro error: {dup_error}")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"✗ ERROR: {e}")

# TEST 5: Prueba del endpoint HTTP
print("\n[TEST 5] Probando endpoint HTTP /api/register...")
test_email_api = f"test_api_{int(time.time())}@test.com"

payload = {
    "fullname": "Test API User",
    "email": test_email_api,
    "phone": "+5491234567",
    "password": "ApiTestPass123!"
}

try:
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/register',
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        if result.get("success"):
            print("✓ Registro HTTP exitoso")
            print(f"  Usuario ID: {result['data']['id_usuario']}")
            print(f"  Nombre: {result['data']['Nombre']}")
            print(f"  Email: {result['data']['Email']}")
        else:
            print(f"✗ Respuesta no exitosa: {result}")
except urllib.error.HTTPError as e:
    error_data = json.loads(e.read().decode())
    print(f"✗ Error HTTP {e.code}: {error_data}")
except urllib.error.URLError as e:
    print(f"✗ ERROR: No se puede conectar al servidor en http://127.0.0.1:8000")
    print(f"  Detalle: {e}")
    print("\n⚠ SOLUCIÓN: Inicia el servidor FastAPI con:")
    print("  cd c:\\projects\\ai-print-studio\\database\\source")
    print("  python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000")
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

# TEST 6: Limpiar datos de prueba
print("\n[TEST 6] Limpiando datos de prueba...")
try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Usuarios WHERE Email LIKE 'test_%@test.com'")
    conn.commit()
    print("✓ Datos de prueba eliminados")
    cur.close()
    conn.close()
except Exception as e:
    print(f"⚠ No se pudieron limpiar los datos: {e}")

print("\n" + "=" * 70)
print("TEST FINALIZADO")
print("=" * 70)
