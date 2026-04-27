import pyodbc

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=.\\SQLEXPRESS01;'
    'DATABASE=PrendeteRock;'
    'Trusted_Connection=yes;'
)

cursor = conn.cursor()

# Ver todos los tipos de usuario
cursor.execute("""
    SELECT id_usuario, Nombre, Email, Tipo
    FROM Usuarios
    ORDER BY Tipo, id_usuario
""")

print("=== Usuarios en la base de datos ===\n")
for row in cursor.fetchall():
    id_usuario, nombre, email, tipo = row
    print(f"ID: {id_usuario:3d} | Tipo: {tipo:15s} | Nombre: {nombre:20s} | Email: {email}")

print("\n=== Tipos únicos ===")
cursor.execute("""
    SELECT DISTINCT Tipo, COUNT(*) as cantidad
    FROM Usuarios
    GROUP BY Tipo
""")

for row in cursor.fetchall():
    tipo, cantidad = row
    print(f"  - '{tipo}' ({cantidad} usuarios)")

conn.close()
