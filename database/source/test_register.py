#!/usr/bin/env python3
"""
Test simple de registro de usuario
Asegúrate de que el servidor FastAPI esté corriendo:
  python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
"""
import urllib.request
import json
import sys
import time

def test_register(fullname, email, phone, password):
    """Prueba el endpoint de registro"""
    payload = {
        "fullname": fullname,
        "email": email,
        "phone": phone,
        "password": password
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/register',
        data=data,
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print("✓ Registro exitoso!")
            print(json.dumps(result, indent=2))
            return result
    except urllib.error.HTTPError as e:
        error_data = json.loads(e.read().decode())
        print(f"✗ Error HTTP {e.code}")
        print(json.dumps(error_data, indent=2))
        return None
    except urllib.error.URLError as e:
        print(f"✗ Error de conexión: {e}")
        print("\n⚠ El servidor FastAPI no está corriendo.")
        print("Inicia el servidor con:")
        print("  cd c:\\projects\\ai-print-studio\\database\\source")
        print("  python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

if __name__ == "__main__":
    print("=" * 70)
    print("TEST: Registro de Usuario")
    print("=" * 70)
    print()
    
    # Test con usuario único
    test_email = f"usuario_{int(time.time())}@test.com"
    print(f"Email de prueba: {test_email}\n")
    
    test_register(
        fullname="Juan Perez",
        email=test_email,
        phone="+541123456789",
        password="Password123"
    )
