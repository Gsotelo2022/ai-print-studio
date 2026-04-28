"""
Test del endpoint de proponer cupones del agente de IA
"""

import requests

BASE_URL = "http://localhost:5003"

print("\n" + "="*70)
print("🧪 TEST: Endpoint proponer cupones (Agente IA)")
print("="*70 + "\n")

# Test 1: Verificar que el agente responda
print("1️⃣ Verificando agente...")
try:
    response = requests.get(f"{BASE_URL}/", timeout=5)
    if response.status_code == 200:
        print("   ✅ Agente activo")
    else:
        print(f"   ⚠️  Status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Test 2: Probar endpoint de proponer cupones
print("\n2️⃣ Probando endpoint /api/cupones/proponer...")
try:
    response = requests.post(
        f"{BASE_URL}/api/cupones/proponer",
        timeout=60  # Dar tiempo suficiente para que la IA procese
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Respuesta exitosa")
        print(f"\n   📋 Resultado:")
        
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"      • {key}: {value}")
        else:
            print(f"      {data}")
    else:
        print(f"   ❌ Error: {response.text}")
        
except requests.exceptions.Timeout:
    print(f"   ⏱️  Timeout - La IA está tardando demasiado")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*70 + "\n")
