"""
Test para verificar que el precio se guarda correctamente con descuento
cuando se aplica un cupón durante la creación de un pedido.

Este test verifica:
1. Servidor funcional
2. Cupón TEST50 existe (50% de descuento)
3. Crear pedido con cupón
4. Verificar que se guarden correctamente:
   - subtotal (precio original)
   - descuento (monto del descuento)
   - total (precio con descuento)

Autor: Sistema AI Print Studio
Fecha: 28/04/2026
"""

import sys
sys.path.append('../backend/api_python')

import requests
from datetime import datetime
from db import get_connection

BASE_URL = "http://localhost:8000"

print("\n" + "="*80)
print("🧪 TEST: Guardado de precio con descuento (cupón aplicado)")
print("="*80)

# PASO 1: Verificar servidor
print("\n1️⃣ Verificando servidor...")
try:
    response = requests.get(f"{BASE_URL}/api/health", timeout=5)
    if response.status_code == 200:
        print("   ✅ Servidor activo")
    else:
        print(f"   ⚠️  Servidor responde con status {response.status_code}")
except Exception as e:
    print(f"   ❌ Erro: {e}")
    print("   💡 Inicia el servidor primero")
    exit(1)

# PASO 2: Obtener datos de prueba
print("\n2️⃣ Obteniendo datos de prueba...")
conn = get_connection()
cur = conn.cursor()

# Buscar usuario de prueba
cur.execute("SELECT TOP 1 id_usuario, Nombre FROM Usuarios WHERE Tipo = 'cliente'")
usuario = cur.fetchone()

if not usuario:
    print("   ❌ No hay usuarios de prueba")
    conn.close()
    exit(1)

id_usuario = usuario[0]
nombre_usuario = usuario[1]
print(f"   ✅ Usuario: {nombre_usuario} (ID: {id_usuario})")

# Buscar variante de prueba
cur.execute("""
    SELECT TOP 1 pv.id_variante, p.nombre, pv.precio
    FROM Producto_Variantes pv
    INNER JOIN Productos p ON pv.id_producto = p.id_producto
    WHERE pv.activo = 1 AND pv.stock_actual > 0
    ORDER BY pv.precio DESC
""")

variante = cur.fetchone()

if not variante:
    print("   ❌ No hay variantes disponibles")
    conn.close()
    exit(1)

id_variante = variante[0]
nombre_producto = variante[1]
precio_unitario = float(variante[2])
print(f"   ✅ Producto: {nombre_producto} - ${precio_unitario:,.2f}")

# Verificar cupón TEST50
cur.execute("SELECT id_cupon, descuento_porcentaje FROM Cupones WHERE codigo = 'TEST50' AND activo = 1")
cupon = cur.fetchone()

if not cupon:
    print("   ⚠️  Cupón TEST50 no existe, sera usado cupon manual")
    cupon_codigo = "TEST50"
    cupon_descuento = 50
else:
    cupon_codigo = "TEST50"
    cupon_descuento = int(cupon[1])
    print(f"   ✅ Cupón: {cupon_codigo} (-{cupon_descuento}%)")

conn.close()

# PASO 3: Calcular valores esperados
print("\n3️⃣ Calculando valores esperados...")
cantidad = 1
subtotal_esperado = precio_unitario * cantidad
descuento_esperado = (subtotal_esperado * cupon_descuento) / 100
total_esperado = subtotal_esperado - descuento_esperado

print(f"   Subtotal:  ${subtotal_esperado:,.2f}")
print(f"   Descuento: -${descuento_esperado:,.2f} ({cupon_descuento}%)")
print(f"   Total:     ${total_esperado:,.2f}")

# PASO 4: Crear pedido CON cupón
print(f"\n4️⃣ Creando pedido con cupón {cupon_codigo}...")

payload = {
    "user_id": id_usuario,
    "items": [
        {
            "id_variante": id_variante,
            "cantidad": cantidad,
            "archivo_diseno": "https://ejemplo.com/diseno_test.png",
            "posicion_x": 0,
            "posicion_y": 0,
            "zoom": 1
        }
    ],
    "codigo_cupon": cupon_codigo,
    "direccion_envio": "Calle Test 456",
    "ciudad": "Test City",
    "telefono_contacto": "9876543210",
    "notas_cliente": f"Test automatizado - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
}

