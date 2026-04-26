import pyodbc
import hashlib
import secrets

def hash_password(pw: str) -> str:
    """Hashear contraseña con PBKDF2 (SHA256)"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', pw.encode(), bytes.fromhex(salt), 100000)
    return f"{salt}${hash_obj.hex()}"

conn = pyodbc.connect(
    'DRIVER={SQL Server};'
    'SERVER=localhost\SQLEXPRESS01;'
    'DATABASE=PrendeteRock;'
    'Trusted_Connection=yes;'
)

cur = conn.cursor()

# Verificar si ya existe un administrador
cur.execute("SELECT id_usuario, Email, Nombre, Tipo FROM Usuarios WHERE Tipo = 'admin' OR Email LIKE '%admin%'")
admins = cur.fetchall()

print("=== USUARIOS ADMINISTRADORES ===")
if admins:
    for admin in admins:
        print(f"ID: {admin[0]} | Email: {admin[1]} | Nombre: {admin[2]} | Tipo: {admin[3]}")
    print(f"\nTotal: {len(admins)} administrador(es)")
    
    # Mostrar las credenciales del primer admin
    print(f"\n📧 Email: {admins[0][1]}")
    print(f"🔑 Contraseña: [Revisa los registros o resetea con password123]")
else:
    print("No hay administradores. Creando uno nuevo...")
    
    # Crear usuario administrador
    admin_email = "admin@prendeterock.com"
    admin_password = "Admin123!!"
    admin_nombre = "Administrador Sistema"
    
    password_hash = hash_password(admin_password)
    
    cur.execute("""
        INSERT INTO Usuarios (Email, password_user, Nombre, Tipo)
        VALUES (?, ?, ?, 'admin')
    """, (admin_email, password_hash, admin_nombre))
    
    conn.commit()
    
    print(f"\n✅ Administrador creado exitosamente:")
    print(f"   📧 Email: {admin_email}")
    print(f"   🔑 Contraseña: {admin_password}")
    print(f"   👤 Tipo: admin")

conn.close()
