#!/usr/bin/env python3
"""
Crear usuarios de prueba con contraseñas hasheadas
Genera INSERT SQL con contraseñas PBKDF2
"""

import hashlib
import os
import binascii

def hash_password(password):
    """
    Genera hash PBKDF2-HMAC-SHA256 compatible con la app
    Retorna: salt$iterations$hashedPassword (formato esperado)
    """
    iterations = 2500
    salt = os.urandom(32)
    salt_hex = binascii.hexlify(salt).decode()
    
    pwdhash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        iterations
    )
    pwdhash_hex = binascii.hexlify(pwdhash).decode()
    
    # Formato: iterations$salt$hash
    return f"{iterations}${salt_hex}${pwdhash_hex}"

# Crear usuarios
usuarios = [
    {
        'nombre': 'Cliente Test',
        'email': 'cliente@test.com',
        'telefono': '1234567890',
        'password': 'password123',
        'tipo': 'cliente'
    },
    {
        'nombre': 'Admin Test',
        'email': 'admin@test.com',
        'telefono': '0987654321',
        'password': 'password123',
        'tipo': 'admin'
    }
]

print("=" * 70)
print("🔐 GENERAR CONTRASEÑAS HASHEADAS")
print("=" * 70)
print()

# Generar hashes y mostrar
for usuario in usuarios:
    password = usuario['password']
    hash_completo = hash_password(password)
    
    print(f"Usuario: {usuario['email']}")
    print(f"Contraseña: {password}")
    print(f"Hash PBKDF2: {hash_completo}")
    print()

# Generar scripts SQL
print("\n" + "=" * 70)
print("📝 SCRIPTS SQL")
print("=" * 70)
print()

for usuario in usuarios:
    password = usuario['password']
    hash_completo = hash_password(password)
    
    sql = f"""
-- {usuario['nombre']}
INSERT INTO Usuarios (Nombre, Email, telefono, password_user, Tipo, fecha_registro)
VALUES (
    '{usuario['nombre']}',
    '{usuario['email']}',
    '{usuario['telefono']}',
    '{hash_completo}',
    '{usuario['tipo']}',
    GETDATE()
);
"""
    print(sql)

print("\n" + "=" * 70)
print("✅ DATOS GENERADOS")
print("=" * 70)
print("\n1. Copia los scripts SQL de arriba")
print("2. Pegalos en SQL Server Management Studio")
print("3. Ejecutalos contra la BD: PrendeteRock")
print("4. Luego podrás hacer login con:")
print()
for usuario in usuarios:
    print(f"   Email: {usuario['email']}")
    print(f"   Password: {usuario['password']}")
    print()
