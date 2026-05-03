"""Actualiza los passwords de los usuarios de prueba al formato PBKDF2 del backend."""
import hashlib
import secrets
import psycopg2

def hash_password(pw: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 100_000)
    return f"{salt}${h.hex()}"

conn = psycopg2.connect(
    host="localhost", port=5432,
    dbname="PrendeteRock", user="postgres", password="Pasteldepapas123#"
)
cur = conn.cursor()

cur.execute("UPDATE usuarios SET password_user = %s WHERE email = %s",
            (hash_password("Admin1234!"), "admin_101221@prendeterock.com"))
cur.execute("UPDATE usuarios SET password_user = %s WHERE email = %s",
            (hash_password("Cliente1234!"), "cliente_101221@prendeterock.com"))
conn.commit()

cur.execute("SELECT email, LEFT(password_user, 20) FROM usuarios ORDER BY id_usuario LIMIT 3")
for r in cur.fetchall():
    print(r)
conn.close()
print("✓ Passwords actualizados con PBKDF2-HMAC-SHA256")
