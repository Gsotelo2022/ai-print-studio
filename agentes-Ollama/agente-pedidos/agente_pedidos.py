from flask import Flask, request, jsonify
from flask_cors import CORS
import pyodbc
import requests
import re
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os

app = Flask(__name__)
CORS(app)

# ==============================
# CONFIG
# ==============================

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:1.5b"
FAQ_FILE = os.path.join(os.path.dirname(__file__), "faq_sql_ollama.xlsx")
SIMILARITY_THRESHOLD = 0.3  # Umbral mínimo de similitud

# ==============================
# CACHE FAQ
# ==============================

faq_data = None
vectorizer = None
tfidf_matrix = None

def cargar_faq():
    """Carga FAQ del Excel y prepara vectorizador TF-IDF"""
    global faq_data, vectorizer, tfidf_matrix
    
    try:
        if not os.path.exists(FAQ_FILE):
            print(f"❌ Archivo FAQ no encontrado: {FAQ_FILE}")
            return False
        
        df = pd.read_excel(FAQ_FILE)
        faq_data = df.copy()
        
        # Preparar vectorizador TF-IDF
        # Nota: scikit-learn solo soporta 'english' por defecto
        # Usamos None para cargar todas las palabras
        vectorizer = TfidfVectorizer(lowercase=True, stop_words=None)
        tfidf_matrix = vectorizer.fit_transform(faq_data['Pregunta Frecuente'].astype(str))
        
        # Verificar que existe columna 'Tipo'
        if 'Tipo' not in faq_data.columns:
            print(f"⚠️ Columna 'Tipo' no encontrada en FAQ")
        
        print(f"✅ FAQ cargado: {len(faq_data)} preguntas")
        return True
    except Exception as e:
        print(f"❌ Error cargando FAQ: {e}")
        return False

def buscar_pregunta_similar(consulta_usuario):
    """Busca la pregunta más similar en el FAQ usando TF-IDF"""
    global faq_data, vectorizer, tfidf_matrix
    
    if faq_data is None or vectorizer is None:
        return None, None, 0
    
    try:
        # Vectorizar consulta del usuario
        user_vector = vectorizer.transform([consulta_usuario])
        
        # Calcular similitud con todas las preguntas
        similarities = cosine_similarity(user_vector, tfidf_matrix)[0]
        
        # Obtener índice de mayor similitud
        best_idx = np.argmax(similarities)
        best_score = similarities[best_idx]
        
        if best_score < SIMILARITY_THRESHOLD:
            print(f"⚠️ Similitud muy baja ({best_score:.2f}) - debajo del umbral")
            return None, None, best_score
        
        pregunta = faq_data.iloc[best_idx]['Pregunta Frecuente']
        query_sql = faq_data.iloc[best_idx]['Query SQL']
        
        print(f"🎯 Pregunta similar encontrada (similitud: {best_score:.2f})")
        print(f"   Pregunta: {pregunta[:60]}...")
        
        return pregunta, query_sql, best_score
    
    except Exception as e:
        print(f"❌ Error buscando pregunta similar: {e}")
        return None, None, 0

# ==============================
# DB CONNECTION
# ==============================

def get_db_connection():
    try:
        return pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=.\\SQLEXPRESS01;'
            'DATABASE=PrendeteRock;'
            'Trusted_Connection=yes;'
        )
    except Exception as e:
        print(f"❌ Error conectando a BD: {e}")
        return None

