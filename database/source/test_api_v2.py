"""
================================================================================
SCRIPT DE PRUEBA - API V2
================================================================================
Descripción: Testear todos los endpoints del nuevo backend
Fecha: 22 de abril de 2026
================================================================================
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = 'http://localhost:8000/api'
TEST_USER = {
    'fullname': 'Usuario Test',
    'email': f'test_{datetime.now().timestamp()}@example.com',
    'phone': '+54 11 1234-5678',
    'password': 'test123456'
}

# ============================================================
# UTILIDADES
# ============================================================

def print_test(name):
    """Imprimir encabezado de test"""
    print(f"\n{'=' * 60}")
    print(f"🧪 TEST: {name}")
    print('=' * 60)


def print_result(success, message, data=None):
    """Imprimir resultado de test"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")
    if data:
        print(f"   Datos: {json.dumps(data, indent=2, ensure_ascii=False)}")


# ============================================================
# TESTS
# ============================================================

def test_health():
    """Test: Health check"""
    print_test("Health Check")
    try:
        response = requests.get(f'{BASE_URL}/health')
        data = response.json()
        
        if data.get('success') and data.get('data', {}).get('status') == 'ok':
            print_result(True, "Servidor FastAPI está funcionando", data['data'])
            return True
        else:
            print_result(False, "Respuesta inesperada", data)
            return False
    except Exception as e:
        print_result(False, f"Error de conexión: {e}")
        return False


def test_register():
    """Test: Registrar usuario"""
    print_test("Registro de Usuario")
    try:
        response = requests.post(f'{BASE_URL}/register', json=TEST_USER)
        data = response.json()
        
        if data.get('success'):
            user_id = data['data']['user_id']
            print_result(True, f"Usuario registrado con ID: {user_id}", data['data'])
            return user_id
        else:
            print_result(False, f"Error al registrar: {data.get('error')}")
            return None
    except Exception as e:
        print_result(False, f"Excepción: {e}")
        return None


def test_login():
    """Test: Login de usuario"""
    print_test("Login de Usuario")
    try:
        login_data = {
            'email': TEST_USER['email'],
            'password': TEST_USER['password']
        }
        response = requests.post(f'{BASE_URL}/login', json=login_data)
        data = response.json()
        
        if data.get('success'):
            user_id = data['data']['user_id']
            print_result(True, f"Login exitoso, user_id: {user_id}", data['data'])
            return user_id
        else:
            print_result(False, f"Error al hacer login: {data.get('error')}")
            return None
    except Exception as e:
        print_result(False, f"Excepción: {e}")
        return None


def test_get_productos():
    """Test: Obtener catálogo de productos"""
    print_test("Obtener Catálogo de Productos")
    try:
        response = requests.get(f'{BASE_URL}/productos')
        data = response.json()
        
        if data.get('success'):
            productos = data['data']
            print_result(True, f"Se obtuvieron {len(productos)} productos")
            
            for prod in productos[:2]:  # Mostrar primeros 2
                print(f"\n   📦 {prod['nombre']}")
                print(f"      Categoría: {prod['categoria']}")
                print(f"      Variantes: {len(prod['variantes'])}")
                print(f"      Precio desde: ${prod['precio_desde']}")
                
                if prod['variantes']:
                    var = prod['variantes'][0]
                    print(f"      Ejemplo variante: {var['sku']} - ${var['precio']} (Stock: {var['stock']})")
            
            return productos
        else:
            print_result(False, f"Error: {data.get('error')}")
            return None
    except Exception as e:
        print_result(False, f"Excepción: {e}")
        return None


def test_get_variante(id_variante):
    """Test: Obtener detalles de variante"""
    print_test(f"Obtener Variante ID {id_variante}")
    try:
        response = requests.get(f'{BASE_URL}/variante/{id_variante}')
        data = response.json()
        
        if data.get('success'):
            var = data['data']
            print_result(True, f"Variante: {var['sku']}")
            print(f"   Producto: {var['producto_nombre']}")
            print(f"   Precio: ${var['precio']}")
            print(f"   Stock: {var['stock']}")
            print(f"   Atributos: {var['atributos']}")
            return var
        else:
            print_result(False, f"Error: {data.get('error')}")
            return None
    except Exception as e:
        print_result(False, f"Excepción: {e}")
        return None


