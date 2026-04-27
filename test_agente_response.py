import requests
import json

print("Consultando agente...")
response = requests.get("http://localhost:5001/productos-ia", timeout=30)

print(f"Status: {response.status_code}")
print(f"\nRespuesta JSON:")
data = response.json()
print(json.dumps(data, indent=2, ensure_ascii=False))

print(f"\n✅ Total productos: {len(data)}")
print("\nResumen:")
for p in data:
    print(f"  - {p.get('producto')}: ${p.get('precio')} | Talles: {p.get('talles')} | Colores: {p.get('colores')}")
