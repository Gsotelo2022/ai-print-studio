import pyodbc

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=.\\SQLEXPRESS01;'
    'DATABASE=PrendeteRock;'
    'Trusted_Connection=yes;'
)

cursor = conn.cursor()

# Obtener columnas de Archivos_Diseno
cursor.execute("""
    SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'Archivos_Diseno'
    ORDER BY ORDINAL_POSITION
""")

print("=== Columnas de Archivos_Diseno ===")
for row in cursor.fetchall():
    col_name, data_type, max_len, nullable = row
    len_str = f"({max_len})" if max_len else ""
    print(f"  - {col_name} {data_type}{len_str} {'NULL' if nullable == 'YES' else 'NOT NULL'}")

conn.close()
