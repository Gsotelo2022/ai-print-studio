from flask import Flask, jsonify
from flask_cors import CORS
import requests
import json
import pyodbc

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde el frontend

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:1.5b"  # Optimizado para i3 + 16GB RAM

# =========================
# CONFIGURACIÓN
# =========================
LIMITE_PRODUCTOS = None  # Cambiar a None para procesar TODOS los productos
                         # Recomendado: 10-20 para i3, 50+ para i5/i7


# =========================
# PROMPT OPTIMIZADO PARA i3
# =========================
def construir_prompt(productos_json):
    # NO reducir: procesar todos los productos que vienen de BD (limitados en query)
    return f"""
Agrupa estos productos JSON por "Detalle".
Devuelve SOLO JSON válido en este formato:
[{{"producto":"Nombre","talles":["S","M"],"colores":["Rojo","Azul"]}}]

Datos ({len(productos_json)} productos):
{json.dumps(productos_json, ensure_ascii=False)}

RESPONDE SOLO EL JSON, SIN TEXTO ADICIONAL.
"""


# =========================
# OLLAMA
# =========================
def llamar_ollama(prompt):
    try:
        print("[OLLAMA] Enviando petición a http://localhost:11434...")
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60  # 60s para i3 + 16GB RAM
        )

        print(f"[OLLAMA] Status: {response.status_code}")
        
        if response.status_code != 200:
            error_msg = f"Error Ollama: {response.text}"
            print(f"[OLLAMA] ❌ {error_msg}")
            raise Exception(error_msg)

        resultado = response.json()["response"]
        print(f"[OLLAMA] ✓ Respuesta recibida ({len(resultado)} caracteres)")
        return resultado
        
    except requests.exceptions.ConnectionError as e:
        print(f"[OLLAMA] ❌ No se puede conectar a OLLAMA en http://localhost:11434")
        print(f"         ¿Está OLLAMA corriendo? (ollama serve)")
        raise
    except Exception as e:
        print(f"[OLLAMA] ❌ Error: {str(e)}")
        raise


# =========================
# GENERADOR ESTÁTICO (FALLBACK)
# =========================
def generar_catalogo_sin_ollama(productos):
    """
    Genera catálogo agrupado sin usar OLLAMA.
    Fallback cuando OLLAMA no responde.
    """
    print("[FALLBACK] Generando catálogo sin OLLAMA...")
    catalogo = {}
    
    for prod in productos:
        detalle = prod.get('Detalle', 'Sin nombre')
        color = prod.get('Color')
        talle = prod.get('talle')
        
        if detalle not in catalogo:
            catalogo[detalle] = {'talles': set(), 'colores': set()}
        
        if talle:
            catalogo[detalle]['talles'].add(talle)
        if color:
            catalogo[detalle]['colores'].add(color)
    
    # Convertir sets a listas ordenadas
    resultado = [
        {
            "producto": producto,
            "talles": sorted(list(datos['talles'])),
            "colores": sorted(list(datos['colores']))
        }
        for producto, datos in sorted(catalogo.items())
    ]
    
    print(f"[FALLBACK] ✓ {len(resultado)} productos agrupados")
    return resultado


# =========================
# LIMPIAR RESPUESTA
# =========================
def limpiar_respuesta(respuesta_texto):
    try:
        inicio = respuesta_texto.find("[")
        fin = respuesta_texto.rfind("]") + 1
        json_str = respuesta_texto[inicio:fin]
        return json.loads(json_str)
    except Exception as e:
        print("Error parseando JSON:", e)
        print("Respuesta cruda:", respuesta_texto)
        return []


# =========================
# DB
# =========================
def obtener_productos_db():
    try:
        # Conexión a SQL Server
        print("[DB] Intentando conectar a SQL Server...")
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=.\\SQLEXPRESS01;'
            'DATABASE=PrendeteRock;'
            'Trusted_Connection=yes;'
        )
        print("[DB] ✓ Conectado a SQL Server")
        
        cursor = conn.cursor()
        
        if LIMITE_PRODUCTOS:
            print(f"[DB] Ejecutando SELECT TOP {LIMITE_PRODUCTOS}... (MODO PRUEBA)")
            cursor.execute(f"SELECT TOP {LIMITE_PRODUCTOS} Detalle, Color, talle FROM Productos")
        else:
            print("[DB] Ejecutando SELECT... (TODOS LOS PRODUCTOS)")
            cursor.execute("SELECT Detalle, Color, talle FROM Productos")

        productos = []
        rows = cursor.fetchall()
        print(f"[DB] Obtenidos {len(rows)} registros")
        
        for i, row in enumerate(rows):
            producto = {
                "Detalle": row[0],  # Detalle
                "Color": row[1],    # Color
                "talle": row[2] if row[2] else None  # talle (puede ser NULL)
            }
            productos.append(producto)
            # Log TODOS en modo prueba (son solo 10)
            print(f"[DB]   {i+1}. {producto}")
        
        cursor.close()
        conn.close()
        print("[DB] Conexión cerrada")
        return productos
        
    except Exception as e:
        print(f"[DB] ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


# =========================
# ENDPOINT IA
# =========================
@app.route("/productos-ia")
def productos_ia():
    try:
        print("\n[DEBUG] Iniciando /productos-ia...")
        
        # 1. Obtener productos de BD
        print("[DEBUG] Conectando a BD...")
        productos = obtener_productos_db()
        print(f"[DEBUG] Productos obtenidos: {len(productos)} registros")
        
        if not productos:
            print("[DEBUG] ⚠️ No hay productos en BD!")
            return jsonify([]), 200
        
        # 2. Intentar usar OLLAMA con fallback
        try:
            print(f"[DEBUG] Construyendo prompt...")
            prompt = construir_prompt(productos)
            
            print(f"[DEBUG] Llamando OLLAMA ({MODEL})...")
            respuesta = llamar_ollama(prompt)
            print(f"[DEBUG] Respuesta OLLAMA: {respuesta[:200]}...")
            
            print("[DEBUG] Limpiando respuesta JSON...")
            resultado = limpiar_respuesta(respuesta)
            print(f"[DEBUG] ✓ Resultado OLLAMA: {len(resultado)} productos")
            
        except Exception as ollama_error:
            print(f"[WARN] OLLAMA falló: {str(ollama_error)[:100]}")
            print("[WARN] Usando catálogo estático sin IA...")
            resultado = generar_catalogo_sin_ollama(productos)
        
        return jsonify(resultado)

    except Exception as e:
        print(f"[ERROR] Exception en /productos-ia: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    print("="*50)
    print("🤖 AGENTE IA - OLLAMA")
    print("="*50)
    print("✓ Endpoint: http://localhost:5001/productos-ia")
    print(f"✓ Modelo: {MODEL}")
    print("✓ Puerto: 5001")
    if LIMITE_PRODUCTOS:
        print(f"⚠ MODO PRUEBA: Procesando solo {LIMITE_PRODUCTOS} productos")
        print(f"  (Cambiar LIMITE_PRODUCTOS a None para procesar todos)")
    else:
        print("✓ Procesando TODOS los productos de la BD")
    print("="*50)
    app.run(host="0.0.0.0", port=5001, debug=False)