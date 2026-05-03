from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json
import psycopg2
import os

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde el frontend

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:1.5b"  # Optimizado para i3 + 16GB RAM
FASTAPI_URL = "http://localhost:8000/api"

# =========================
# CONFIGURACIÓN
# =========================

# =========================
# PROMPT PARA EXTRAER INFORMACIÓN
# =========================
def construir_prompt_precio(consulta):
    return f"""
Extrae información de esta consulta sobre cambio de precio de producto.
Devuelve SOLO JSON válido en este formato:
{{"producto": "nombre del producto", "precio": 15000, "nuevo_nombre": null}}

Si el usuario quiere cambiar el nombre también, incluirlo en "nuevo_nombre", sino dejarlo en null.

Ejemplos:
- "cambiar el precio del buzo a 15000" → {{"producto": "Buzo", "precio": 15000, "nuevo_nombre": null}}
- "actualizar remera a 8500" → {{"producto": "Remera", "precio": 8500, "nuevo_nombre": null}}
- "cambiar buzo por sudadera y precio 12000" → {{"producto": "Buzo", "precio": 12000, "nuevo_nombre": "Sudadera"}}

Consulta del usuario:
"{consulta}"

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
            timeout=30  # 30s es suficiente para consultas simples
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
# LIMPIAR RESPUESTA
# =========================
def limpiar_respuesta(respuesta_texto):
    """Extrae el JSON de la respuesta de OLLAMA"""
    try:
        # Buscar el JSON en la respuesta
        inicio = respuesta_texto.find("{")
        fin = respuesta_texto.rfind("}") + 1
        
        if inicio == -1 or fin == 0:
            print("[WARN] No se encontró JSON en respuesta")
            return None
            
        json_str = respuesta_texto[inicio:fin]
        return json.loads(json_str)
    except Exception as e:
        print(f"[ERROR] Error parseando JSON: {e}")
        print(f"[ERROR] Respuesta cruda: {respuesta_texto}")
        return None


# =========================
# PARSEO MANUAL (FALLBACK)
# =========================
def parsear_consulta_manual(consulta):
    """
    Fallback: intenta extraer producto y precio sin OLLAMA.
    Busca patrones comunes como "buzo a 15000", "remera 8500", etc.
    """
    print("[FALLBACK] Parseando consulta manualmente...")
    consulta_lower = consulta.lower()
    
    # Buscar precio (número de 3-6 dígitos)
    import re
    precio_match = re.search(r'\b(\d{3,6})\b', consulta)
    
    if not precio_match:
        return None
    
    precio = int(precio_match.group(1))
    
    # Buscar producto (palabras antes del precio)
    palabras = consulta_lower.split()
    producto_palabras = []
    
    for palabra in palabras:
        if palabra.isdigit():
            break
        # Filtrar palabras comunes
        if palabra not in ['cambiar', 'actualizar', 'modificar', 'el', 'precio', 'de', 'del', 'a', 'por', 'en']:
            producto_palabras.append(palabra)
    
    if not producto_palabras:
        return None
    
    producto = ' '.join(producto_palabras).title()
    
    print(f"[FALLBACK] ✓ Extraído: {producto} = ${precio}")
    return {
        "producto": producto,
        "precio": precio,
        "nuevo_nombre": None
    }


# =========================
# VERIFICAR PRODUCTO EN BD
# =========================
def verificar_producto_existe(detalle):
    """Verifica si existe un producto con ese Detalle en la BD"""
    try:
        print(f"[DB] Verificando si existe producto: '{detalle}'")
        conn = psycopg2.connect(
            host=os.getenv("PG_HOST", "127.0.0.1"),
            port=int(os.getenv("PG_PORT", "5432")),
            dbname=os.getenv("PG_DB", "PrendeteRock"),
            user=os.getenv("PG_USER", "postgres"),
            password=os.getenv("PG_PASSWORD", ""),
            connect_timeout=5,
            sslmode="disable"
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Productos WHERE Detalle = %s", (detalle,))
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"[DB] Encontradas {count} variante(s)")
        return count > 0
        
    except Exception as e:
        print(f"[DB] ❌ Error: {str(e)}")
        return False


# =========================
# ACTUALIZAR PRECIO VÍA FASTAPI
# =========================
def actualizar_precio_fastapi(detalle, precio, nuevo_detalle=None):
    """Llama al endpoint de FastAPI para actualizar el precio"""
    try:
        url = f"{FASTAPI_URL}/admin/productos/detalle/{detalle}/precio"
        payload = {
            "precio": precio,
            "nuevo_detalle": nuevo_detalle
        }
        
        print(f"[FASTAPI] PUT {url}")
        print(f"[FASTAPI] Body: {payload}")
        
        response = requests.put(url, json=payload, timeout=10)
        
        print(f"[FASTAPI] Status: {response.status_code}")
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"[FASTAPI] ✓ {resultado}")
            return resultado
        else:
            error = response.json()
            print(f"[FASTAPI] ❌ {error}")
            return {"success": False, "error": error.get("detail", {}).get("error", "Error desconocido")}
            
    except Exception as e:
        print(f"[FASTAPI] ❌ Error: {str(e)}")
        return {"success": False, "error": str(e)}


# =========================
# ENDPOINT: ACTUALIZAR PRECIO
# =========================
@app.route("/actualizar-precio", methods=["POST"])
def actualizar_precio():
    try:
        print("\n" + "="*50)
        print("[REQUEST] /actualizar-precio")
        
        # Obtener datos del body
        data = request.get_json()
        
        # Soporte para dos formatos:
        # 1. Formato directo: {"detalle": "Buzo", "precio": 15000, "nuevo_detalle": "Sudadera"}
        # 2. Formato lenguaje natural: {"consulta": "cambiar precio del buzo a 15000"}
        
        detalle = data.get("detalle")
        precio = data.get("precio")
        nuevo_detalle = data.get("nuevo_detalle")
        consulta = data.get("consulta")
        
        # Si viene en formato directo, usarlo
        if detalle and precio:
            print(f"[FORMATO DIRECTO] Detalle: {detalle}, Precio: {precio}")
            producto = detalle
            
        # Si viene como consulta en lenguaje natural, procesarla
        elif consulta:
            print(f"[CONSULTA] '{consulta}'")
            
            # 1. Intentar extraer información con OLLAMA
            info_extraida = None
            
            try:
                print("[IA] Construyendo prompt...")
                prompt = construir_prompt_precio(consulta)
                
                print(f"[IA] Llamando OLLAMA ({MODEL})...")
                respuesta = llamar_ollama(prompt)
                print(f"[IA] Respuesta: {respuesta[:200]}...")
                
                info_extraida = limpiar_respuesta(respuesta)
                
                if info_extraida:
                    print(f"[IA] ✓ Info extraída: {info_extraida}")
                else:
                    print("[WARN] OLLAMA no retornó JSON válido")
                    
            except Exception as ollama_error:
                print(f"[WARN] OLLAMA falló: {str(ollama_error)[:100]}")
            
            # 2. Fallback: parseo manual
            if not info_extraida:
                print("[DEBUG] Usando fallback (parseo manual)...")
                info_extraida = parsear_consulta_manual(consulta)
                
                if not info_extraida:
                    return jsonify({
                        "success": False,
                        "error": "No se pudo entender la consulta. Formato esperado: 'cambiar precio del [producto] a [precio]'"
                    }), 400
            
            # 3. Validar información extraída
            producto = info_extraida.get("producto")
            precio = info_extraida.get("precio")
            nuevo_detalle = info_extraida.get("nuevo_nombre")
            
            if not producto or not precio:
                return jsonify({
                    "success": False,
                    "error": "No se pudo extraer producto o precio de la consulta"
                }), 400
        else:
            return jsonify({
                "success": False,
                "error": "Falta el campo 'detalle' y 'precio' o 'consulta'"
            }), 400
        
        print(f"[INFO] Producto: {producto}")
        print(f"[INFO] Precio: ${precio}")
        if nuevo_detalle:
            print(f"[INFO] Nuevo nombre: {nuevo_detalle}")
        
        # 4. Verificar que el producto existe
        if not verificar_producto_existe(producto):
            return jsonify({
                "success": False,
                "error": f"No se encontró ningún producto con el nombre '{producto}'"
            }), 404
        
        # 5. Actualizar precio vía FastAPI
        print("[DEBUG] Llamando a FastAPI para actualizar...")
        resultado = actualizar_precio_fastapi(producto, precio, nuevo_detalle)
        
        if resultado.get("success"):
            print("[SUCCESS] ✓ Precio actualizado correctamente")
            return jsonify(resultado["data"]), 200
        else:
            print(f"[ERROR] ✗ {resultado.get('error')}")
            return jsonify({
                "success": False,
                "error": resultado.get("error")
            }), 500

    except Exception as e:
        print(f"[ERROR] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================
# ENDPOINT: HEALTH CHECK
# =========================
@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "servicio": "Agente de Actualización de Precios",
        "modelo": MODEL
    })


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    print("="*50)
    print("🤖 AGENTE IA - ACTUALIZACIÓN DE PRECIOS")
    print("="*50)
    print("✓ Endpoint: http://localhost:5002/actualizar-precio")
    print("✓ Health: http://localhost:5002/health")
    print(f"✓ Modelo OLLAMA: {MODEL}")
    print("✓ Puerto: 5002")
    print("="*50)
    print("\nEjemplos de uso:")
    print('  POST /actualizar-precio')
    print('  {"consulta": "cambiar el precio del buzo a 15000"}')
    print("="*50)
    app.run(host="0.0.0.0", port=5002, debug=False)
