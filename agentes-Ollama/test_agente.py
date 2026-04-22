#!/usr/bin/env python3
"""
Test directo del agente (sin Flask)
Útil para debuguear sin levantar el servidor
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from agente_productos import (
    obtener_productos_db,
    construir_prompt,
    llamar_ollama,
    limpiar_respuesta
)

print("=" * 60)
print("🧪 TEST AGENTE IA")
print("=" * 60)

try:
    # 1. Conectar BD
    print("\n[1] Conectando a BD...")
    productos = obtener_productos_db()
    print(f"    ✓ {len(productos)} productos obtenidos\n")
    
    if not productos:
        print("    ❌ ERROR: No hay productos en BD!")
        sys.exit(1)
    
    # 2. Construir prompt
    print("[2] Construyendo prompt...")
    prompt = construir_prompt(productos)
    print(f"    ✓ Prompt: {len(prompt)} caracteres\n")
    
    # 3. Llamar OLLAMA
    print("[3] Llamando a OLLAMA (phi3:mini)...")
    print("    ⏳ Esto puede tomar 10-30 segundos...\n")
    respuesta = llamar_ollama(prompt)
    print(f"    ✓ Respuesta: {respuesta[:200]}...\n")
    
    # 4. Limpiar
    print("[4] Limpiando respuesta JSON...")
    resultado = limpiar_respuesta(respuesta)
    print(f"    ✓ Resultado:\n")
    
    import json
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
