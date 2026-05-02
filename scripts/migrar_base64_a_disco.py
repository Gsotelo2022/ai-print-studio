"""
Migración: Pedidos_detalle.imagen (Base64 VARCHAR MAX) → archivos en disco
=========================================================================
Ejecutar UNA SOLA VEZ contra la base de datos de producción.

1. Lee cada fila de Pedidos_detalle que tenga imagen en Base64
2. Decodifica y guarda el archivo PNG en backend/uploads/designs/
3. Actualiza imagen_ruta con la ruta relativa del archivo
4. Establece imagen = NULL para liberar espacio

Prerrequisito: ejecutar primero el script SQL de SQL Server que agrega
la columna imagen_ruta VARCHAR(500) a Pedidos_detalle.

Uso:
    cd backend/api_python
    python ../../scripts/migrar_base64_a_disco.py [--dry-run] [--batch 100]
"""

import argparse
import base64
import hashlib
import sys
from datetime import datetime
from pathlib import Path

# Ajustar el path para encontrar db.py
SCRIPT_DIR  = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent / "backend"
API_PY_DIR  = BACKEND_DIR / "api_python"
sys.path.insert(0, str(API_PY_DIR))

from db import get_connection

UPLOADS_DIR = BACKEND_DIR / "uploads" / "designs"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================

def es_base64(valor: str) -> bool:
    """Devuelve True si parece un data-URI base64 o una cadena base64 pura."""
    if not valor:
        return False
    v = valor.strip()
    return v.startswith("data:image") or (len(v) > 100 and ";" not in v and "/" not in v[:10])


def extraer_bytes_base64(valor: str) -> bytes | None:
    try:
        v = valor.strip()
        if v.startswith("data:image"):
            _, encoded = v.split(",", 1)
            return base64.b64decode(encoded)
        return base64.b64decode(v)
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description="Migrar imágenes Base64 de BD a disco")
    parser.add_argument("--dry-run", action="store_true", help="Solo reportar, no escribir nada")
    parser.add_argument("--batch", type=int, default=100, help="Registros por lote (default: 100)")
    args = parser.parse_args()

    dry = args.dry_run
    batch_size = args.batch

    print("=" * 60)
    print("  Migración Base64 → Disco")
    print(f"  Modo: {'DRY-RUN (sin cambios)' if dry else 'REAL — escribirá archivos y actualizará BD'}")
    print(f"  Directorio destino: {UPLOADS_DIR}")
    print("=" * 60)

    conn = get_connection()
    cur  = conn.cursor()

    # Columna imagen_ruta debe existir
    try:
        cur.execute("SELECT TOP 1 imagen_ruta FROM Pedidos_detalle")
    except Exception:
        print("\n❌ ERROR: La columna 'imagen_ruta' no existe en Pedidos_detalle.")
        print("   Ejecutá primero el script SQL:")
        print("   scripts/phase4_sqlserver_alteraciones.sql")
        sys.exit(1)

    # Contar registros que tienen Base64
    cur.execute("""
        SELECT COUNT(*)
        FROM Pedidos_detalle
        WHERE imagen IS NOT NULL
          AND imagen <> ''
          AND imagen_ruta IS NULL
    """)
    total = cur.fetchone()[0]

    if total == 0:
        print("\n✅ No hay registros con imagen Base64 pendientes de migrar.")
        sys.exit(0)

    print(f"\nRegistros a migrar: {total}")

    migrados   = 0
    errores    = 0
    omitidos   = 0
    offset     = 0

    while True:
        cur.execute("""
            SELECT id_detalle, imagen, id_pedido
            FROM Pedidos_detalle
            WHERE imagen IS NOT NULL
              AND imagen <> ''
              AND imagen_ruta IS NULL
            ORDER BY id_detalle
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
        """, (offset, batch_size))

        filas = cur.fetchall()
        if not filas:
            break

        for id_detalle, imagen_raw, id_pedido in filas:
            if not es_base64(imagen_raw):
                print(f"  [OMITIR] id_detalle={id_detalle}: valor no parece Base64")
                omitidos += 1
                continue

            img_bytes = extraer_bytes_base64(imagen_raw)
            if not img_bytes:
                print(f"  [ERROR]  id_detalle={id_detalle}: no se pudo decodificar Base64")
                errores += 1
                continue

            hash_md5   = hashlib.md5(img_bytes).hexdigest()
            timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_alm = f"pedido{id_pedido}_det{id_detalle}_{hash_md5[:8]}.png"
            ruta_disco = UPLOADS_DIR / nombre_alm
            ruta_rel   = f"uploads/designs/{nombre_alm}"

            if not dry:
                ruta_disco.write_bytes(img_bytes)
                cur.execute("""
                    UPDATE Pedidos_detalle
                    SET imagen_ruta = ?, imagen = NULL
                    WHERE id_detalle = ?
                """, (ruta_rel, id_detalle))

            migrados += 1
            if migrados % 10 == 0:
                print(f"  [{migrados}/{total}] Migrados...")
                if not dry:
                    conn.commit()

        if not dry:
            conn.commit()

        offset += batch_size
        if len(filas) < batch_size:
            break

    cur.close()
    conn.close()

    print("\n" + "=" * 60)
    print(f"  ✅ Migrados:  {migrados}")
    print(f"  ⚠️  Omitidos: {omitidos}")
    print(f"  ❌ Errores:   {errores}")
    if dry:
        print("  (DRY-RUN: ningún cambio fue guardado)")
    print("=" * 60)


if __name__ == "__main__":
    main()
