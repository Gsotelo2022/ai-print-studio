"""
Script para listar todos los endpoints disponibles en el servidor FastAPI
"""

import requests

BASE_URL = "http://localhost:8000"

print("\n" + "="*70)
print("📋 Endpoints disponibles en el servidor")
print("="*70 + "\n")

try:
    # FastAPI genera automáticamente el schema OpenAPI en /openapi.json
    response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
    
    if response.status_code == 200:
        openapi = response.json()
        paths = openapi.get('paths', {})
        
        print(f"Total de endpoints: {len(paths)}\n")
        
        for path, methods in sorted(paths.items()):
            print(f"  • {path}")
            for method in methods.keys():
                print(f"      ├─ {method.upper()}")
        
        # Buscar específicamente el endpoint de cupones
        cupones_path = [p for p in paths.keys() if 'cupon' in p.lower()]
        
        if cupones_path:
            print(f"\n✅ Endpoints de cupones encontrados:")
            for p in cupones_path:
                print(f"   • {p}")
        else:
            print(f"\n❌ NO se encontraron endpoints de cupones")
            print(f"   El endpoint esperado es: /api/cupones/disponibles/{{id_cliente}}")
    
    else:
        print(f"❌ Error al obtener schema: {response.status_code}")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*70 + "\n")
