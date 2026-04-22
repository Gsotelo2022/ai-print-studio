#!/usr/bin/env python3
"""
Test flujo completo: Registro + Login
Valida que el usuario se puede registrar y luego loguear correctamente
"""
import urllib.request
import json
import sys
import time

def make_request(endpoint, payload):
    """Helper para hacer requests HTTP"""
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        f'http://127.0.0.1:8000{endpoint}',
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_data = json.loads(e.read().decode())
        return {"error": error_data, "http_code": e.code}
    except urllib.error.URLError as e:
        return {"error": f"No se puede conectar: {e}"}
    except Exception as e:
        return {"error": str(e)}

print("=" * 70)
print("TEST: Flujo Completo de Autenticación (Registro + Login)")
print("=" * 70)
print()

# Test con usuario único
test_email = f"usuario_completo_{int(time.time())}@test.com"
test_password = "TestPassword123!"
test_name = "Test User Complete"

print(f"Email: {test_email}")
print(f"Contraseña: {test_password}")
print()

# PASO 1: Registro
print("[PASO 1] Registrando usuario...")
register_payload = {
    "fullname": test_name,
    "email": test_email,
    "phone": "+5491123456789",
    "password": test_password
}

register_result = make_request('/api/register', register_payload)

if "error" in register_result:
    print(f"✗ Error en registro: {register_result['error']}")
    sys.exit(1)

if register_result.get("success"):
    user_id = register_result['data']['id_usuario']
    print(f"✓ Registro exitoso")
    print(f"  ID Usuario: {user_id}")
    print(f"  Nombre: {register_result['data']['Nombre']}")
    print(f"  Email: {register_result['data']['Email']}")
else:
    print(f"✗ Registro no exitoso: {register_result}")
    sys.exit(1)

# PASO 2: Login con credenciales correctas
print()
print("[PASO 2] Intentando login con credenciales correctas...")
login_payload = {
    "email": test_email,
    "password": test_password
}

login_result = make_request('/api/login', login_payload)

if "error" in login_result:
    print(f"✗ Error en login: {login_result['error']}")
    sys.exit(1)

if login_result.get("success"):
    print(f"✓ Login exitoso")
    print(f"  ID Usuario: {login_result['data']['id_usuario']}")
    print(f"  Nombre: {login_result['data']['Nombre']}")
    print(f"  Email: {login_result['data']['Email']}")
    print(f"  Tipo: {login_result['data']['Tipo']}")
    
    if login_result['data']['id_usuario'] == user_id:
        print(f"✓ ID coincide con el registro")
    else:
        print(f"✗ ERROR: ID no coincide")
else:
    print(f"✗ Login no exitoso: {login_result}")
    sys.exit(1)

# PASO 3: Login con contraseña incorrecta
print()
print("[PASO 3] Intentando login con contraseña incorrecta...")
login_payload_bad = {
    "email": test_email,
    "password": "WrongPassword123!"
}

login_result_bad = make_request('/api/login', login_payload_bad)

if login_result_bad.get("success"):
    print(f"✗ ERROR: Login con contraseña incorrecta fue aceptado!")
    sys.exit(1)
else:
    error = login_result_bad.get("error")
    if isinstance(error, dict) and "error" in error:
        print(f"✓ Login rechazado correctamente")
        print(f"  Mensaje: {error['error']}")
    elif isinstance(error, str):
        if "Credenciales inválidas" in error or "invalid" in error.lower():
            print(f"✓ Login rechazado correctamente")
        else:
            print(f"⚠ Login rechazado pero con mensaje inesperado: {error}")

# PASO 4: Login con email que no existe
print()
print("[PASO 4] Intentando login con email que no existe...")
login_payload_nonexistent = {
    "email": f"nosuchuser_{int(time.time())}@test.com",
    "password": "AnyPassword123!"
}

login_result_nonexistent = make_request('/api/login', login_payload_nonexistent)

if login_result_nonexistent.get("success"):
    print(f"✗ ERROR: Login con usuario inexistente fue aceptado!")
    sys.exit(1)
else:
    print(f"✓ Login rechazado correctamente (usuario no existe)")

print()
print("=" * 70)
print("✓ TODOS LOS TESTS PASARON CORRECTAMENTE")
print("=" * 70)
print()
print("Resumen:")
print(f"  - Usuario registrado: {test_name} ({test_email})")
print(f"  - Login exitoso con credenciales correctas")
print(f"  - Login rechazado con contraseña incorrecta")
print(f"  - Login rechazado con email inexistente")
print()
