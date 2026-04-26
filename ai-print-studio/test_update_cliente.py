import requests
import json

# URL del endpoint para actualizar un cliente
# Asegúrate de que el ID (ej. 11) exista en tu base de datos para la prueba.
CLIENTE_ID = 11 
API_URL = f"http://localhost:8000/api/admin/clientes/{CLIENTE_ID}"

# Datos de ejemplo para la actualización
# Modifica estos datos si es necesario
payload = {
    "nombre": "Usuario de Prueba Actualizado",
    "email": f"test.user.{CLIENTE_ID}@example.com",
    "telefono": "1234567890",
    "tipo": "cliente",
    "cuenta_bloqueada": False
}

def test_update_cliente():
    """
    Envía una petición PUT para actualizar un cliente y verifica la respuesta.
    """
    print(f"▶️  Intentando actualizar el cliente ID: {CLIENTE_ID}")
    print(f"▶️  URL del endpoint: {API_URL}")
    print(f"▶️  Payload enviado: {json.dumps(payload, indent=2)}")

    try:
        # Realizar la petición PUT
        response = requests.put(API_URL, json=payload)

        # Imprimir la información de la respuesta
        print(f"\n⏹️  Respuesta recibida:")
        print(f"Código de estado: {response.status_code}")
        
        # Intentar decodificar el JSON de la respuesta
        try:
            response_json = response.json()
            print(f"Respuesta (JSON): \n{json.dumps(response_json, indent=2)}")
        except json.JSONDecodeError:
            print(f"Respuesta (texto plano): {response.text}")

        # Evaluar el resultado
        if response.status_code == 200:
            print("\n✅ ¡ÉXITO! El cliente fue actualizado correctamente en el backend.")
        elif response.status_code == 404:
            print("\n❌ ¡FALLO! Error 404: El endpoint no fue encontrado.")
            print("   Verifica que el servidor FastAPI esté corriendo y que la URL es correcta.")
            print("   La ruta que se probó es: /api/admin/clientes/{id_cliente}")
        elif response.status_code == 422:
             print("\n❌ ¡FALLO! Error 422: Error de validación de datos.")
             print("   El payload enviado no tiene el formato correcto esperado por la API.")
        else:
            print(f"\n❌ ¡FALLO! Se recibió un código de error inesperado: {response.status_code}")

    except requests.exceptions.ConnectionError as e:
        print("\n❌ ¡FALLO! Error de conexión.")
        print("   Asegúrate de que el servidor FastAPI (backend) esté corriendo en http://localhost:8000")
        print(f"   Error detallado: {e}")
    except Exception as e:
        print(f"\n❌ ¡FALLO! Ocurrió un error inesperado durante la prueba: {e}")

if __name__ == "__main__":
    test_update_cliente()
