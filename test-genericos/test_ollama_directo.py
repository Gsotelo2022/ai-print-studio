"""
Test directo de Ollama
"""

import requests
import time

print("\n" + "="*70)
print("🧪 TEST: Ollama directo")
print("="*70 + "\n")

print("1️⃣ Verificando Ollama...")
try:
    start = time.time()
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': 'qwen2.5:1.5b',
            'prompt': 'Di "hola" en una palabra',
            'stream': False
        },
        timeout=30
    )
    end = time.time()
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Ollama responde")
        print(f"   ⏱️  Tiempo: {end - start:.2f}s")
        print(f"   📝 Respuesta: {result.get('response', '')[:100]}")
    else:
        print(f"   ❌ Error: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("   ❌ No se puede conectar a Ollama")
    print("   💡 Inicia Ollama con: ollama serve")
except requests.exceptions.Timeout:
    print("   ⏱️  Timeout - Ollama está tardando demas iado")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*70 + "\n")
