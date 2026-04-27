import pyodbc

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=.\\SQLEXPRESS01;'
    'DATABASE=PrendeteRock;'
    'Trusted_Connection=yes;'
)

cur = conn.cursor()

print('\n=== Columnas de Variante_Atributos ===')
cur.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Variante_Atributos'")
for row in cur.fetchall():
    print(f'  - {row[0]} ({row[1]})')

print('\n=== Columnas de Producto_Atributos ===')
cur.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Producto_Atributos'")
for row in cur.fetchall():
    print(f'  - {row[0]} ({row[1]})')

conn.close()
