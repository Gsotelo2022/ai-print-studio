import os
import psycopg2

# Variables de entorno
PG_HOST = os.getenv("PG_HOST", "127.0.0.1")
PG_PORT = int(os.getenv("PG_PORT", "5432"))
PG_DB = os.getenv("PG_DB", "PrendeteRock")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "Pasteldepapas123#")


def get_connection():
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            dbname=PG_DB,
            user=PG_USER,
            password=PG_PASSWORD,
            connect_timeout=5,
            sslmode="disable"
        )
        return conn

    except Exception as e:
        print("❌ ERROR CONEXION DB:")
        print(f"Host: {PG_HOST}:{PG_PORT}")
        print(f"DB: {PG_DB}")
        print(f"User: {PG_USER}")
        print("Detalle:", str(e))
        raise