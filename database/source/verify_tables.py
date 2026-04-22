#!/usr/bin/env python3
import pyodbc

try:
    # Conectar a la base de datos
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=.\\SQLEXPRESS01;DATABASE=PrendeteRock;Trusted_Connection=yes;'
    conn = pyodbc.connect(conn_str)
    conn.autocommit = True
    cur = conn.cursor()
    
    # Verificar tablas
    cur.execute("""
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA='dbo' AND TABLE_CATALOG='PrendeteRock'
        ORDER BY TABLE_NAME
    """)
    
    tables = cur.fetchall()
    print("TABLAS ENCONTRADAS:")
    print("-" * 40)
    
    if tables:
        for table in tables:
            table_name = table[0]
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
            print(f"  ✓ {table_name}: {count} registros")
        print("-" * 40)
        print("✓ BASE DE DATOS CREADA CORRECTAMENTE")
    else:
        print("  ✗ No se encontraron tablas")
        print("✗ ERROR: La base de datos no fue creada correctamente")
    
    cur.close()
    conn.close()

except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
