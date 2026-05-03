"""
Test de conexión a PostgreSQL (pgAdmin) — AI Print Studio
==========================================================
Verifica:
  1. Que psycopg2 está instalado
  2. Que la conexión a la BD PrendeteRock funciona
  3. Que las tablas principales existen
  4. Que se puede crear un usuario administrador
  5. Que se puede crear un usuario cliente

Requisitos previos:
  - Haber ejecutado scripts/phase4_postgresql_schema.sql en pgAdmin
  - pip install psycopg2-binary (o psycopg2)

Variables de conexión (modificar si tus credenciales son distintas):
  PG_HOST     → host del servidor (default: localhost)
  PG_PORT     → puerto           (default: 5432)
  PG_DB       → nombre de la BD  (default: prendeterock)
  PG_USER     → usuario postgres (default: postgres)
  PG_PASSWORD → contraseña       (pedida por consola si no está definida)

Uso:
  cd test-genericos
  python test_postgresql.py
  python test_postgresql.py --host 192.168.1.10 --password mipass
"""

import sys
import os
import hashlib
import argparse
import getpass
from datetime import datetime

# ── Configuración de conexión ──────────────────────────────────────

DEFAULT_HOST = os.getenv("PG_HOST", "localhost")
DEFAULT_PORT = int(os.getenv("PG_PORT", "5432"))
DEFAULT_DB   = os.getenv("PG_DB",   "PrendeteRock")
DEFAULT_USER = os.getenv("PG_USER", "postgres")


# ── Utilidades de consola ──────────────────────────────────────────

def ok(msg):   print(f"  ✅ {msg}")
def fail(msg): print(f"  ❌ {msg}")
def info(msg): print(f"  ℹ️  {msg}")
def title(msg):
    print()
    print("=" * 60)
    print(f"  {msg}")
    print("=" * 60)


def hash_password(pw: str) -> str:
    """SHA-256 — mismo algoritmo usado en el backend FastAPI."""
    return hashlib.sha256(pw.encode()).hexdigest()


# ── Tests ──────────────────────────────────────────────────────────

def test_psycopg2():
    title("TEST 1: psycopg2 disponible")
    try:
        import psycopg2
        ok(f"psycopg2 versión: {psycopg2.__version__}")
        return True
    except ImportError:
        fail("psycopg2 no está instalado.")
        info("Instalalo con:  pip install psycopg2-binary")
        return False


def test_conexion(conn_params: dict):
    title("TEST 2: Conexión a PostgreSQL")
    import psycopg2

    try:
        conn = psycopg2.connect(**conn_params)
        cur  = conn.cursor()

        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        ok(f"Conectado a: {version[:60]}...")

        cur.execute("SELECT current_database();")
        db = cur.fetchone()[0]
        ok(f"Base de datos activa: {db}")

        cur.close()
        conn.close()
        return True

    except Exception as e:
        fail(f"No se pudo conectar: {e}")
        info("Verificá: servidor corriendo, credenciales, y que la BD existe en pgAdmin.")
        return False


def test_tablas(conn_params: dict):
    title("TEST 3: Tablas del schema")
    import psycopg2

    tablas_esperadas = [
        "usuarios", "productos", "producto_variantes",
        "producto_atributos", "producto_atributo_valores",
        "variante_atributos", "archivos_diseno",
        "pedidos", "pedidos_items", "pagos",
        "cupones", "descuentos",
    ]

    try:
        conn = psycopg2.connect(**conn_params)
        cur  = conn.cursor()

        cur.execute("""
            SELECT table_name
            FROM   information_schema.tables
            WHERE  table_schema = 'public'
              AND  table_type   = 'BASE TABLE'
            ORDER  BY table_name;
        """)
        existentes = {r[0] for r in cur.fetchall()}

        todas_ok = True
        for tabla in tablas_esperadas:
            if tabla in existentes:
                ok(f"Tabla '{tabla}' existe")
            else:
                fail(f"Tabla '{tabla}' NO encontrada")
                todas_ok = False

        sobrantes = existentes - set(tablas_esperadas)
        if sobrantes:
            info(f"Tablas adicionales encontradas: {', '.join(sorted(sobrantes))}")

        cur.close()
        conn.close()
        return todas_ok

    except Exception as e:
        fail(f"Error al verificar tablas: {e}")
        return False


def test_indices(conn_params: dict):
    title("TEST 4: Índices compuestos (Phase 4)")
    import psycopg2

    indices_esperados = [
        "ix_pedidos_usuario_fecha",
        "ix_pedidos_estado_pago_fecha",
        "ix_cupones_codigo",
        "idx_usuarios_email",
    ]

    try:
        conn = psycopg2.connect(**conn_params)
        cur  = conn.cursor()

        cur.execute("""
            SELECT indexname FROM pg_indexes
            WHERE  schemaname = 'public'
            ORDER  BY indexname;
        """)
        existentes = {r[0] for r in cur.fetchall()}

        todas_ok = True
        for idx in indices_esperados:
            if idx in existentes:
                ok(f"Índice '{idx}' existe")
            else:
                fail(f"Índice '{idx}' NO encontrado")
                todas_ok = False

        cur.close()
        conn.close()
        return todas_ok

    except Exception as e:
        fail(f"Error al verificar índices: {e}")
        return False


