"""
Script de prueba para la función obtener_productos_db corregida
"""
import sys
sys.path.append('c:\\projects\\ai-print-studio\\agentes-Ollama')

from agente_productos import obtener_productos_db, generar_catalogo_sin_ollama
import json

print("="*60)
print("PROBANDO FUNCIÓN obtener_productos_db()")
print("="*60)
print()

productos = obtener_productos_db()

print()
print("="*60)
print("RESULTADO:")
print("="*60)
print(json.dumps(productos, indent=2, ensure_ascii=False))

print()
print("="*60)
print("PROBANDO FALLBACK (sin OLLAMA):")
print("="*60)
print()

catalogo = generar_catalogo_sin_ollama(productos)
print(json.dumps(catalogo, indent=2, ensure_ascii=False))

print()
print(f"Total productos: {len(catalogo)}")
