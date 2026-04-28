"""
Script para reproducir el error [WinError 233] reportado por el usuario
"""

import requests
import sys
import time

BASE_URL = "http://localhost:8000"

print("\n" + "="*70)
print("🔍 Reproduciendo error [WinError 233]")
print("="*70 + "\n")

# Test 1: Ver si el servidor responde
print("1️⃣ Verificando servidor...")
try:
    response = requests.get(f"{BASE_URL}/api/health", timeout=5)
    print(f"   ✅ Servidor responde: {response.status_code}\n")
except Exception as e:
    print(f"   ❌ Error conectando: {e}\n")
    sys.exit(1)

# Test 2: Intentar obtener cupones (podría causar [WinError 233])
print("2️⃣ Probando endpoint de cupones...")
test_users = [1, 2, 3]

for user_id in test_users:
    try:
        print(f"\n   Usuario {user_id}:")
        response = requests.get(
            f"{BASE_URL}/api/cupones/disponibles/{user_id}",
            timeout=10
        )
        
        print(f"      Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"      ✅ OK - {data}")
        else:
            print(f"      ⚠️  Response: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"      ❌ ConnectionError: {e}")
        if "[WinError 233]" in str(e):
            print(f"      🎯 ¡AHÍ ESTÁ EL ERROR [WinError 233]!")
            print(f"      Detalles: {e}")
            break
    except Exception as e:
        print(f"      ❌ Error: {type(e).__name__}: {e}")
        if "WinError 233" in str(e):
            print(f"      🎯 ¡ENCONTRADO [WinError 233]!")
            break

print("\n" + "="*70 + "\n")
