"""
Test para verificar que create-order maneja base64 correctamente
"""
import requests
import json

# Base64 de una imagen pequeña (1x1 píxel rojo)
IMAGEN_BASE64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="

# Usuario de prueba (Cliente Demo ID: 2)
USER_ID = 2

# Variante de prueba (debería existir en la BD)
ID_VARIANTE = 1

payload = {
    "user_id": USER_ID,
    "items": [
        {
            "id_variante": ID_VARIANTE,
            "cantidad": 1,
            "archivo_diseno": IMAGEN_BASE64,
            "posicion_x": 50,
            "posicion_y": 50,
            "zoom": 1.0
        }
    ],
    "direccion_envio": "Calle Test 123",
    "ciudad": "Buenos Aires",
    "telefono_contacto": "1234567890",
    "notas_cliente": "Test de base64"
}

print("📤 Enviando pedido con base64...")
print(f"   Usuario ID: {USER_ID}")
print(f"   Variante ID: {ID_VARIANTE}")
print(f"   Base64 length: {len(IMAGEN_BASE64)} caracteres")
print()

try:
    response = requests.post(
        "http://localhost:8000/api/create-order",
        json=payload,
        timeout=30
    )
    
    print(f"📥 Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        result = response.json()
        print("✅ PEDIDO CREADO EXITOSAMENTE")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("❌ ERROR AL CREAR PEDIDO")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error en la petición: {e}")
