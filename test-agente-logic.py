import pyodbc
import json

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=.\\SQLEXPRESS01;'
    'DATABASE=PrendeteRock;'
    'Trusted_Connection=yes;'
)

cursor = conn.cursor()

query = """
SELECT 
    p.id_producto,
    p.nombre,
    pv.precio,
    pv.id_variante,
    pa.nombre,
    pav.valor
FROM Productos p
INNER JOIN Producto_Variantes pv ON p.id_producto = pv.id_producto
LEFT JOIN Variante_Atributos va ON pv.id_variante = va.id_variante
LEFT JOIN Producto_Atributo_Valores pav ON va.id_valor = pav.id_valor
LEFT JOIN Producto_Atributos pa ON pav.id_atributo = pa.id_atributo
WHERE p.activo = 1 AND pv.activo = 1
ORDER BY p.id_producto
"""

cursor.execute(query)
rows = cursor.fetchall()

productos_map = {}
variantes_map = {}

for row in rows:
    id_producto = row[0]
    nombre = row[1]
    precio = float(row[2]) if row[2] else 0
    id_variante = row[3]
    attr_name = row[4]
    attr_value = row[5]

    if id_producto not in productos_map:
        productos_map[id_producto] = {
            "id_producto": id_producto,
            "Detalle": nombre,
            "precio": precio,
            "talles": set(),
            "colores": set(),
            "variantes": []
        }

    # atributos
    if attr_name == "Talle" and attr_value:
        productos_map[id_producto]["talles"].add(attr_value)

    if attr_name == "Color" and attr_value:
        productos_map[id_producto]["colores"].add(attr_value)

    # Agrupar atributos por variante
    if id_variante:
        if id_variante not in variantes_map:
            variantes_map[id_variante] = {
                "id_variante": id_variante,
                "id_producto": id_producto,
                "talle": None,
                "color": None,
                "precio": precio
            }
        
        if attr_name == "Talle" and attr_value:
            variantes_map[id_variante]["talle"] = attr_value
        elif attr_name == "Color" and attr_value:
            variantes_map[id_variante]["color"] = attr_value

# Agregar variantes agrupadas a productos
for id_variante, variante_data in variantes_map.items():
    id_producto = variante_data["id_producto"]
    if id_producto in productos_map:
        productos_map[id_producto]["variantes"].append({
            "id_variante": variante_data["id_variante"],
            "talle": variante_data["talle"],
            "color": variante_data["color"],
            "precio": variante_data["precio"]
        })

# Formato final
productos = []
for info in productos_map.values():
    productos.append({
        "id_producto": info["id_producto"],
        "producto": info["Detalle"],
        "talles": sorted(list(info["talles"])),
        "colores": sorted(list(info["colores"])),
        "precio": info["precio"],
        "variantes": info["variantes"]
    })

print(f"✅ Total productos: {len(productos)}")
if productos:
    primer = productos[0]
    print(f"\n📦 Primer producto:")
    print(f"   ID: {primer['id_producto']}")
    print(f"   Nombre: {primer['producto']}")
    print(f"   Precio: ${primer['precio']}")
    print(f"   Variantes: {len(primer['variantes'])}")
    
    if primer['variantes']:
        v = primer['variantes'][0]
        print(f"\n🔍 Primera variante:")
        print(f"   ID: {v['id_variante']}")
        print(f"   Talle: {v['talle'] or 'N/A'}")
        print(f"   Color: {v['color'] or 'N/A'}")
        print(f"   Precio: ${v['precio']}")

conn.close()