def obtener_rol_usuario(user_id):
    """Obtiene el rol del usuario desde la BD"""
    try:
        conn = get_db_connection()
        if not conn:
            print(f"⚠️ No se pudo verificar rol del usuario {user_id}")
            return "CLIENTE"  # Default a CLIENTE si hay error
        
        cursor = conn.cursor()
        
        # Buscar en tabla usuarios (es_admin, rol, tipo_usuario, etc)
        queries_intento = [
            "SELECT es_admin FROM usuarios WHERE id_usuario = ?",
            "SELECT is_admin FROM usuarios WHERE id_usuario = ?", 
            "SELECT rol FROM usuarios WHERE id_usuario = ?",
            "SELECT tipo_usuario FROM usuarios WHERE id_usuario = ?"
        ]
        
        for query in queries_intento:
            try:
                cursor.execute(query, user_id)
                result = cursor.fetchone()
                if result:
                    # Verificar si es admin (1, True, 'admin', 'ADMIN')
                    valor = result[0]
                    if isinstance(valor, bool):
                        return "ADMIN" if valor else "CLIENTE"
                    elif isinstance(valor, int):
                        return "ADMIN" if valor == 1 else "CLIENTE"
                    elif isinstance(valor, str):
                        return "ADMIN" if valor.upper() in ['ADMIN', 'ADMINISTRADOR'] else "CLIENTE"
                    break
            except:
                continue
        
        conn.close()
        return "CLIENTE"  # Default a CLIENTE
        
    except Exception as e:
        print(f"⚠️ Error obteniendo rol: {e}")
        return "CLIENTE"  # Default a CLIENTE

# ==============================
# FUNCIONES DB
# ==============================

def ejecutar_query_faq(query_sql, user_id):
    """Ejecuta query del FAQ reemplazando :id_usuario con el user_id
    
    Maneja dos casos:
    - Queries CON :id_usuario → Pasa user_id como parámetro
    - Queries SIN :id_usuario → Ejecuta sin parámetro (queries genéricas/catálogo)
    
    También CORRIGE sintaxis SQL Server (LIMIT → TOP)
    """
    try:
        conn = get_db_connection()
        if conn is None:
            return None, "Error de conexión a la BD"
        
        cursor = conn.cursor()
        
        # Contar placeholders
        param_count = query_sql.count(':id_usuario') + query_sql.count(':user_id')
        
        # CORRECCIÓN: Reemplazar LIMIT (MySQL) con TOP (SQL Server)
        # Patrón: ... LIMIT 10 → SELECT TOP 10 ...
        if 'LIMIT' in query_sql.upper():
            import re
            match = re.search(r'\bLIMIT\s+(\d+)\s*$', query_sql, re.IGNORECASE)
            if match:
                limit_value = match.group(1)
                # Remover LIMIT
                query_sql = re.sub(r'\s+LIMIT\s+\d+\s*$', '', query_sql, flags=re.IGNORECASE)
                # Agregar TOP después de SELECT
                query_sql = re.sub(r'^(\s*SELECT\s+)', f'SELECT TOP {limit_value} ', query_sql, flags=re.IGNORECASE)
                print(f"   🔧 Convertido LIMIT a TOP {limit_value}")
        
        # Reemplazar placeholders
        query_procesada = query_sql.replace(':id_usuario', '?')
        query_procesada = query_procesada.replace(':user_id', '?')
        
        print(f"📊 Ejecutando query: {query_procesada[:100]}...")
        print(f"   Parámetros: {param_count} (user_id: {user_id})")
        
        # Ejecutar con o sin parámetros según corresponda
        if param_count > 0:
            # Query con filtro de usuario
            cursor.execute(query_procesada, user_id)
        else:
            # Query genérica (sin parámetros)
            print(f"   ⚠️ Query genérica detectada (sin :id_usuario)")
            cursor.execute(query_procesada)
        
        rows = cursor.fetchall()
        conn.close()
        
        return rows, None
    
    except Exception as e:
        print(f"❌ Error ejecutando query: {e}")
        return None, str(e)

def formatear_resultado(rows, columnas_cursor):
    """Formatea resultados de BD en texto legible"""
    if not rows:
        return "Sin resultados"
    
    try:
        # Obtener nombres de columnas
        col_names = [desc[0] for desc in columnas_cursor.description] if hasattr(columnas_cursor, 'description') else []
        
        if len(rows) == 1 and len(rows[0]) == 1:
            # Un solo valor (ej: COUNT)
            return str(rows[0][0])
        
        # Múltiples filas/columnas
        resultado = []
        for row in rows[:10]:  # Máximo 10 filas
            resultado.append(" | ".join(str(v) for v in row))
        
        return "\n".join(resultado)
    
    except Exception as e:
        print(f"❌ Error formateando: {e}")
        return str(rows)

