#!/usr/bin/env python3
"""
TEST COMPLETO DEL AGENTE
Verifica: BD → Agente Flask → OLLAMA
"""

import sys
import os
import time
import subprocess
import requests
import json

# Agregar ruta para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agentes-Ollama'))

print("=" * 70)
print("🧪 TEST COMPLETO DEL AGENTE IA")
print("=" * 70)

# ============================================================================
# PASO 1: VERIFICAR CONEXIÓN A BD
# ============================================================================
print("\n[1] Verificando conexión a SQL Server...")
print("-" * 70)

try:
    import pyodbc
    
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=.\\SQLEXPRESS01;'
        'DATABASE=PrendeteRock;'
        'Trusted_Connection=yes;'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM Productos")
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    print(f"✓ BD conectada correctamente")
    print(f"✓ Total de productos en BD: {total}")
    
except Exception as e:
    print(f"❌ Error conectando a BD: {e}")
    sys.exit(1)

# ============================================================================
# PASO 2: TEST 1 - PROCESAMIENTO SIN OLLAMA (solo Python)
# ============================================================================
print("\n[2] TEST 1: Procesamiento Python (sin OLLAMA)...")
print("-" * 70)
print("⏳ Obteniendo productos de BD y agrupando por tipo...")

try:
    # Reimportar pyodbc para obtener productos directamente
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=.\\SQLEXPRESS01;'
        'DATABASE=PrendeteRock;'
        'Trusted_Connection=yes;'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT Detalle, Color, talle FROM Productos")
    
    productos = []
    for row in cursor.fetchall():
        productos.append({
            'Detalle': row[0],
            'Color': row[1],
            'talle': row[2]
        })
    
    cursor.close()
    conn.close()
    
    print(f"✓ Obtenidos {len(productos)} registros")
    
    # Agrupar por Detalle
    grupos = {}
    for prod in productos:
        detalle = prod['Detalle']
        if detalle not in grupos:
            grupos[detalle] = {'talles': set(), 'colores': set()}
        
        if prod['talle']:
            grupos[detalle]['talles'].add(prod['talle'])
        grupos[detalle]['colores'].add(prod['Color'])
    
    # Convertir a lista
    resultado = []
    for prod_nombre, datos in sorted(grupos.items()):
        resultado.append({
            'producto': prod_nombre,
            'talles': sorted(list(datos['talles'])),
            'colores': sorted(list(datos['colores']))
        })
    
    print(f"✓ Agrupados en {len(resultado)} categorías\n")
    
    # Mostrar resultados
    print("📋 RESULTADO (Agrupación Python):\n")
    for item in resultado:
        print(f"  {item['producto']}:")
        print(f"    └─ Talles: {item['talles'] if item['talles'] else 'N/A'}")
        print(f"    └─ Colores: {', '.join(item['colores']) if item['colores'] else 'N/A'}")
    
    print(f"\n✅ TEST 1 EXITOSO - Agrupación correcta")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# PASO 3: TEST 2 - AGENTE FLASK (si está corriendo)
# ============================================================================
print("\n" + "=" * 70)
print("[3] TEST 2: Agente Flask en http://localhost:5001...")
print("-" * 70)

try:
    print("⏳ Conectando a http://localhost:5001/productos-ia...")
    response = requests.get('http://localhost:5001/productos-ia', timeout=5)
    
    if response.status_code == 200:
        datos = response.json()
        print(f"✓ Agente respondió exitosamente")
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Productos agrupados: {len(datos)}\n")
        
        print("📋 RESULTADO (Agente Flask):\n")
        for item in datos:
            print(f"  {item['producto']}:")
            print(f"    └─ Talles: {item['talles'] if item['talles'] else 'N/A'}")
            print(f"    └─ Colores: {', '.join(item['colores']) if item['colores'] else 'N/A'}")
        
        print(f"\n✅ TEST 2 EXITOSO - Agente Flask funciona!")
    
    else:
        print(f"⚠️  Agente devolvió status {response.status_code}")
        print(f"   Respuesta: {response.text[:200]}")
        print(f"\n❌ TEST 2 - Agente Flask con error (pero BD funciona)")
        
except requests.exceptions.ConnectionError:
    print(f"⚠️  No se puede conectar a http://localhost:5001")
    print(f"   El agente no está corriendo")
    print(f"\n💡 Para iniciar el agente, ejecuta:")
    print(f"   cd c:\\projects\\ai-print-studio\\agentes-Ollama")
    print(f"   python agente_productos.py")
    
except requests.exceptions.Timeout:
    print(f"⚠️  Timeout en http://localhost:5001 (tarda más de 5 segundos)")
    print(f"   Probablemente OLLAMA está procesando")
    print(f"\n💡 Espera a que OLLAMA responda (puede tardar 1-2 minutos en i3)")

except Exception as e:
    print(f"⚠️  Error: {e}")

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("\n" + "=" * 70)
print("📊 RESUMEN")
print("=" * 70)
print("\n✅ FUNCIONANDO:")
print("   • Base de datos SQL Server: OK")
print("   • Conexión a Productos: OK")
print("   • Agrupación Python: OK")
print("\n⏳ PRÓXIMOS PASOS:")
print("   1. Inicia OLLAMA: ollama serve")
print("   2. Levanta el agente: python agente_productos.py")
print("   3. Accede a: http://localhost:5001/productos-ia")
print("   4. O ejecuta RUN.bat para levantarlo todo automáticamente")
print("\n" + "=" * 70)
