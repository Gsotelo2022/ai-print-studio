"""
Script de prueba para verificar que rembg funciona correctamente
"""
from PIL import Image
from rembg import remove
import io
import time

print("🔄 Creando imagen de prueba...")
# Crear una imagen de prueba simple
test_image = Image.new('RGB', (200, 200), color='red')

print("⏱️  Iniciando remoción de fondo (midiendo tiempo)...")
start = time.time()

# Remover el fondo
result = remove(test_image)

elapsed = time.time() - start

print(f"✅ ¡Fondo removido exitosamente en {elapsed:.2f} segundos!")
print(f"   Tamaño resultado: {result.size}")
print(f"   Modo: {result.mode}")
print()
print("✅ rembg está funcionando correctamente.")
print("   El removedor de fondo en la app debería funcionar ahora.")
