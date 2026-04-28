"""
Test específico para el método obtener_estadisticas_ventas
"""

import sys
sys.path.append('../agentes-Ollama/agente-cupones')

from agente_descuentos import AgenteDescuentos

print("\n" + "="*70)
print("🧪 TEST: Método obtener_estadisticas_ventas")
print("="*70 + "\n")

agente = AgenteDescuentos()

print("1️⃣ Llamando a obtener_estadisticas_ventas()...")
try:
    stats = agente.obtener_estadisticas_ventas()
    
    if stats:
        print(f"   ✅ Estadísticas obtenidas\n")
        
        print("   📊 Resumen:")
        if 'ultimo_mes' in stats:
            print(f"      Pedidos último mes: {stats['ultimo_mes'].get('total_pedidos', 0)}")
            print(f"      Ticket promedio: ${stats['ultimo_mes'].get('ticket_promedio', 0):,.2f}")
            print(f"      Ingresos: ${stats['ultimo_mes'].get('ingresos_totales', 0):,.2f}")
        
        if 'productos_top' in stats:
            print(f"      Productos top: {len(stats['productos_top'])}")
            
        if 'clientes' in stats:
            print(f"      Clientes nuevos: {stats['clientes'].get('nuevos', 0)}")
            print(f"      Clientes recurrentes: {stats['clientes'].get('recurrentes', 0)}")
    else:
        print("   ⚠️  Estadísticas vacías")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70 + "\n")