# ==============================
# (IA DEPRECADA - Ahora usamos similitud TF-IDF)
# ==============================

# def construir_prompt(texto):
#     return f"""... (código antiguo)"""

# def llamar_ollama(prompt):
#     ... (código antiguo)

# def parsear_json(texto):
#     ... (código antiguo)



# ==============================
# ENDPOINT
# ==============================

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        mensaje = data.get("mensaje", "").strip()
        user_id = data.get("user_id")

        if not mensaje:
            return jsonify({"respuesta": "Mensaje vacío"}), 400

        if not user_id:
            return jsonify({"respuesta": "Falta user_id"}), 400

        print(f"\n📩 Mensaje usuario: {mensaje}")
        print(f"👤 User ID: {user_id}")

        # ========================================
        # BUSCAR PREGUNTA SIMILAR EN FAQ
        # ========================================
        pregunta_similar, query_sql, similitud = buscar_pregunta_similar(mensaje)

        if query_sql is None:
            return jsonify({
                "respuesta": "No conseguí una respuesta cercana a tu consulta. Intenta reformular. 🤔",
                "debug": {"similitud_max": float(similitud)}
            })

        # ========================================
        # VALIDAR PERMISOS (CLIENTE vs ADMIN)
        # ========================================
        tipo_pregunta = "CLIENTE"  # Default
        if faq_data is not None and 'Tipo' in faq_data.columns:
            # Buscar índice de la pregunta similar
            for idx, row in faq_data.iterrows():
                if row['Pregunta Frecuente'].lower() == pregunta_similar.lower():
                    tipo_pregunta = row['Tipo']
                    break
        
        print(f"🔐 Tipo de pregunta: {tipo_pregunta}")
        
        # Si es pregunta ADMIN, verificar que el usuario sea admin
        if tipo_pregunta == "ADMIN":
            rol_usuario = obtener_rol_usuario(user_id)
            print(f"👨‍💼 Rol del usuario: {rol_usuario}")
            
            if rol_usuario != "ADMIN":
                return jsonify({
                    "respuesta": "❌Su consuSolo administradores pueden consultar datos administrativos.",
                    "pregunta_interpretada": pregunta_similar,
                    "tipo": tipo_pregunta
                }), 403

        # ========================================
        # EJECUTAR QUERY SQL
        # ========================================
        rows, error = ejecutar_query_faq(query_sql, user_id)

        if error:
            return jsonify({
                "respuesta": f"Error al consultar: {error}",
                "pregunta_interpretada": pregunta_similar
            }), 500

        if not rows:
            return jsonify({
                "respuesta": "No hay datos para mostrar.",
                "pregunta_interpretada": pregunta_similar
            })

        # ========================================
        # FORMATEAR RESPUESTA
        # ========================================
        resultado_formateado = formatear_resultado(rows, None)

        return jsonify({
            "respuesta": resultado_formateado,
            "pregunta_interpretada": pregunta_similar,
            "similitud": float(similitud),
            "tipo_consulta": tipo_pregunta
        })

    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"respuesta": f"Error: {str(e)}"}), 500

# ==============================
# HEALTH
# ==============================

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "agente": "pedidos",
        "modelo": MODEL
    })

# ==============================
# RUN
# ==============================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 INICIANDO AGENTE DE PEDIDOS")
    print("="*60)
    
    # Cargar FAQ
    if cargar_faq():
        print("✅ Sistema listo para consultas")
    else:
        print("⚠️ Advertencia: FAQ no disponible")
    
    print("🌐 Escuchando en http://localhost:5005")
    print("="*60 + "\n")
    
    app.run(port=5005, debug=True)