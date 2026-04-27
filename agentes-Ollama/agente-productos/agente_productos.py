from flask import Flask, jsonify
from flask_cors import CORS
import requests
import json
import pyodbc

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
# DB
# =========================
def obtener_productos_db():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=.\\SQLEXPRESS01;'
            'DATABASE=PrendeteRock;'
            'Trusted_Connection=yes;'
        )

        cursor = conn.cursor()

        # 🔥 FIX: orden correcto de columnas y JOINs corregidos
        query = """
        SELECT 
            p.id_producto,        -- 0
            p.nombre,             -- 1
            pv.precio,            -- 2
            pv.id_variante,       -- 3
            pa.nombre,            -- 4
            pav.valor             -- 5
        FROM Productos p
        INNER JOIN Producto_Variantes pv ON p.id_producto = pv.id_producto
        LEFT JOIN Variante_Atributos va ON pv.id_variante = va.id_variante
        LEFT JOIN Producto_Atributo_Valores pav ON va.id_valor = pav.id_valor
        LEFT JOIN Producto_Atributos pa ON pav.id_atributo = pa.id_atributo
        WHERE p.activo = 1 AND pv.activo = 1
        ORDER BY p.id_producto
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        productos_map = {}
        variantes_map = {}  # Para agrupar atributos por variante

        for row in rows:
            id_producto = row[0]
            nombre = row[1]
            precio = float(row[2]) if row[2] else 0

            # 🔥 FIX CLAVE: índices correctos
            id_variante = row[3]
            attr_name = row[4]
            attr_value = row[5]

            if id_producto not in productos_map:
                productos_map[id_producto] = {
                    "id_producto": id_producto,
                    "Detalle": nombre,
                    "precio": precio,
                    "talles": set(),
                    "colores": set(),
                    "variantes": []
                }

            # atributos
            if attr_name == "Talle" and attr_value:
                productos_map[id_producto]["talles"].add(attr_value)

            if attr_name == "Color" and attr_value:
                productos_map[id_producto]["colores"].add(attr_value)

            # 🔥 Agrupar atributos por variante
            if id_variante:
                if id_variante not in variantes_map:
                    variantes_map[id_variante] = {
                        "id_variante": id_variante,
                        "id_producto": id_producto,
                        "talle": None,
                        "color": None,
                        "precio": precio
                    }
                
                if attr_name == "Talle" and attr_value:
                    variantes_map[id_variante]["talle"] = attr_value
                elif attr_name == "Color" and attr_value:
                    variantes_map[id_variante]["color"] = attr_value
        
        # Agregar variantes agrupadas a productos
        for id_variante, variante_data in variantes_map.items():
            id_producto = variante_data["id_producto"]
            if id_producto in productos_map:
                productos_map[id_producto]["variantes"].append({
                    "id_variante": variante_data["id_variante"],
                    "talle": variante_data["talle"],
                    "color": variante_data["color"],
                    "precio": variante_data["precio"]
                })

        # =========================
        # FORMATO FINAL
        # =========================
        productos = []

        for id_producto, datos in productos_map.items():
            talles_lista = list(datos["talles"]) if datos["talles"] else ["U"]
            colores_lista = list(datos["colores"]) if datos["colores"] else ["Unico"]

            productos.append({
                "id_producto": id_producto,
                "Detalle": datos["Detalle"],
                "precio": datos["precio"],
                "talles": talles_lista,
                "colores": colores_lista,
                "variantes": datos["variantes"]
            })

        cursor.close()
        conn.close()

        return productos

    except Exception as e:
        print("DB ERROR:", e)
        return []


# =========================
# ENDPOINT
# =========================
@app.route("/productos-ia")
def productos_ia():
    try:
        productos = obtener_productos_db()

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