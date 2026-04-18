import os
from dotenv import load_dotenv
import pyodbc

load_dotenv()

# Leer configuración desde variables de entorno
DB_DRIVER = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
DB_SERVER = os.getenv('DB_SERVER', r'localhost\\SQLEXPRESS')
DB_NAME = os.getenv('DB_NAME', 'PrendeteRock')
DB_UID = os.getenv('DB_UID', '')
DB_PWD = os.getenv('DB_PWD', '')
TRUSTED = os.getenv('TRUSTED_CONNECTION', 'yes').lower() in ('1', 'true', 'yes')


def build_conn_str():
    # Construir connection string compatible con pyodbc
    # Si se usan credenciales, se usan UID/PWD, si no usar Trusted_Connection
    parts = [f"DRIVER={{{DB_DRIVER}}}", f"SERVER={DB_SERVER}", f"DATABASE={DB_NAME}"]
    if TRUSTED and (DB_UID == '' and DB_PWD == ''):
        parts.append('Trusted_Connection=yes')
    else:
        parts.append(f"UID={DB_UID}")
        parts.append(f"PWD={DB_PWD}")

    return ';'.join(parts)


def get_connection():
    """Devuelve una conexión pyodbc. Lanza RuntimeError en caso de fallo."""
    conn_str = build_conn_str()
    try:
        conn = pyodbc.connect(conn_str, autocommit=True)
        # Aseguramos encoding utf-8 en pyodbc (depende del driver)
        return conn
    except Exception as e:
        raise RuntimeError(f'No se pudo conectar a la base de datos: {e}')
