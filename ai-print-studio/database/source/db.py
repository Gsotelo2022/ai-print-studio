import pyodbc

def get_connection():
    """Conecta a SQL Server usando Trusted Connection (autenticación de Windows)"""
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost\\SQLEXPRESS01;'
            'DATABASE=PrendeteRock;'
            'Trusted_Connection=yes;'
        )
        return conn
    except Exception as e:
        raise RuntimeError(f'No se pudo conectar a la base de datos: {e}')
