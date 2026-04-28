"""
Test simple del endpoint de cupones disponibles para verificar 
que no haya error [WinError 233]

Fecha: 28/04/2026
"""

import requests
import time

BASE_URL = "http://localhost:8000"

print("\n" + "="*70)
print("🧪 TEST: Endpoint de cupones disponibles")
print("="*70)

# Esperar a que el servidor arranque
print("\n⏳ Esperando servidor...")
time.sleep(3)

# Verificar servidor
print("1️⃣ Verificando servidor...")
try:
    response = requests.get(f"{BASE_URL}/docs", timeout=5)
    print("   ✅ Servidor activo\n")
except Exception as e:
    print(f"   ❌ Servidor no responde: {e}\n")
    exit(1)

# Probar endpoint con varios usuarios
usuarios_test = [1, 2, 3, 99]  # Probar usuarios que existan y uno que no

for id_usuario in usuarios_test:
    print(f"2️⃣ Probando cupones para usuario ID={id_usuario}...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/cupones/disponibles/{id_usuario}",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                cupones = data['data']['cupones']
                total = data['data']['total']
                mensaje = data['data']['mensaje']
                
                print(f"   ✅ Respuesta exitosa: {total} cupones disponibles")
                
                if cupones:
                    print(f"      📜 Cupones:")
                    for cupon in cupones[:3]:  # Mostrar solo los primeros 3
                        print(f"         • {cupon['codigo']}: {cupon['descuento']}% OFF")
                        if cupon.get('razon'):
                            print(f"           {cupon['razon']}")
                else:
                    print(f"      ℹ️  {mensaje}")
            else:
                print(f"   ⚠️  Respuesta con success=false")
        else:
            print(f"   ⚠️  Status code: {response.status_code}")
            print(f"      {response.text[:200]}")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()

print("="*70)
print("✅ Test completado")
print("="*70 + "\n")
