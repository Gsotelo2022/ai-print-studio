#!/usr/bin/env python3
"""
Test de Insert y Login de Usuario
Prueba inserción directa en BD + autenticación
"""
import pyodbc
import hashlib
import secrets
import json

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
print("TEST: Insert de Usuario y Login")
print("=" * 70)
print()

try:
    # Conectar a BD
    print("[1] Conectando a SQL Server...")
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=.\SQLEXPRESS01;'
        'DATABASE=PrendeteRock;'
        'Trusted_Connection=yes;'
    )
    cur = conn.cursor()
    print("✓ Conexión exitosa")
    
    # Datos de prueba
    test_email = "test_insert@example.com"
    test_name = "Usuario Test Insert"
    test_password = "TestPassword123"
    
    # Limpiar si existe
    print(f"\n[2] Preparando BD (eliminando usuario si existe)...")
    cur.execute("DELETE FROM Usuarios WHERE Email = ?", (test_email,))
    conn.commit()
    print("✓ BD preparada")
    
    # Insertar usuario
    print(f"\n[3] Insertando usuario...")
    hashed = hash_password(test_password)
    cur.execute(
        "INSERT INTO Usuarios (Nombre, Email, telefono, password_user, Tipo) VALUES (?, ?, ?, ?, ?)",
        (test_name, test_email, "+5491234567", hashed, "cliente")
    )
    conn.commit()
    print(f"✓ Usuario insertado correctamente")
    
    # Verificar insert
    print(f"\n[4] Verificando insert...")
    cur.execute("SELECT id_usuario, Nombre, Email FROM Usuarios WHERE Email = ?", (test_email,))
    row = cur.fetchone()
    
    if not row:
        print("✗ ERROR: Usuario no encontrado después del insert")
        exit(1)
    
    user_id, nombre, email = row[0], row[1], row[2]
    print(f"✓ Usuario encontrado:")
    print(f"  ID: {user_id}")
    print(f"  Nombre: {nombre}")
    print(f"  Email: {email}")
    
    # Test de Login (verificación de contraseña)
    print(f"\n[5] Probando verificación de contraseña...")
    cur.execute(
        "SELECT password_user FROM Usuarios WHERE Email = ?",
        (test_email,)
    )
    stored_hash = cur.fetchone()[0]
    
    # Verificar con contraseña correcta
    if verify_password(test_password, stored_hash):
        print("✓ Contraseña correcta verificada")
    else:
        print("✗ ERROR: Contraseña no coincide")
        exit(1)
    
    # Verificar con contraseña incorrecta
    if not verify_password("WrongPassword123", stored_hash):
        print("✓ Contraseña incorrecta rechazada correctamente")
    else:
        print("✗ ERROR: Contraseña incorrecta fue aceptada")
        exit(1)
    
    # Simulación de login (SELECT + verificación)
    print(f"\n[6] Simulando proceso de login...")
    cur.execute(
        "SELECT id_usuario, Nombre, Email, password_user, Tipo FROM Usuarios WHERE Email = ?",
        (test_email,)
    )
    row = cur.fetchone()
    
    if not row:
        print("✗ ERROR: Usuario no encontrado en login")
        exit(1)
    
    user_id, nombre, email, stored_hash, tipo = row[0], row[1], row[2], row[3], row[4]
    
    # Verificar contraseña
    if not verify_password(test_password, stored_hash):
        print("✗ ERROR: Credenciales inválidas")
        exit(1)
    
    print(f"✓ Login exitoso!")
    print(f"  Usuario: {nombre}")
    print(f"  Email: {email}")
    print(f"  Tipo: {tipo}")
    print(f"  Session ID: {user_id}")
    
    # Datos del usuario (como se devolvería en la API)
    user_data = {
        "id_usuario": user_id,
        "Nombre": nombre,
        "Email": email,
        "Tipo": tipo
    }
    print(f"\n[7] Datos que se enviarían en respuesta API:")
    print(json.dumps(user_data, indent=2))
    
    # Limpiar
    print(f"\n[8] Limpiando datos de prueba...")
    cur.execute("DELETE FROM Usuarios WHERE Email = ?", (test_email,))
    conn.commit()
    print("✓ Datos limpiados")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 70)
    print("✓ TEST COMPLETADO EXITOSAMENTE")
    print("=" * 70)
    print()
    print("Resumen:")
    print(f"  ✓ Insert de usuario funciona")
    print(f"  ✓ Verificación de contraseña funciona")
    print(f"  ✓ Login (select + verify) funciona")
    print(f"  ✓ Hash PBKDF2 funciona correctamente")
    print()

except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
