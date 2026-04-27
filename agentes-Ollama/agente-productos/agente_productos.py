from flask import Flask, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:1.5b"

LIMITE_PRODUCTOS = None


# =========================
# PROMPT
# =========================
def construir_prompt(productos_json):
    return f"""
Convierte estos productos JSON al formato de salida deseado.
Cada producto ya tiene sus talles y colores agrupados.

Devuelve SOLO JSON válido.

Datos:
{json.dumps(productos_json, ensure_ascii=False)}

RESPONDE SOLO JSON.
"""


# =========================
# OLLAMA
# =========================
def llamar_ollama(prompt):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()["response"]

    except Exception as e:
        print("[OLLAMA ERROR]", e)
        raise


# =========================
# FALLBACK
# =========================
def generar_catalogo_sin_ollama(productos):
    resultado = []

    for prod in productos:
        resultado.append({
            "id_producto": prod["id_producto"],
            "producto": prod["Detalle"],
            "talles": prod["talles"],
            "colores": prod["colores"],
            "precio": prod["precio"],
            "variantes": prod.get("variantes", [])
        })

    return resultado


# =========================
# LIMPIAR JSON
# =========================
def limpiar_respuesta(texto):
    try:
        inicio = texto.find("[")
        fin = texto.rfind("]") + 1
        return json.loads(texto[inicio:fin])
    except:
        return []


# =========================
# API LOCAL
# =========================
def obtener_productos_api():
    try:
        response = requests.get('http://127.0.0.1:8000/api/productos')
        if not response.ok:
            print(f"[API ERROR] Status: {response.status_code}")
            return []
            
        data = response.json()
        if not data.get("success") or "data" not in data:
            print("[API ERROR] Respuesta sin success o data")
            return []
            
        productos_map = {}
        for row in data["data"]:
            id_producto = row["id_producto"]
            nombre = row["nombre"]
            
            if id_producto not in productos_map:
                productos_map[id_producto] = {
                    "id_producto": id_producto,
                    "Detalle": nombre,
                    "precio": 0,
                    "talles": set(),
                    "colores": set(),
                    "variantes": []
                }
                
            # Extraer de variantes y sus atributos
            for v in row.get("variantes", []):
                precio = v.get("precio", 0)
                if productos_map[id_producto]["precio"] == 0 and precio > 0:
                    productos_map[id_producto]["precio"] = precio
                
                # Extraer atributos de la variante
                atributos = v.get("atributos", {})
                talle = None
                color = None
                
                # Buscar talle y color en los atributos
                for attr_name, attr_data in atributos.items():
                    valor = attr_data.get("valor") if isinstance(attr_data, dict) else attr_data
                    
                    if attr_name.lower() in ['talle', 'tamaño', 'size']:
                        talle = valor
                        if valor:
                            productos_map[id_producto]["talles"].add(valor)
                    elif attr_name.lower() in ['color', 'colour']:
                        color = valor
                        if valor:
                            productos_map[id_producto]["colores"].add(valor)
                    
                productos_map[id_producto]["variantes"].append({
                    "id_variante": v.get("id_variante"),
                    "talle": talle,
                    "color": color,
                    "precio": precio
                })
        
        # Convertir sets a listas ordenadas
        productos = []
        for id_producto, datos in productos_map.items():
            talles = sorted(list(datos["talles"]))
            colores = sorted(list(datos["colores"]))
            
            # Si no hay talles/colores, usar valores por defecto
            if not talles:
                talles = ["Único"]
            if not colores:
                colores = ["Estándar"]
            
            productos.append({
                "id_producto": id_producto,
                "Detalle": datos["Detalle"],
                "precio": float(datos["precio"] or 15000),
                "talles": talles,
                "colores": colores,
                "variantes": datos["variantes"]
            })

        print(f"[API INFO] Procesados {len(productos)} productos")
        return productos

    except Exception as e:
        print(f"[API ERROR] {e}")
        import traceback
        traceback.print_exc()
        return []


# =========================
# ENDPOINT
# =========================
@app.route("/productos-ia")
def productos_ia():
    try:
        productos = obtener_productos_api()

        if not productos:
            return jsonify([])

        try:
            prompt = construir_prompt(productos)
            respuesta = llamar_ollama(prompt)
            resultado = limpiar_respuesta(respuesta)

            if not resultado:
                raise Exception("IA vacía")

        except:
            resultado = generar_catalogo_sin_ollama(productos)

        return jsonify(resultado)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    print("Servidor IA activo en http://localhost:5001")
    app.run(host="0.0.0.0", port=5001, debug=False)