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

# Resetear contraseña del admin
admin_email = "admin@prendeterock.com"
nueva_password = "Admin123!!"

password_hash = hash_password(nueva_password)

cur.execute("""
    UPDATE Usuarios
    SET password_user = ?
    WHERE Email = ?
""", (password_hash, admin_email))

conn.commit()

print("✅ Contraseña de administrador reseteada exitosamente:")
print(f"\n📧 Email: {admin_email}")
print(f"🔑 Contraseña: {nueva_password}")
print(f"\n👉 Usa estas credenciales para iniciar sesión como administrador")

conn.close()
