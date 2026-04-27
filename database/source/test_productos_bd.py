"""
Script para verificar productos en la BD
"""
import pyodbc

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=.\\SQLEXPRESS01;'
    'DATABASE=PrendeteRock;'
    'Trusted_Connection=yes;'
)

cursor = conn.cursor()

# Contar productos
cursor.execute('SELECT COUNT(*) FROM Productos')
total = cursor.fetchone()[0]
print(f'Total productos en BD: {total}')
print()

# Ver primeros 5
cursor.execute('SELECT TOP 5 id_producto, Detalle, Color, talle, precio FROM Productos')
print('Primeros 5 productos:')
for row in cursor.fetchall():
    print(f'  ID:{row[0]} - {row[1]} | Color:{row[2]} | Talle:{row[3]} | Precio:{row[4]}')

cursor.close()
conn.close()
