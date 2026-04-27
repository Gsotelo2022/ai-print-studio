"""
Script para ver la estructura de la tabla Productos
"""
import pyodbc

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=.\\SQLEXPRESS01;'
    'DATABASE=PrendeteRock;'
    'Trusted_Connection=yes;'
)

cursor = conn.cursor()

# Ver columnas de la tabla Productos
print('Columnas de la tabla Productos:')
cursor.execute("""
    SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'Productos'
    ORDER BY ORDINAL_POSITION
""")

for row in cursor.fetchall():
    print(f'  - {row[0]} ({row[1]})')

print()

# Ver primeros 3 registros completos
cursor.execute('SELECT TOP 3 * FROM Productos')
columns = [column[0] for column in cursor.description]
print('Columnas encontradas:', columns)
print()
print('Primeros 3 productos:')
for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()
