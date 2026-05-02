import psycopg2
import os
import hashlib
import secrets

def hash_password(pw: str) -> str:
    """Hashear contraseña con PBKDF2 (SHA256)"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', pw.encode(), bytes.fromhex(salt), 100000)
    return f"{salt}${hash_obj.hex()}"

conn = psycopg2.connect(
    host=os.getenv("PG_HOST", "127.0.0.1"),
    port=int(os.getenv("PG_PORT", "5432")),
    dbname=os.getenv("PG_DB", "PrendeteRock"),
    user=os.getenv("PG_USER", "postgres"),
    password=os.getenv("PG_PASSWORD", ""),
    connect_timeout=5,
    sslmode="disable"
)

cur = conn.cursor()

# Resetear contraseña del admin
admin_email = "admin@prendeterock.com"
nueva_password = "Admin123!!"

password_hash = hash_password(nueva_password)

cur.execute("""
    UPDATE Usuarios
    SET password_user = %s
    WHERE Email = %s
""", (password_hash, admin_email))

conn.commit()

print("✅ Contraseña de administrador reseteada exitosamente:")
print(f"\n📧 Email: {admin_email}")
print(f"🔑 Contraseña: {nueva_password}")
print(f"\n👉 Usa estas credenciales para iniciar sesión como administrador")

conn.close()
