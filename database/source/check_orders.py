from db import get_connection

conn = get_connection()
cur = conn.cursor()

print("PEDIDOS:")
cur.execute("SELECT COUNT(*) FROM Pedidos")
row = cur.fetchone()
print("Total de pedidos:", row[0])

cur.execute("SELECT id_pedido, id_usuario FROM Pedidos ORDER BY id_pedido DESC")
rows = cur.fetchall()
for row in rows:
    print("  Pedido ID:", row[0], "Usuario ID:", row[1])

print("\nDETALLES DE PEDIDOS:")
cur.execute("SELECT COUNT(*) FROM Pedidos_detalle")
row = cur.fetchone()
print("Total de detalles:", row[0])

cur.execute("SELECT TOP 5 id_detalle, id_pedido, estado, pago, total FROM Pedidos_detalle ORDER BY id_detalle DESC")
rows = cur.fetchall()
for row in rows:
    print("  Detalle ID:", row[0], "Pedido ID:", row[1], "Estado:", row[2], "Pago:", row[3], "Total:", row[4])

cur.close()
conn.close()
print("\nConsulta completada.")
