"""
Test con imagen grande (1024x1024 píxeles)
"""
import requests
import json
from PIL import Image
import io
import base64

# Crear una imagen de 1024x1024 píxeles con gradiente
print("🎨 Generando imagen de prueba 1024x1024...")
img = Image.new('RGB', (1024, 1024))
pixels = img.load()

for i in range(1024):
    for j in range(1024):
        pixels[i, j] = (i % 256, j % 256, (i+j) % 256)

# Convertir a base64
buffer = io.BytesIO()
img.save(buffer, format='PNG')
image_bytes = buffer.getvalue()

base64_encoded = base64.b64encode(image_bytes).decode('utf-8')
IMAGEN_BASE64 = f"data:image/png;base64,{base64_encoded}"

print(f"✅ Imagen generada: {len(image_bytes)} bytes")
print(f"✅ Base64: {len(IMAGEN_BASE64)} caracteres")
print()

# Usuario y variante de prueba
USER_ID = 2
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
    "notas_cliente": "Test con imagen GRANDE 1024x1024"
}

print("📤 Enviando pedido con imagen GRANDE...")
print()

try:
    response = requests.post(
        "http://localhost:8000/api/create-order",
        json=payload,
        timeout=60
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
