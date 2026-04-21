import pyodbc   

try: 
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost\\SQLEXPRESS01;'
        'DATABASE=PrendeteRock;'
        'Trusted_Connection=yes;'
    )
    print("Conexión exitosa a la base de datos.")
except Exception as ex:  
    print(f"Error al conectar a la base de datos: {ex}")
    
finally:    
    try:
        conn.close()
        print("Conexión cerrada.")
    except Exception as ex:
        print(f"Error al cerrar la conexión: {ex}")