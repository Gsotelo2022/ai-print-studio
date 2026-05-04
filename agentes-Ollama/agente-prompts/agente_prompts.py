from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json
import re

app = Flask(__name__)
CORS(app)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:1.5b"


def construir_prompt_sistema(descripcion_usuario: str) -> str:
    return f"""You are an expert prompt engineer for Stable Diffusion image generation.
The user describes what they want in Spanish. Your job is to convert it into a high-quality
English prompt optimized for Stable Diffusion / Flux image generation.

Rules:
- Respond ONLY with the English prompt, no explanations, no quotes, no preamble
- Use comma-separated descriptive keywords
- Include style qualifiers: "digital art, high quality, detailed, sharp focus"
- Keep it under 120 words
- Do NOT translate literally — optimize for image generation

User description (in Spanish): "{descripcion_usuario}"

English prompt:"""


def llamar_ollama(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 150  # Máximo 150 tokens — prompts son cortos
            }
        },
        timeout=120
    )
    if response.status_code != 200:
        raise Exception(f"Ollama error: {response.text}")
    return response.json()["response"].strip()


def limpiar_prompt(texto: str) -> str:
    """Elimina comillas, saltos de línea y prefijos que a veces agrega el modelo."""
    texto = texto.strip().strip('"').strip("'")
    texto = re.sub(r'^(English prompt:|Prompt:|Result:)\s*', '', texto, flags=re.IGNORECASE)
    texto = texto.replace('\n', ', ').replace('  ', ' ')
    return texto.strip()


@app.route("/generar-prompt", methods=["POST"])
def generar_prompt():
    data = request.get_json()
    descripcion = data.get("descripcion", "").strip()

    if not descripcion or len(descripcion) < 3:
        return jsonify({
            "success": False,
            "error": "La descripción debe tener al menos 3 caracteres"
        }), 400

    if len(descripcion) > 300:
        return jsonify({
            "success": False,
            "error": "La descripción no puede superar los 300 caracteres"
        }), 400

    try:
        prompt_sistema = construir_prompt_sistema(descripcion)
        respuesta_cruda = llamar_ollama(prompt_sistema)
        prompt_final = limpiar_prompt(respuesta_cruda)

        return jsonify({
            "success": True,
            "prompt": prompt_final,
            "descripcion_original": descripcion
        })

    except requests.exceptions.ConnectionError:
        return jsonify({
            "success": False,
            "error": "No se puede conectar a Ollama. ¿Está corriendo ollama serve?"
        }), 503

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "servicio": "Agente Asistente de Prompts",
        "modelo": MODEL,
        "puerto": 5004
    })


if __name__ == "__main__":
    print("=" * 50)
    print("🤖 AGENTE IA — ASISTENTE DE PROMPTS")
    print("=" * 50)
    print("✓ Endpoint: http://localhost:5004/generar-prompt")
    print("✓ Health:   http://localhost:5004/health")
    print(f"✓ Modelo:   {MODEL}")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5004, debug=False)