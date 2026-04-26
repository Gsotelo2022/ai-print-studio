import pyodbc

conn = pyodbc.connect('Driver={SQL Server};Server=localhost\\SQLEXPRESS01;Database=PrendeteRock;Trusted_Connection=yes;')
cur = conn.cursor()

print("\n=== TABLAS ACTUALES EN PrendeteRock ===\n")
cur.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' ORDER BY TABLE_NAME")

for row in cur.fetchall():
    table_name = row[0]
    
    # Contar registros
    try:
        cur.execute(f"SELECT COUNT(*) FROM [{table_name}]")
        count = cur.fetchone()[0]
        print(f"  - {table_name:<30} ({count} registros)")
    except:
        print(f" - {table_name:<30} (error al contar)")

print()
cur.close()
conn.close()
