"""
Script para crear clientes de ejemplo en la base de datos
Útil para testing de la sección de Gestión de Clientes
"""

from db import get_connection
import hashlib
import secrets

def hash_password(pw: str) -> str:
    """Hashear contraseña con PBKDF2 (SHA256)"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', pw.encode(), bytes.fromhex(salt), 100000)
    return f"{salt}${hash_obj.hex()}"

def crear_clientes_ejemplo():
    """Crear clientes de ejemplo si no existen"""
    conn = get_connection()
    cur = conn.cursor()
    
    clientes_ejemplo = [
        {
            "nombre": "María González",
            "email": "maria.gonzalez@email.com",
            "telefono": "11 2345-6789",
            "password": "password123"
        },
        {
            "nombre": "Lucas Rodríguez",
            "email": "lucas.rodriguez@email.com",
            "telefono": "11 9876-5432",
            "password": "password123"
        },
        {
            "nombre": "Ana Vázquez",
            "email": "ana.vazquez@email.com",
            "telefono": "11 4567-8901",
            "password": "password123"
        },
        {
            "nombre": "Carlos Pérez",
            "email": "carlos.perez@email.com",
            "telefono": "11 1122-3344",
            "password": "password123"
        },
        {
            "nombre": "Sofía Martínez",
            "email": "sofia.martinez@email.com",
            "telefono": "11 5566-7788",
            "password": "password123"
        }
    ]
    
    creados = 0
    existentes = 0
    
    for cliente in clientes_ejemplo:
        # Verificar si ya existe
        cur.execute("SELECT COUNT(*) FROM Usuarios WHERE Email = %s", (cliente["email"],))
        count = cur.fetchone()[0]
        
        if count > 0:
            print(f"⚠️  Cliente ya existe: {cliente['email']}")
            existentes += 1
            continue
        
        # Hashear contraseña
        hashed_password = hash_password(cliente["password"])
        
        # Insertar cliente
        cur.execute("""
            INSERT INTO Usuarios (Nombre, Email, telefono, password_user, Tipo)
            VALUES (%s, ?, ?, ?, 'cliente')
        """, (cliente["nombre"], cliente["email"], cliente["telefono"], hashed_password))
        
        conn.commit()
        print(f"✅ Cliente creado: {cliente['nombre']} ({cliente['email']})")
        creados += 1
    
    cur.close()
    conn.close()
    
    print(f"\n📊 RESUMEN:")
    print(f"   • Clientes creados: {creados}")
    print(f"   • Clientes existentes: {existentes}")
    print(f"   • Total: {len(clientes_ejemplo)}")
    print(f"\n🔐 Todos los clientes tienen la contraseña: password123")

if __name__ == "__main__":
    print("🔄 Creando clientes de ejemplo...\n")
    try:
        crear_clientes_ejemplo()
        print("\n✅ Proceso completado exitosamente!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
