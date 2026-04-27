import urllib.request
import urllib.error
import json
import time

BASE_URL = "http://localhost:5003/api"

def print_step(msg):
    print(f"\n[{time.strftime('%H:%M:%S')}] 🚀 {msg}")

def print_success(msg):
    print(f"  ✅ {msg}")

def print_warning(msg):
    print(f"  ⚠️ {msg}")

def print_error(msg):
    print(f"  ❌ {msg}")

def request_api(method, endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    req_data = None
    if data:
        req_data = json.dumps(data).encode('utf-8')
        
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode())
        except:
            return {"success": False, "error": f"HTTP {e.code}"}
    except urllib.error.URLError as e:
        return {"success": False, "error": f"Connection refused: {e.reason}", "connection_error": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def run_tests():
    print("=========================================")
    print("  🧪 TESTS E2E: SISTEMA DE CUPONES E IA  ")
    print("=========================================")
    
    # 1. Verificar estado de la API HTTP GET
    print_step("Paso 1: Conectando con la API de Cupones...")
    res = request_api('GET', '/cupones')
    if res.get('connection_error'):
        print_error("No se pudo conectar a la API. ¿Está corriendo el Agente de Cupones en el puerto 5003?")
        return
    elif not res.get('success', True) and 'cupones' not in res: 
        print_error(f"La API respondió con error: {res}")
        return
        
    cupones_totales = res.get('total', len(res.get('cupones', [])))
    print_success(f"API conectada. Tienes {cupones_totales} cupones listados.")
    
    # 2. Crear cupón temporal
    print_step("Paso 2: Crear un cupón de prueba (POST /api/cupones)...")
    codigo_prueba = f"TEST{int(time.time())}"
    test_cupon = {
        "codigo": codigo_prueba,
        "descripcion": "Cupón de prueba E2E",
        "descuento_porcentaje": 15,
        "usos_maximos": 5
    }
    
    res = request_api('POST', '/cupones', test_cupon)
    if res.get('success') or res.get('codigo'):
        print_success(f"Cupón {codigo_prueba} creado correctamente en la base de datos.")
    else:
        print_error(f"Fallo al crear cupón: {res}")
        
    # 3. Validar Estadísticas
    print_step("Paso 3: Recuperar estadísticas en tiempo real (GET /api/estadisticas)...")
    res = request_api('GET', '/estadisticas')
    if res.get('success') or 'estadisticas' in res:
        print_success("Estadísticas obtenidas correctamente del backend.")
    else:
        print_error("Fallo al obtener las estadísticas.")
        
    # 4. Probar Motor de IA (Ollama)
    print_step("Paso 4: Solicitando propuestas a la IA (Ollama)...")
    print("  -> Esto enviará el contexto de las ventas al LLM y esperará por la deducción.")
    print("  -> (Por favor aguarda, la inferencia local puede tardar unos segundos...)")
    res = request_api('POST', '/cupones/proponer')
    if res.get('success') or 'propuesta' in res:
        propuesta = res.get('propuesta', {})
        print_success("¡La IA (Ollama) analizó el contexto y generó cupones estratégicos!")
        
        analisis = propuesta.get('analisis', 'Análisis no detallado.')
        print("\n  [🧠 Análisis de la IA]:")
        print(f"  > {analisis}\n")
        
        print("  [🎟️ Cupones Propuestos]:")
        for c in propuesta.get('cupones', []):
            print(f"    - {c.get('codigo')}: {c.get('descuento')}% OFF | {c.get('objetivo')} | Validez: {c.get('duracion_dias', 0)} días")
    else:
        print_warning("La respuesta de la IA falló o Ollama está apagado.")
        print(f"  Detalle: {res.get('error', res)}")
        
    print("\n=========================================")
    print(" ✅ CICLO DE PRUEBAS COMPLETADO")
    print("=========================================\n")

if __name__ == "__main__":
    run_tests()