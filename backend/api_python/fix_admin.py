import psycopg2
import os
import hashlib
import secrets

def hash_password(pw: str) -> str:
    """Hashear contraseña con PBKDF2 (SHA256)"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', pw.encode(), bytes.fromhex(salt), 100000)
    return f"{salt}${hash_obj.hex()}"

try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        dbname="PrendeteRock",
        user="postgres",
        password="Pasteldepapas123#",
        connect_timeout=5,
        sslmode="disable"
    )

    cur = conn.cursor()

    admin_email = "admin_101221@prendeterock.com"
    nueva_password = "Admin1234!"
    password_hash = hash_password(nueva_password)

    # Primero verificar si existe
    cur.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (admin_email,))
    user = cur.fetchone()

    if user:
        cur.execute("""
            UPDATE usuarios
            SET password_user = %s, tipo = 'admin'
            WHERE email = %s
        """, (password_hash, admin_email))
        print(f"✅ Usuario {admin_email} actualizado.")
    else:
        cur.execute("""
            INSERT INTO usuarios (nombre, email, password_user, tipo)
            VALUES (%s, %s, %s, %s)
        """, ("Administrador", admin_email, password_hash, "admin"))
        print(f"✅ Usuario {admin_email} creado.")

    conn.commit()
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