try:
    response = requests.post(f"{BASE_URL}/api/create-order", json=payload, timeout=15)
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get('success'):
            id_pedido = result['data']['order_id']  # Cambio aquí: order_id no id_pedido
            numero_orden = result['data']['numero_orden']
            print(f"   ✅ Pedido creado: {numero_orden} (ID: {id_pedido})")
        else:
            print(f"   ❌ Error en respuesta: {result}")
            exit(1)
    else:
        print(f"   ❌ Error HTTP {response.status_code}: {response.text}")
        exit(1)
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# PASO 5: Verificar valores en base de datos
print("\n5️⃣ Verificando valores guardados en BD...")

conn = get_connection()
cur = conn.cursor()

cur.execute("""
    SELECT subtotal, descuento, total
    FROM Pedidos
    WHERE id_pedido = ?
""", (id_pedido,))

pedido_bd = cur.fetchone()

if not pedido_bd:
    print("   ❌ No se encontró el pedido en la BD")
    conn.close()
    exit(1)

subtotal_bd = float(pedido_bd[0]) if pedido_bd[0] else 0
descuento_bd = float(pedido_bd[1]) if pedido_bd[1] else 0
total_bd = float(pedido_bd[2]) if pedido_bd[2] else 0

print(f"\n   📊 Valores en BD:")
print(f"      Subtotal:  ${subtotal_bd:,.2f}")
print(f"      Descuento: ${descuento_bd:,.2f}")
print(f"      Total:     ${total_bd:,.2f}")

conn.close()

# PASO 6: Validar valores
print("\n6️⃣ Validando...")

errores = []
tolerancia = 0.01  # Tolerancia de 1 centavo para comparaciones

# Validar subtotal
if abs(subtotal_bd - subtotal_esperado) > tolerancia:
    errores.append(f"   ❌ Subtotal incorrecto: esperado ${subtotal_esperado:,.2f}, BD ${subtotal_bd:,.2f}")
else:
    print(f"   ✅ Subtotal correcto: ${subtotal_bd:,.2f}")

# Validar descuento
if abs(descuento_bd - descuento_esperado) > tolerancia:
    errores.append(f"   ❌ Descuento incorrecto: esperado ${descuento_esperado:,.2f}, BD ${descuento_bd:,.2f}")
else:
    print(f"   ✅ Descuento correcto: ${descuento_bd:,.2f}")

# Validar total
if abs(total_bd - total_esperado) > tolerancia:
    errores.append(f"   ❌ Total incorrecto: esperado ${total_esperado:,.2f}, BD ${total_bd:,.2f}")
else:
    print(f"   ✅ Total correcto: ${total_bd:,.2f}")

# Validar fórmula: subtotal - descuento = total
total_calculado = subtotal_bd - descuento_bd
if abs(total_calculado - total_bd) > tolerancia:
    errores.append(f"   ❌ Fórmula incorrecta: ${subtotal_bd} - ${descuento_bd} ≠ ${total_bd}")
else:
    print(f"   ✅ Fórmula correcta: ${subtotal_bd:,.2f} - ${descuento_bd:,.2f} = ${total_bd:,.2f}")

# RESULTADO FINAL
print("\n" + "="*80)

if errores:
    print("❌ TEST FALLIDO\n")
    print("Errores encontrados:")
    for error in errores:
        print(error)
    print("\n💡 El sistema NO está guardando correctamente el precio con descuento")
    exit(1)
else:
    print("✅ TEST EXITOSO\n")
    print("El sistema guarda CORRECTAMENTE:")
    print(f"  • Subtotal: ${subtotal_bd:,.2f} (precio sin descuento)")
    print(f"  • Descuento: ${descuento_bd:,.2f} (monto del cupón)")
    print(f"  • Total: ${total_bd:,.2f} (precio final con descuento)")
    print(f"\n📦 Pedido creado: {numero_orden}")
    print(f"💰 El cliente pagará ${total_bd:,.2f} gracias al cupón {cupon_codigo}")

print("="*80 + "\n")
