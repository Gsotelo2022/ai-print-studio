"""
Test del endpoint /api/mis-disenos/{id_usuario}
Obtiene todos los diseños que un cliente ha subido o generado
"""
import requests
import json

# Usuario de prueba (Cliente Demo ID: 2)
USER_ID = 2

print(f"📥 Obteniendo diseños del usuario {USER_ID}...")
print()

try:
    response = requests.get(
        f"http://localhost:8000/api/mis-disenos/{USER_ID}",
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        result = response.json()
        
        if result['success']:
            data = result['data']
            
            print("✅ DISEÑOS OBTENIDOS EXITOSAMENTE")
            print("=" * 60)
            print(f"📊 Total de diseños: {data['total']}")
            print(f"🤖 Generados por IA: {data['total_generados_ia']}")
            print(f"📤 Subidos manualmente: {data['total_subidos']}")
            print()
            
            if data['disenos']:
                print("🎨 LISTA DE DISEÑOS:")
                print("=" * 60)
                
                for i, diseno in enumerate(data['disenos'], 1):
                    print(f"\n{i}. {diseno['nombre_original']}")
                    print(f"   ID: {diseno['id_archivo']}")
                    print(f"   Ruta: {diseno['ruta_archivo']}")
                    print(f"   Thumbnail: {diseno['ruta_thumbnail']}")
                    print(f"   Dimensiones: {diseno['dimensiones']} ({diseno['tamano_kb']} KB)")
                    print(f"   Generado IA: {'Sí' if diseno['es_generado_ia'] else 'No'}")
                    
                    if diseno['es_generado_ia'] and diseno['prompt_usado']:
                        print(f"   Prompt: {diseno['prompt_usado'][:80]}{'...' if len(diseno['prompt_usado']) > 80 else ''}")
                    
                    print(f"   Fecha: {diseno['fecha_subida']}")
                    print(f"   Usado en: {diseno['estadisticas']['veces_usado']} pedido(s)")
                    
                    if diseno['estadisticas']['ultimo_uso']:
                        print(f"   Último uso: {diseno['estadisticas']['ultimo_uso']}")
                
                print("\n" + "=" * 60)
            else:
                print("ℹ️  Este usuario no tiene diseños aún")
        else:
            print("❌ Error en respuesta")
            print(json.dumps(result, indent=2))
    else:
        print("❌ ERROR EN LA PETICIÓN")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")
