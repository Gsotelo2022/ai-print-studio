import os
import psycopg2

# Configuración de conexión PostgreSQL (sobreescribible via variables de entorno)
PG_HOST = os.getenv("PG_HOST", "127.0.0.1")
PG_PORT     = int(os.getenv("PG_PORT", "5432"))
PG_DB       = os.getenv("PG_DB",       "PrendeteRock")
PG_USER     = os.getenv("PG_USER",     "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "Pasteldepapas123#")


def get_connection():
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",   # ⚠️ clave
            port="5432",
            dbname="PrendeteRock",
            user="postgres",
            password="Pasteldepapas123#",
            connect_timeout=5,   # evita cuelgues
            sslmode="disable"    # ⚠️ MUY IMPORTANTE en local
        )
        return conn
    except Exception as e:
        print("ERROR CONEXION DB:", str(e))
        raise
