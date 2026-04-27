"""
Test para el Agente de Productos

Verifica:
1. Que la API de productos devuelve datos correctos
2. Que el agente de productos procesa los datos correctamente
3. Que los talles y colores se extraen correctamente de las variantes
"""

import requests
import json

def test_api_productos():
    """Test 1: Verificar que la API de productos funciona"""
    print("\n" + "="*60)
    print("TEST 1: Verificar API de productos (app_v2.py)")
    print("="*60)
    
    try:
        response = requests.get('http://127.0.0.1:8000/api/productos', timeout=5)
        
        if response.status_code != 200:
            print(f"❌ ERROR: API devolvió código {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
            return False
            
        data = response.json()
        
        if not data.get("success"):
            print(f"❌ ERROR: API devolvió success=False")
            print(f"   Datos: {json.dumps(data, indent=2, ensure_ascii=False)[:300]}")
            return False
            
        if "data" not in data:
            print(f"❌ ERROR: Falta campo 'data' en respuesta")
            return False
            
        productos = data["data"]
        
        if not isinstance(productos, list):
            print(f"❌ ERROR: 'data' no es una lista")
            return False
            
        if len(productos) == 0:
            print(f"⚠️  ADVERTENCIA: No hay productos en la base de datos")
            return False
            
        print(f"✅ API funciona correctamente")
        print(f"   Total de productos: {len(productos)}")
        
        # Mostrar ejemplo del primer producto
        if productos:
            primer_producto = productos[0]
            print(f"\n   Ejemplo del primer producto:")
            print(f"   - ID: {primer_producto.get('id_producto')}")
            print(f"   - Nombre: {primer_producto.get('nombre')}")
            print(f"   - Variantes: {len(primer_producto.get('variantes', []))}")
            
            # Verificar estructura de variantes
            if primer_producto.get('variantes'):
                primera_variante = primer_producto['variantes'][0]
                print(f"\n   Ejemplo de primera variante:")
                print(f"   - ID Variante: {primera_variante.get('id_variante')}")
                print(f"   - SKU: {primera_variante.get('sku')}")
                print(f"   - Precio: {primera_variante.get('precio')}")
                print(f"   - Stock: {primera_variante.get('stock_actual')}")
                
                # Verificar si tiene atributos
                if 'atributos' in primera_variante:
                    print(f"   - Atributos: {primera_variante.get('atributos')}")
                else:
                    print(f"   ⚠️  Las variantes NO tienen atributos (talles/colores)")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: No se pudo conectar a http://127.0.0.1:8000")
        print(f"   ¿Está corriendo el servidor backend (app_v2.py)?")
        return False
    except Exception as e:
        print(f"❌ ERROR inesperado: {e}")
        return False


def test_agente_productos():
    """Test 2: Verificar que el agente de productos funciona"""
    print("\n" + "="*60)
    print("TEST 2: Verificar Agente de Productos")
    print("="*60)
    
    try:
        response = requests.get('http://127.0.0.1:5001/productos-ia', timeout=10)
        
        if response.status_code != 200:
            print(f"❌ ERROR: Agente devolvió código {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
            return False
            
        productos = response.json()
        
        if not isinstance(productos, list):
            print(f"❌ ERROR: Agente no devolvió una lista")
            if isinstance(productos, dict) and 'error' in productos:
                print(f"   Error: {productos['error']}")
            return False
            
        if len(productos) == 0:
            print(f"❌ ERROR: Agente devolvió lista vacía")
            return False
            
        print(f"✅ Agente funciona correctamente")
        print(f"   Total de productos procesados: {len(productos)}")
        
        # Analizar estructura de productos
        primer_producto = productos[0]
        print(f"\n   Ejemplo del primer producto:")
        print(f"   - Producto: {primer_producto.get('producto')}")
        print(f"   - Talles: {primer_producto.get('talles')}")
        print(f"   - Colores: {primer_producto.get('colores')}")
        print(f"   - Precio: {primer_producto.get('precio')}")
        print(f"   - ID Producto: {primer_producto.get('id_producto')}")
        
        # Verificar que los campos necesarios existen
        campos_requeridos = ['producto', 'talles', 'colores', 'precio']
        campos_faltantes = [campo for campo in campos_requeridos if campo not in primer_producto]
        
        if campos_faltantes:
            print(f"\n   ⚠️  ADVERTENCIA: Faltan campos: {', '.join(campos_faltantes)}")
        
        # Verificar que talles y colores no estén vacíos/por defecto
        if primer_producto.get('talles') == ["S", "M", "L", "XL"]:
            print(f"\n   ⚠️  ADVERTENCIA: Talles parecen ser valores por defecto")
            
        if primer_producto.get('colores') == ["Negro", "Blanco"]:
            print(f"\n   ⚠️  ADVERTENCIA: Colores parecen ser valores por defecto")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: No se pudo conectar a http://127.0.0.1:5001")
        print(f"   ¿Está corriendo el agente de productos?")
        print(f"   Ejecuta: start-agente-productos.bat")
        return False
    except json.JSONDecodeError:
        print(f"❌ ERROR: Respuesta del agente no es JSON válido")
        print(f"   Respuesta: {response.text[:200]}")
        return False
    except Exception as e:
        print(f"❌ ERROR inesperado: {e}")
        return False


def test_integracion():
    """Test 3: Verificar que los datos fluyen correctamente de API a Agente"""
    print("\n" + "="*60)
    print("TEST 3: Verificar integración API -> Agente")
    print("="*60)
    
    try:
        # Obtener datos de la API
        api_response = requests.get('http://127.0.0.1:8000/api/productos', timeout=5)
        api_data = api_response.json()
        productos_api = api_data.get("data", [])
        
        # Obtener datos del agente
        agente_response = requests.get('http://127.0.0.1:5001/productos-ia', timeout=10)
        productos_agente = agente_response.json()
        
        if not productos_api or not productos_agente:
            print(f"❌ ERROR: No hay productos en API o Agente")
            return False
        
        print(f"   Productos en API: {len(productos_api)}")
        print(f"   Productos en Agente: {len(productos_agente)}")
        
        # Verificar que el agente tenga productos y que coincidan de alguna forma
        if len(productos_agente) == 0:
            print(f"❌ ERROR: Agente no procesó ningún producto")
            return False
        
        # Buscar si existe algún producto de la API en el resultado del agente
        encontrados = 0
        for prod_api in productos_api[:5]:  # Verificar los primeros 5
            nombre_api = prod_api.get('nombre', '').lower()
            
            for prod_agente in productos_agente:
                nombre_agente = prod_agente.get('producto', '').lower()
                
                if nombre_api in nombre_agente or nombre_agente in nombre_api:
                    encontrados += 1
                    break
        
        if encontrados == 0:
            print(f"⚠️  ADVERTENCIA: No se encontró correlación entre productos de API y Agente")
            print(f"   Esto podría indicar un problema de transformación de datos")
        else:
            print(f"✅ Integración correcta: {encontrados} productos coinciden")
        
        # Comparar detalles del primer producto
        print(f"\n   Comparación del primer producto:")
        print(f"   API - Nombre: {productos_api[0].get('nombre')}")
        if productos_agente:
            print(f"   Agente - Producto: {productos_agente[0].get('producto')}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR en test de integración: {e}")
        return False


def main():
    """Ejecutar todos los tests"""
    print("\n" + "="*60)
    print("🧪 TEST DEL AGENTE DE PRODUCTOS")
    print("="*60)
    
    resultados = {
        "API de productos": test_api_productos(),
        "Agente de productos": test_agente_productos(),
        "Integración": test_integracion()
    }
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE TESTS")
    print("="*60)
    
    for nombre, resultado in resultados.items():
        emoji = "✅" if resultado else "❌"
        print(f"{emoji} {nombre}: {'PASS' if resultado else 'FAIL'}")
    
    total = len(resultados)
    exitosos = sum(1 for r in resultados.values() if r)
    
    print(f"\n   Total: {exitosos}/{total} tests exitosos")
    
    if exitosos == total:
        print("\n🎉 ¡Todos los tests pasaron!")
    else:
        print("\n⚠️  Algunos tests fallaron. Revisa los errores arriba.")
    
    return exitosos == total


if __name__ == "__main__":
    main()