def test_crear_usuarios(conn_params: dict):
    title("TEST 5: Crear usuario administrador y cliente")
    import psycopg2
    from psycopg2.extras import RealDictCursor

    ts = datetime.now().strftime("%H%M%S")   # sufijo para evitar conflictos en re-ejecuciones

    usuarios_seed = [
        {
            "nombre":       "Admin Principal",
            "email":        f"admin_{ts}@prendeterock.com",
            "telefono":     "1160000001",
            "password_raw": "Admin1234!",
            "tipo":         "admin",
        },
        {
            "nombre":       "Cliente Demo",
            "email":        f"cliente_{ts}@prendeterock.com",
            "telefono":     "1160000002",
            "password_raw": "Cliente1234!",
            "tipo":         "cliente",
        },
    ]

    try:
        conn = psycopg2.connect(**conn_params)
        cur  = conn.cursor(cursor_factory=RealDictCursor)
        todas_ok = True

        for u in usuarios_seed:
            pw_hash = hash_password(u["password_raw"])
            try:
                cur.execute("""
                    INSERT INTO usuarios (nombre, email, telefono, password_user, tipo)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id_usuario, nombre, email, tipo, fecha_registro;
                """, (u["nombre"], u["email"], u["telefono"], pw_hash, u["tipo"]))

                row = cur.fetchone()
                ok(
                    f"[{row['tipo'].upper()}] id={row['id_usuario']} "
                    f"| {row['nombre']} <{row['email']}> "
                    f"| registrado: {row['fecha_registro'].strftime('%Y-%m-%d %H:%M:%S')}"
                )
                info(f"  Contraseña (original): {u['password_raw']}")
                info(f"  Contraseña (hash SHA-256): {pw_hash[:20]}...")

            except psycopg2.errors.UniqueViolation:
                conn.rollback()
                fail(f"Email '{u['email']}' ya existe en la BD (ejecutaste el test antes?)")
                todas_ok = False
                # Reconectar cursor limpio
                cur = conn.cursor(cursor_factory=RealDictCursor)
                continue

        conn.commit()

        # Verificar que existen en la BD
        print()
        info("Verificando registros insertados:")
        cur.execute("""
            SELECT id_usuario, nombre, email, tipo, fecha_registro
            FROM   usuarios
            ORDER  BY id_usuario DESC
            LIMIT  5;
        """)
        for row in cur.fetchall():
            info(f"  id={row['id_usuario']} | {row['tipo']:8} | {row['nombre']} <{row['email']}>")

        cur.close()
        conn.close()
        return todas_ok

    except Exception as e:
        fail(f"Error al crear usuarios: {e}")
        return False


# ── Main ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Test de conexión PostgreSQL — AI Print Studio")
    parser.add_argument("--host",     default=DEFAULT_HOST, help=f"Host PostgreSQL (default: {DEFAULT_HOST})")
    parser.add_argument("--port",     type=int, default=DEFAULT_PORT, help=f"Puerto (default: {DEFAULT_PORT})")
    parser.add_argument("--db",       default=DEFAULT_DB,   help=f"Nombre BD (default: {DEFAULT_DB})")
    parser.add_argument("--user",     default=DEFAULT_USER, help=f"Usuario (default: {DEFAULT_USER})")
    parser.add_argument("--password", default=os.getenv("PG_PASSWORD"), help="Contraseña (si no se pasa, la pide)")
    parser.add_argument("--skip-usuarios", action="store_true", help="Omitir creación de usuarios seed")
    args = parser.parse_args()

    password = args.password
    if not password:
        password = getpass.getpass(f"Contraseña para '{args.user}' en {args.host}:{args.port}/{args.db}: ")

    conn_params = {
        "host":     args.host,
        "port":     args.port,
        "dbname":   args.db,
        "user":     args.user,
        "password": password,
    }

    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   Test PostgreSQL — AI Print Studio / Prendete Rock      ║")
    print(f"║   {args.host}:{args.port}/{args.db} ({args.user})".ljust(59) + "║")
    print("╚══════════════════════════════════════════════════════════╝")

    resultados = []

    resultados.append(("psycopg2 instalado",  test_psycopg2()))

    if not resultados[-1][1]:
        print("\n⛔ Sin psycopg2 no se puede continuar. Instalalo y volvé a correr.")
        sys.exit(1)

    resultados.append(("Conexión a PostgreSQL", test_conexion(conn_params)))

    if not resultados[-1][1]:
        print("\n⛔ Sin conexión no se pueden ejecutar los demás tests.")
        sys.exit(1)

    resultados.append(("Tablas del schema",    test_tablas(conn_params)))
    resultados.append(("Índices Phase 4",      test_indices(conn_params)))

    if not args.skip_usuarios:
        resultados.append(("Crear usuarios seed",  test_crear_usuarios(conn_params)))

    # ── Resumen ──────────────────────────────────────────────────────
    title("RESUMEN")
    aprobados = sum(1 for _, r in resultados if r)
    total     = len(resultados)
    for nombre, resultado in resultados:
        estado = "✅ PASS" if resultado else "❌ FAIL"
        print(f"  {estado}  {nombre}")
    print()
    print(f"  {aprobados}/{total} tests pasaron")

    if aprobados < total:
        print("  ⚠️  Revisá los errores arriba.")
        sys.exit(1)
    else:
        print("  🎉 Todos los tests pasaron. PostgreSQL listo.")


if __name__ == "__main__":
    main()
