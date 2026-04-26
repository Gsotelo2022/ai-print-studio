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
    """
    Construye el prompt para OLLAMA.
    Los productos ya vienen agrupados con talles y colores en arrays.
    Solo necesitamos formatear la salida final.
    """
    return f"""
Convierte estos productos JSON al formato de salida deseado.
Cada producto ya tiene sus talles y colores agrupados.
Devuelve SOLO JSON válido en este formato exacto:
[{{"id_producto":1,"producto":"Remera","talles":["S","M"],"colores":["Rojo","Azul"],"precio":12000}}]

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
            timeout=10  # 10s timeout - si falla, va al fallback rápidamente
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
    Los productos ya vienen agrupados desde obtener_productos_db()
    """
    print("[FALLBACK] Generando catálogo sin OLLAMA...")
    
    # Convertir al formato esperado por el frontend
    resultado = []
    for prod in productos:
        resultado.append({
            "id_producto": prod.get('id_producto'),
            "producto": prod.get('Detalle', 'Sin nombre'),
            "talles": prod.get('talles', []),
            "colores": prod.get('colores', []),
            "precio": prod.get('precio', 0.0)
        })
    
    print(f"[FALLBACK] ✓ {len(resultado)} productos procesados")
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
        
        # Query corregida para la nueva estructura de BD normalizada
        query = """
        SELECT 
            p.id_producto,
            p.nombre,
            pv.precio,
            pa.nombre as atributo_nombre,
            pav.valor as atributo_valor
        FROM Productos p
        INNER JOIN Producto_Variantes pv ON p.id_producto = pv.id_producto
        LEFT JOIN Variante_Atributos va ON pv.id_variante = va.id_variante
        LEFT JOIN Producto_Atributos pa ON va.id_atributo = pa.id_atributo
        LEFT JOIN Producto_Atributo_Valores pav ON va.id_valor = pav.id_valor
        WHERE p.activo = 1 AND pv.activo = 1
        ORDER BY p.id_producto
        """
        
        print("[DB] Ejecutando query con JOINs...")
        cursor.execute(query)
        
        # Agrupar productos por id_producto (no por nombre para evitar duplicados)
        productos_map = {}
        rows = cursor.fetchall()
        print(f"[DB] Obtenidos {len(rows)} registros (con variantes)")
        
        for row in rows:
            id_producto = row[0]
            nombre = row[1]
            precio = float(row[2]) if row[2] else 0.0
            atributo_nombre = row[3]
            atributo_valor = row[4]
            
            # Inicializar producto si no existe (agrupar por ID, no por nombre)
            if id_producto not in productos_map:
                productos_map[id_producto] = {
                    "id_producto": id_producto,
                    "Detalle": nombre,
                    "precio": precio,
                    "Color": None,
                    "talle": None,
                    "talles": set(),
                    "colores": set()
                }
            
            # Agregar atributos
            if atributo_nombre == 'Talle' and atributo_valor:
                productos_map[id_producto]['talles'].add(atributo_valor)
            elif atributo_nombre == 'Color' and atributo_valor:
                productos_map[id_producto]['colores'].add(atributo_valor)
        
        # Convertir a lista y preparar datos
        productos = []
        for id_producto, datos in productos_map.items():
            talles_lista = sorted(list(datos["talles"]))
            colores_lista = sorted(list(datos["colores"]))
            
            # Crear registro base
            producto = {
                "id_producto": datos["id_producto"],
                "Detalle": datos["Detalle"],
                "precio": datos["precio"],
                "talles": talles_lista,
                "colores": colores_lista,
                # Para compatibilidad con código que espera campos individuales:
                "Color": colores_lista[0] if colores_lista else None,
                "talle": talles_lista[0] if talles_lista else None
            }
            productos.append(producto)
            print(f"[DB]   {len(productos)}. {producto['Detalle']}: {len(talles_lista)} talles, {len(colores_lista)} colores")
        
        cursor.close()
        conn.close()
        print(f"[DB] ✓ {len(productos)} productos agrupados")
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
        print("\n[DEBUG] ======= INICIO /productos-ia =======")
        
        # 1. Obtener productos de BD
        print("[DEBUG] Conectando a BD...")
        productos = obtener_productos_db()
        print(f"[DEBUG] Productos obtenidos: {len(productos)} registros")
        
        if not productos:
            print("[DEBUG] ⚠️ No hay productos en BD!")
            return jsonify([]), 200
        
        print(f"[DEBUG] Primer producto de ejemplo: {productos[0] if productos else 'N/A'}")
        
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
            
            if not resultado or len(resultado) == 0:
                print("[WARN] OLLAMA devolvió array vacío, usando fallback...")
                raise Exception("OLLAMA devolvió resultado vacío")
            
        except Exception as ollama_error:
            print(f"[WARN] OLLAMA falló: {str(ollama_error)[:100]}")
            print("[WARN] Usando catálogo estático sin IA...")
            resultado = generar_catalogo_sin_ollama(productos)
            print(f"[DEBUG] Resultado FALLBACK: {len(resultado)} productos")
        
        print(f"[DEBUG] ======= FIN /productos-ia - Devolviendo {len(resultado)} productos =======\n")
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