def test_create_order(user_id, variantes):
    """Test: Crear pedido"""
    print_test("Crear Pedido Multi-Item")
    try:
        # Crear pedido con 2 items de diferentes variantes
        order_data = {
            "user_id": user_id,
            "items": [
                {
                    "id_variante": variantes[0]['id_variante'],
                    "cantidad": 2,
                    "posicion_x": 100,
                    "posicion_y": 150,
                    "zoom": 1.2
                },
                {
                    "id_variante": variantes[1]['id_variante'],
                    "cantidad": 1,
                    "posicion_x": 50,
                    "posicion_y": 75,
                    "zoom": 1.0
                }
            ],
            "direccion_envio": "Av. Corrientes 1234",
            "ciudad": "Buenos Aires",
            "telefono_contacto": "+54 11 1234-5678",
            "notas_cliente": "Test automatizado"
        }
        
        response = requests.post(f'{BASE_URL}/create-order', json=order_data)
        data = response.json()
        
        if data.get('success'):
            pedido = data['data']
            print_result(True, f"Pedido creado: {pedido['numero_orden']}")
            print(f"   ID: {pedido['order_id']}")
            print(f"   Total: ${pedido['total']}")
            print(f"   Items: {pedido['items_count']}")
            return pedido['order_id']
        else:
            print_result(False, f"Error: {data.get('error')}")
            return None
    except Exception as e:
        print_result(False, f"Excepción: {e}")
        return None


def test_admin_pedidos():
    """Test: Listar pedidos (Admin)"""
    print_test("Admin - Listar Pedidos")
    try:
        response = requests.get(f'{BASE_URL}/admin/pedidos?filtro=todos')
        data = response.json()
        
        if data.get('success'):
            pedidos = data['data']
            print_result(True, f"Se obtuvieron {len(pedidos)} pedidos")
            
            if pedidos:
                ped = pedidos[0]
                print(f"\n   📦 Pedido: {ped['numero_orden']}")
                print(f"      Estado: {ped['estado']} | Pago: {ped['estado_pago']}")
                print(f"      Total: ${ped['total']}")
                print(f"      Cliente: {ped['cliente']['nombre']}")
            
            return True
        else:
            print_result(False, f"Error: {data.get('error')}")
            return False
    except Exception as e:
        print_result(False, f"Excepción: {e}")
        return False


def test_admin_clientes():
    """Test: Listar clientes (Admin)"""
    print_test("Admin - Listar Clientes")
    try:
        response = requests.get(f'{BASE_URL}/admin/clientes')
        data = response.json()
        
        if data.get('success'):
            clientes = data['data']
            print_result(True, f"Se obtuvieron {len(clientes)} clientes")
            
            if clientes:
                cli = clientes[0]
                print(f"\n   👤 Cliente: {cli['nombre']}")
                print(f"      Email: {cli['email']}")
                print(f"      Pedidos: {cli['pedidos']}")
                print(f"      Total gastado: ${cli['totalGastado']}")
            
            return True
        else:
            print_result(False, f"Error: {data.get('error')}")
            return False
    except Exception as e:
        print_result(False, f"Excepción: {e}")
        return False


def test_admin_metricas():
    """Test: Dashboard métricas (Admin)"""
    print_test("Admin - Dashboard Métricas")
    try:
        response = requests.get(f'{BASE_URL}/admin/dashboard/metricas')
        data = response.json()
        
        if data.get('success'):
            metricas = data['data']
            print_result(True, "Métricas obtenidas")
            print(f"\n   📊 HOY:")
            print(f"      Pedidos: {metricas['hoy']['pedidos']}")
            print(f"      Ventas: ${metricas['hoy']['ventas']}")
            print(f"\n   📊 MES:")
            print(f"      Pedidos: {metricas['mes']['pedidos']}")
            print(f"      Ventas: ${metricas['mes']['ventas']}")
            print(f"\n   ⚠️  Pendientes: {metricas['pedidos_pendientes']}")
            print(f"   ⚠️  Stock bajo: {metricas['stock_bajo']}")
            
            if metricas['top_productos']:
                print(f"\n   🏆 TOP PRODUCTOS:")
                for idx, prod in enumerate(metricas['top_productos'][:3], 1):
                    print(f"      {idx}. {prod['nombre']} - {prod['unidades']} unidades")
            
            return True
        else:
            print_result(False, f"Error: {data.get('error')}")
            return False
    except Exception as e:
        print_result(False, f"Excepción: {e}")
        return False


