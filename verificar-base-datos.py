#!/usr/bin/env python3
"""
Script para verificar la conexión a la base de datos
y validar que todas las tablas estén creadas correctamente
"""
import pyodbc
import sys

def test_connection():
    """Prueba la conexión a SQL Server"""
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=.\\SQLEXPRESS01;'
            'DATABASE=PrendeteRock;'
            'Trusted_Connection=yes;'
        )
        print("✅ Conexión exitosa a SQL Server")
        return conn
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def verify_tables(conn):
    """Verifica que todas las tablas necesarias existan"""
    required_tables = ['Usuarios', 'Productos', 'Pedidos', 'Pedidos_detalle']
    cursor = conn.cursor()
    
    print("\n📋 Verificando tablas...")
    print("-" * 50)
    
    all_ok = True
    for table in required_tables:
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = '{table}'
        """)
        exists = cursor.fetchone()[0]
        
        if exists:
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"✅ {table:20} - {count} registros")
        else:
            print(f"❌ {table:20} - NO EXISTE")
            all_ok = False
    
    cursor.close()
    return all_ok

def show_table_structure(conn, table_name):
    """Muestra la estructura de una tabla"""
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT 
            COLUMN_NAME, 
            DATA_TYPE, 
            CHARACTER_MAXIMUM_LENGTH,
            IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = '{table_name}'
        ORDER BY ORDINAL_POSITION
    """)
    
    print(f"\n📊 Estructura de {table_name}:")
    print("-" * 70)
    print(f"{'Campo':<25} {'Tipo':<20} {'Tamaño':<10} {'Nullable':<10}")
    print("-" * 70)
    
    for row in cursor.fetchall():
        col_name = row[0]
        data_type = row[1]
        max_length = row[2] if row[2] else 'N/A'
        nullable = 'Sí' if row[3] == 'YES' else 'No'
        print(f"{col_name:<25} {data_type:<20} {str(max_length):<10} {nullable:<10}")
    
    cursor.close()

if __name__ == "__main__":
    print("=" * 70)
    print("🔍 VERIFICACIÓN DE BASE DE DATOS - PrendeteRock")
    print("=" * 70)
    
    # Probar conexión
    conn = test_connection()
    if not conn:
        print("\n❌ No se pudo conectar a la base de datos")
        print("\n💡 Asegúrate de que:")
        print("   1. SQL Server esté ejecutándose")
        print("   2. La instancia sea .\\SQLEXPRESS01")
        print("   3. La base de datos 'PrendeteRock' exista")
        sys.exit(1)
    
    # Verificar tablas
    if not verify_tables(conn):
        print("\n❌ Falta crear algunas tablas")
        print("\n💡 Ejecuta el script:")
        print("   database\\estructura-BDD-Prendete-Rock.sql")
        conn.close()
        sys.exit(1)
    
    # Mostrar estructura de tablas principales
    show_table_structure(conn, 'Usuarios')
    show_table_structure(conn, 'Productos')
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("✅ BASE DE DATOS VERIFICADA CORRECTAMENTE")
    print("=" * 70)
