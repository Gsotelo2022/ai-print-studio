"""
Script para obtener productos con sus variantes (talles, colores, precios)
usando la nueva estructura normalizada de BD
"""
import pyodbc
import json

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=.\\SQLEXPRESS01;'
    'DATABASE=PrendeteRock;'
    'Trusted_Connection=yes;'
)

cursor = conn.cursor()

# Query para obtener productos con sus variantes
query = """
SELECT 
    p.id_producto,
    p.nombre,
    pv.id_variante,
    pv.sku,
    pv.precio,
    pv.stock_actual,
    pa.nombre as atributo_nombre,
    pav.valor as atributo_valor
FROM Productos p
INNER JOIN Producto_Variantes pv ON p.id_producto = pv.id_producto
LEFT JOIN Variante_Atributos va ON pv.id_variante = va.id_variante
LEFT JOIN Producto_Atributos pa ON va.id_atributo = pa.id_atributo
LEFT JOIN Producto_Atributo_Valores pav ON va.id_valor = pav.id_valor
WHERE p.activo = 1 AND pv.activo = 1
ORDER BY p.id_producto, pv.id_variante
"""

print("Ejecutando consulta...")
cursor.execute(query)

# Agrupar productos
productos_agrupados = {}

for row in cursor.fetchall():
    id_producto = row[0]
    nombre = row[1]
    precio = float(row[4]) if row[4] else 0
    atributo_nombre = row[6]
    atributo_valor = row[7]
    
    if nombre not in productos_agrupados:
        productos_agrupados[nombre] = {
            'id_producto': id_producto,
            'producto': nombre,
            'talles': set(),
            'colores': set(),
            'precio': precio  # Tomamos el primer precio que encontramos
        }
    
    # Agregar talles y colores
    if atributo_nombre == 'Talle' and atributo_valor:
        productos_agrupados[nombre]['talles'].add(atributo_valor)
    elif atributo_nombre == 'Color' and atributo_valor:
        productos_agrupados[nombre]['colores'].add(atributo_valor)

# Convertir a formato del agente
resultado = []
for nombre, datos in productos_agrupados.items():
    resultado.append({
        'id_producto': datos['id_producto'],
        'producto': nombre,
        'talles': sorted(list(datos['talles'])),
        'colores': sorted(list(datos['colores'])),
        'precio': datos['precio']
    })

print("\n" + "="*60)
print("PRODUCTOS AGRUPADOS CON VARIANTES:")
print("="*60)
print(json.dumps(resultado, indent=2, ensure_ascii=False))
print(f"\nTotal: {len(resultado)} productos")

cursor.close()
conn.close()
