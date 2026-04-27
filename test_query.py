import pyodbc
import json

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=.\\SQLEXPRESS01;'
    'DATABASE=PrendeteRock;'
    'Trusted_Connection=yes;'
)

cur = conn.cursor()

# Query corregida
query = """
SELECT 
    p.id_producto,        -- 0
    p.nombre,             -- 1
    pv.precio,            -- 2
    pv.id_variante,       -- 3
    pa.nombre,            -- 4
    pav.valor             -- 5
FROM Productos p
INNER JOIN Producto_Variantes pv ON p.id_producto = pv.id_producto
LEFT JOIN Variante_Atributos va ON pv.id_variante = va.id_variante
LEFT JOIN Producto_Atributo_Valores pav ON va.id_valor = pav.id_valor
LEFT JOIN Producto_Atributos pa ON pav.id_atributo = pa.id_atributo
WHERE p.activo = 1 AND pv.activo = 1
ORDER BY p.id_producto
"""

cur.execute(query)
rows = cur.fetchall()

print(f'✅ Filas encontradas: {len(rows)}')
if rows:
    print(f'\nPrimeras 5 filas:')
    for i, row in enumerate(rows[:5]):
        print(f'  {i+1}. ID={row[0]}, Producto={row[1]}, Precio={row[2]}, Variante={row[3]}, Attr={row[4]}, Valor={row[5]}')

conn.close()
