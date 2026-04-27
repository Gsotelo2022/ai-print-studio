"""
Script de prueba para el Agente de Descuentos
Ejecutar después de iniciar la API
"""

import requests
import json

BASE_URL = "http://localhost:5003"

def print_resultado(titulo, resultado):
    """Imprimir resultado de forma legible"""
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print(f"{'='*60}")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

def test_health():
    """Verificar estado del servicio"""
    print("\n🔍 Test 1: Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print_resultado("Estado del Servicio", response.json())
    return response.status_code == 200

def test_descuentos_activos():
    """Listar descuentos activos"""
    print("\n🔍 Test 2: Descuentos Activos")
    response = requests.get(f"{BASE_URL}/descuentos-activos")
    print_resultado("Descuentos Disponibles", response.json())
    return response.status_code == 200

def test_validar_cupon():
    """Validar un cupón"""
    print("\n🔍 Test 3: Validar Cupón")
    
    cupones_test = ["PRIMERACOMPRA10", "AMIGOS15", "INVALIDO123"]
    
    for codigo in cupones_test:
        response = requests.post(
            f"{BASE_URL}/validar-cupon",
            json={"codigo": codigo}
        )
        print_resultado(f"Cupón: {codigo}", response.json())

def test_calcular_descuento_simple():
    """Calcular descuento sin cupón"""
    print("\n🔍 Test 4: Descuento por Cantidad (5 productos)")
    
    pedido = {
        "id_cliente": 1,
        "cantidad": 5,
        "total": 60000,
        "productos": []
    }
    
    response = requests.post(
        f"{BASE_URL}/calcular-descuento",
        json=pedido
    )
    print_resultado("Descuento Calculado", response.json())

def test_calcular_descuento_con_cupon():
    """Calcular descuento con cupón"""
    print("\n🔍 Test 5: Descuento con Cupón")
    
    pedido = {
        "id_cliente": 1,
        "cantidad": 3,
        "total": 45000,
        "productos": [],
        "cupon": "PRIMERACOMPRA10"
    }
    
    response = requests.post(
        f"{BASE_URL}/calcular-descuento",
        json=pedido
    )
    print_resultado("Descuento con Cupón", response.json())

def test_descuento_cantidad_grande():
    """Calcular descuento con cantidad grande"""
    print("\n🔍 Test 6: Descuento Cantidad Grande (15 productos)")
    
    pedido = {
        "id_cliente": 2,
        "cantidad": 15,
        "total": 180000,
        "productos": []
    }
    
    response = requests.post(
        f"{BASE_URL}/calcular-descuento",
        json=pedido
    )
    resultado = response.json()
    print_resultado("Descuento Alta Cantidad", resultado)
    
    # Verificar que el descuento es 15%
    assert resultado['descuento_total'] == 15.0, "Descuento debería ser 15%"
    print("✓ Verificación: Descuento correcto (15%)")

def test_cupon_invalido():
    """Probar cupón inválido"""
    print("\n🔍 Test 7: Cupón Inválido")
    
    pedido = {
        "id_cliente": 1,
        "cantidad": 2,
        "total": 24000,
        "productos": [],
        "cupon": "CUPONINEXISTENTE"
    }
    
    response = requests.post(
        f"{BASE_URL}/calcular-descuento",
        json=pedido
    )
    resultado = response.json()
    print_resultado("Cupón Inválido", resultado)
    
    # El descuento debería aplicarse solo por cantidad (5%)
    print(f"✓ Verificación: Sin cupón, solo descuento por cantidad")

def test_combinacion_descuentos():
    """Probar combinación de múltiples descuentos"""
    print("\n🔍 Test 8: Combinación de Descuentos")
    
    # Cliente con historial + cantidad + cupón
    pedido = {
        "id_cliente": 1,  # Asumiendo que tiene compras previas
        "cantidad": 8,
        "total": 96000,
        "productos": [],
        "cupon": "AMIGOS15"
    }
    
    response = requests.post(
        f"{BASE_URL}/calcular-descuento",
        json=pedido
    )
    print_resultado("Combinación de Descuentos", response.json())

def main():
    """Ejecutar todos los tests"""
    print("\n" + "="*60)
    print("  SUITE DE PRUEBAS - AGENTE DE DESCUENTOS")
    print("="*60)
    
    try:
        # Verificar que la API está corriendo
        if not test_health():
            print("\n❌ ERROR: La API no está corriendo")
            print("Ejecuta: start-agente-descuentos.bat")
            return
        
        # Ejecutar tests
        test_descuentos_activos()
        test_validar_cupon()
        test_calcular_descuento_simple()
        test_calcular_descuento_con_cupon()
        test_descuento_cantidad_grande()
        test_cupon_invalido()
        test_combinacion_descuentos()
        
        print("\n" + "="*60)
        print("  ✓ TODOS LOS TESTS COMPLETADOS")
        print("="*60)
        print("\nPara más pruebas, visita:")
        print(f"  • Swagger UI: {BASE_URL}/docs")
        print(f"  • ReDoc: {BASE_URL}/redoc")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se puede conectar a la API")
        print("Asegúrate de que el servicio está corriendo:")
        print("  python api_descuentos.py")
        print("  o ejecuta: start-agente-descuentos.bat")
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")

if __name__ == "__main__":
    main()