def test_admin_update_pedido(id_pedido):
    """Test: Actualizar estado de pedido"""
    print_test(f"Admin - Actualizar Pedido #{id_pedido}")
    try:
        # Cambiar a producción
        response = requests.put(
            f'{BASE_URL}/admin/pedidos/{id_pedido}/estado',
            json={'estado': 'produccion'}
        )
        data = response.json()
        
        if data.get('success'):
            print_result(True, "Estado actualizado a 'produccion'", data['data'])
            
            # Aprobar pago
            response = requests.put(
                f'{BASE_URL}/admin/pedidos/{id_pedido}/pago',
                json={
                    'estado_pago': 'aprobado',
                    'metodo_pago': 'test',
                    'referencia_externa': 'TEST-123456'
                }
            )
            data = response.json()
            
            if data.get('success'):
                print_result(True, "Pago aprobado", data['data'])
                return True
            else:
                print_result(False, f"Error al aprobar pago: {data.get('error')}")
                return False
        else:
            print_result(False, f"Error: {data.get('error')}")
            return False
    except Exception as e:
        print_result(False, f"Excepción: {e}")
        return False


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================

def main():
    """Ejecutar todos los tests"""
    print("\n" + "=" * 60)
    print("🧪 SUITE DE PRUEBAS - API V2")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    resultados = {
        'total': 0,
        'exitosos': 0,
        'fallidos': 0
    }
    
    # Test 1: Health check
    resultados['total'] += 1
    if test_health():
        resultados['exitosos'] += 1
    else:
        resultados['fallidos'] += 1
        print("\n⚠️  Backend no responde. Verifica que esté ejecutándose.")
        return
    
    # Test 2: Registro
    resultados['total'] += 1
    user_id = test_register()
    if user_id:
        resultados['exitosos'] += 1
    else:
        resultados['fallidos'] += 1
    
    # Test 3: Login
    resultados['total'] += 1
    if test_login():
        resultados['exitosos'] += 1
    else:
        resultados['fallidos'] += 1
    
    # Test 4: Obtener productos
    resultados['total'] += 1
    productos = test_get_productos()
    if productos:
        resultados['exitosos'] += 1
    else:
        resultados['fallidos'] += 1
        print("\n⚠️  No se pudieron obtener productos. Verifica la BD.")
        return
    
    # Test 5: Obtener variante
    if productos and productos[0]['variantes']:
        resultados['total'] += 1
        id_var = productos[0]['variantes'][0]['id_variante']
        if test_get_variante(id_var):
            resultados['exitosos'] += 1
        else:
            resultados['fallidos'] += 1
    
    # Test 6: Crear pedido
    if user_id and productos and len(productos[0]['variantes']) >= 2:
        resultados['total'] += 1
        variantes = productos[0]['variantes'][:2]
        id_pedido = test_create_order(user_id, variantes)
        if id_pedido:
            resultados['exitosos'] += 1
            
            # Test 7: Actualizar pedido
            resultados['total'] += 1
            if test_admin_update_pedido(id_pedido):
                resultados['exitosos'] += 1
            else:
                resultados['fallidos'] += 1
        else:
            resultados['fallidos'] += 1
    
    # Test 8: Admin - Pedidos
    resultados['total'] += 1
    if test_admin_pedidos():
        resultados['exitosos'] += 1
    else:
        resultados['fallidos'] += 1
    
    # Test 9: Admin - Clientes
    resultados['total'] += 1
    if test_admin_clientes():
        resultados['exitosos'] += 1
    else:
        resultados['fallidos'] += 1
    
    # Test 10: Admin - Métricas
    resultados['total'] += 1
    if test_admin_metricas():
        resultados['exitosos'] += 1
    else:
        resultados['fallidos'] += 1
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS")
    print("=" * 60)
    print(f"Total ejecutados: {resultados['total']}")
    print(f"✅ Exitosos: {resultados['exitosos']}")
    print(f"❌ Fallidos: {resultados['fallidos']}")
    
    porcentaje = (resultados['exitosos'] / resultados['total'] * 100) if resultados['total'] > 0 else 0
    print(f"\n🎯 Tasa de éxito: {porcentaje:.1f}%")
    
    if resultados['fallidos'] == 0:
        print("\n🎉 ¡TODOS LOS TESTS PASARON! Backend v2 funcionando correctamente.")
    else:
        print(f"\n⚠️  Hay {resultados['fallidos']} tests fallidos. Revisar errores arriba.")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrumpidos por el usuario.")
    except Exception as e:
        print(f"\n\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
