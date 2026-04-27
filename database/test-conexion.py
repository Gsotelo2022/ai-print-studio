"""
Test de conexión a SQL Server
Prueba diferentes configuraciones para encontrar la correcta
"""

import pyodbc

print("="*60)
print("DIAGNÓSTICO DE CONEXIÓN SQL SERVER")
print("="*60)

# Configuraciones a probar
configuraciones = [
    {
        'nombre': 'MSSQLSERVER (instancia por defecto)',
        'string': 'Driver={SQL Server};Server=localhost;Database=PrendeteRock;Trusted_Connection=yes;'
    },
    {
        'nombre': 'localhost\\SQLEXPRESS01',
        'string': 'Driver={SQL Server};Server=localhost\\SQLEXPRESS01;Database=PrendeteRock;Trusted_Connection=yes;'
    },
    {
        'nombre': '.\\SQLEXPRESS01',
        'string': 'Driver={SQL Server};Server=.\\SQLEXPRESS01;Database=PrendeteRock;Trusted_Connection=yes;'
    },
    {
        'nombre': 'localhost\\SQLEXPRESS',
        'string': 'Driver={SQL Server};Server=localhost\\SQLEXPRESS;Database=PrendeteRock;Trusted_Connection=yes;'
    },
    {
        'nombre': '.\\SQLEXPRESS',
        'string': 'Driver={SQL Server};Server=.\\SQLEXPRESS;Database=PrendeteRock;Trusted_Connection=yes;'
    },
    {
        'nombre': '(local)',
        'string': 'Driver={SQL Server};Server=(local);Database=PrendeteRock;Trusted_Connection=yes;'
    },
    {
        'nombre': 'ODBC Driver 17 - localhost',
        'string': 'Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=PrendeteRock;Trusted_Connection=yes;'
    },
    {
        'nombre': 'ODBC Driver 17 - SQLEXPRESS01',
        'string': 'Driver={ODBC Driver 17 for SQL Server};Server=localhost\\SQLEXPRESS01;Database=PrendeteRock;Trusted_Connection=yes;'
    }
]

print("\nProbando configuraciones...\n")

for config in configuraciones:
    print(f"Probando: {config['nombre']}")
    try:
        conn = pyodbc.connect(config['string'], timeout=3)
        cur = conn.cursor()
        
        # Obtener nombre de BD
        cur.execute("SELECT DB_NAME()")
        db_name = cur.fetchone()[0]
        
        # Contar tablas
        cur.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        num_tablas = cur.fetchone()[0]
        
        print(f"  ✅ CONECTADO!")
        print(f"     Base de datos: {db_name}")
        print(f"     Tablas: {num_tablas}")
        print(f"\n  String de conexión exitosa:")
        print(f"  {config['string']}")
        print()
        
        cur.close()
        conn.close()
        
        # Si llegamos aquí, esta configuración funciona
        print("\n" + "="*60)
        print("SOLUCIÓN ENCONTRADA")
        print("="*60)
        print(f"\nUsa esta configuración en ejecutar-migracion.py:")
        print(f"Reemplaza la línea 60 con:")
        print(f"\nconn_string = '{config['string']}'")
        print()
        
        break
        
    except pyodbc.Error as e:
        print(f"  ❌ Error: {str(e)[:80]}")
        print()
    except Exception as e:
        print(f"  ❌ Error: {e}")
        print()

else:
    print("\n" + "="*60)
    print("NO SE PUDO CONECTAR CON NINGUNA CONFIGURACIÓN")
    print("="*60)
    print("\nVerifica:")
    print("1. SQL Server está corriendo:")
    print("   - Abre 'Servicios' de Windows")
    print("   - Busca 'SQL Server'")
    print("   - Verifica que esté 'En ejecución'")
    print("\n2. La base de datos PrendeteRock existe:")
    print("   - Abre SQL Server Management Studio (SSMS)")
    print("   - Conéctate al servidor")
    print("   - Verifica que PrendeteRock esté en la lista")
    print("\n3. Drivers SQL disponibles:")
    
    print("\nDrivers instalados:")
    for driver in pyodbc.drivers():
        print(f"  - {driver}")
    print()

print("="*60)
