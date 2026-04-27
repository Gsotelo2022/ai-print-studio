import pyodbc

conn = pyodbc.connect(
    'DRIVER={SQL Server};'
    'SERVER=localhost\SQLEXPRESS01;'
    'DATABASE=PrendeteRock;'
    'Trusted_Connection=yes;'
)

cur = conn.cursor()

# Ver productos duplicados
cur.execute("""
SELECT 
    p.id_producto, 
    p.nombre, 
    p.descripcion,
    COUNT(pv.id_variante) as num_variantes
FROM Productos p 
LEFT JOIN Producto_Variantes pv ON p.id_producto = pv.id_producto
WHERE p.activo = 1
GROUP BY p.id_producto, p.nombre, p.descripcion
ORDER BY p.nombre, p.id_producto
""")

print("=== TODOS LOS PRODUCTOS ===")
rows = cur.fetchall()
for r in rows:
    desc = r[2][:30] if r[2] else "Sin descripción"
    print(f"ID {r[0]}: {r[1]:15s} - {r[3]:2d} variantes - {desc}")

print(f"\nTotal productos: {len(rows)}")

# Ver específicamente Caja con sus variantes
print("\n=== DETALLE DE 'CAJA' ===")
cur.execute("""
SELECT 
    p.id_producto,
    p.nombre,
    pv.id_variante,
    pv.sku,
    pa.nombre as atributo,
    pav.valor
FROM Productos p
LEFT JOIN Producto_Variantes pv ON p.id_producto = pv.id_producto
LEFT JOIN Variante_Atributos va ON pv.id_variante = va.id_variante
LEFT JOIN Producto_Atributos pa ON va.id_atributo = pa.id_atributo
LEFT JOIN Producto_Atributo_Valores pav ON va.id_valor = pav.id_valor
WHERE p.nombre LIKE '%Caja%' AND p.activo = 1
ORDER BY p.id_producto, pv.id_variante
""")

cajas = cur.fetchall()
if cajas:
    for c in cajas:
        if c[2]:  # tiene variante
            print(f"Prod {c[0]} ({c[1]}): Variante {c[2]} - SKU: {c[3]} - {c[4]}: {c[5]}")
        else:
            print(f"Prod {c[0]} ({c[1]}): SIN VARIANTES")
else:
    print("No se encontraron productos 'Caja'")

conn.close()
