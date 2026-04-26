"""
============================================================
SCRIPT: MIGRACIÓN DE IMÁGENES BASE64 → FILESYSTEM
============================================================
Descripción: Extraer imágenes de Pedidos_detalle_OLD y guardarlas como archivos
Fecha: 22 de abril de 2026
Autor: AI Print Studio
============================================================
"""

import pyodbc
import base64
import os
import hashlib
from pathlib import Path
from datetime import datetime
from PIL import Image
import io

# ============================================================
# CONFIGURACIÓN
# ============================================================

# Importar configuración de conexión
import sys
sys.path.append(str(Path(__file__).parent / 'source'))
from db import get_connection

# Directorios
BASE_DIR = Path(__file__).parent.parent
UPLOADS_DIR = BASE_DIR / 'uploads' / 'designs'
THUMBNAILS_DIR = BASE_DIR / 'uploads' / 'thumbnails'

# Crear directorios si no existen
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

print("🚀 MIGRACIÓN DE IMÁGENES BASE64 → FILESYSTEM")
print("=" * 60)
print(f"📁 Directorio de destino: {UPLOADS_DIR}")
print(f"📁 Directorio de miniaturas: {THUMBNAILS_DIR}")
print()

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def extraer_base64(imagen_str):
    """Extraer datos base64 de string con prefijo data:image/..."""
    if not imagen_str:
        return None
    
    # Remover prefijo si existe: data:image/png;base64,
    if imagen_str.startswith('data:'):
        partes = imagen_str.split(',', 1)
        if len(partes) == 2:
            return partes[1]
        return None
    
    return imagen_str


def guardar_imagen(imagen_base64, id_detalle, id_usuario):
    """
    Guardar imagen desde base64 a archivo
    Retorna: (ruta_archivo, ruta_thumbnail, metadata)
    """
    try:
        # Decodificar base64
        img_data = base64.b64decode(imagen_base64)
        
        # Calcular hash MD5
        hash_md5 = hashlib.md5(img_data).hexdigest()
        
        # Generar nombre de archivo único
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = f"user{id_usuario}_detalle{id_detalle}_{timestamp}_{hash_md5[:8]}.png"
        
        # Ruta completa
        ruta_completa = UPLOADS_DIR / nombre_archivo
        
        # Guardar archivo original
        with open(ruta_completa, 'wb') as f:
            f.write(img_data)
        
        # Abrir con PIL para obtener metadata y crear thumbnail
        img = Image.open(io.BytesIO(img_data))
        ancho, alto = img.size
        
        # Crear thumbnail (200x200 max)
        thumbnail_nombre = f"thumb_{nombre_archivo}"
        thumbnail_path = THUMBNAILS_DIR / thumbnail_nombre
        
        img_thumb = img.copy()
        img_thumb.thumbnail((200, 200), Image.Resampling.LANCZOS)
        img_thumb.save(thumbnail_path, 'PNG')
        
        # Ruta relativa para BD
        ruta_relativa = f"uploads/designs/{nombre_archivo}"
        ruta_thumb_relativa = f"uploads/thumbnails/{thumbnail_nombre}"
        
        metadata = {
            'nombre_original': f"diseño_{id_detalle}.png",
            'nombre_almacenado': nombre_archivo,
            'ruta_archivo': ruta_relativa,
            'ruta_thumbnail': ruta_thumb_relativa,
            'tipo_mime': 'image/png',
            'tamano_bytes': len(img_data),
            'ancho_px': ancho,
            'alto_px': alto,
            'hash_md5': hash_md5
        }
        
        return metadata
        
    except Exception as e:
        print(f"   ❌ Error al procesar imagen: {e}")
        return None


# ============================================================
# PROCESO PRINCIPAL
# ============================================================

def main():
    conn = None
    try:
        # Conectar a BD
        conn = get_connection()
        cur = conn.cursor()
        
        print("✅ Conectado a base de datos")
        print()
        
        # Obtener pedidos detalle con imágenes
        print("🔍 Buscando imágenes en Pedidos_detalle_OLD...")
        
        cur.execute("""
            SELECT 
                pd.id_detalle,
                pd.imagen,
                p.id_usuario
            FROM Pedidos_detalle_OLD pd
            INNER JOIN Pedidos_OLD p ON pd.id_pedido = p.id_pedido
            WHERE pd.imagen IS NOT NULL 
            AND LEN(pd.imagen) > 100
            ORDER BY pd.id_detalle
        """)
        
        rows = cur.fetchall()
        total = len(rows)
        
        if total == 0:
            print("⚠️  No se encontraron imágenes para migrar")
            return
        
        print(f"📊 Encontradas {total} imágenes para migrar")
        print()
        
        # Procesar cada imagen
        migradas = 0
        errores = 0
        
        for idx, row in enumerate(rows, 1):
            id_detalle, imagen_base64, id_usuario = row
            
            print(f"[{idx}/{total}] Procesando detalle #{id_detalle}...", end=" ")
            
            # Extraer base64 limpio
            imagen_limpia = extraer_base64(imagen_base64)
            
            if not imagen_limpia:
                print("⚠️  Sin datos base64 válidos")
                errores += 1
                continue
            
            # Guardar imagen
            metadata = guardar_imagen(imagen_limpia, id_detalle, id_usuario)
            
            if not metadata:
                errores += 1
                continue
            
            # Insertar en tabla Archivos_Diseno
            cur.execute("""
                INSERT INTO Archivos_Diseno (
                    id_usuario,
                    nombre_original,
                    nombre_almacenado,
                    ruta_archivo,
                    ruta_thumbnail,
                    tipo_mime,
                    tamano_bytes,
                    ancho_px,
                    alto_px,
                    hash_md5,
                    es_generado_ia,
                    fecha_subida
                )
                OUTPUT INSERTED.id_archivo
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, GETDATE())
            """, (
                id_usuario,
                metadata['nombre_original'],
                metadata['nombre_almacenado'],
                metadata['ruta_archivo'],
                metadata['ruta_thumbnail'],
                metadata['tipo_mime'],
                metadata['tamano_bytes'],
                metadata['ancho_px'],
                metadata['alto_px'],
                metadata['hash_md5']
            ))
            
            id_archivo = cur.fetchone()[0]
            
            # Actualizar Pedidos_Items con referencia al archivo
            cur.execute("""
                UPDATE Pedidos_Items
                SET archivo_diseno = ?
                WHERE id_pedido IN (
                    SELECT id_pedido FROM Pedidos_detalle_OLD WHERE id_detalle = ?
                )
                AND archivo_diseno IS NULL
            """, (id_archivo, id_detalle))
            
            conn.commit()
            
            print(f"✅ OK (id_archivo: {id_archivo}, {metadata['tamano_bytes']} bytes)")
            migradas += 1
        
        # Resumen
        print()
        print("=" * 60)
        print("📊 RESUMEN DE MIGRACIÓN:")
        print(f"   ✅ Migradas exitosamente: {migradas}")
        print(f"   ❌ Errores: {errores}")
        print(f"   📁 Total archivos: {migradas}")
        print(f"   💾 Ubicación: {UPLOADS_DIR}")
        print()
        
        # Calcular espacio liberado
        print("💡 ESPACIO LIBERADO DE BASE DE DATOS:")
        cur.execute("""
            SELECT 
                COUNT(*) AS imagenes,
                SUM(LEN(imagen)) / 1024 / 1024 AS mb_base64
            FROM Pedidos_detalle_OLD
            WHERE imagen IS NOT NULL AND LEN(imagen) > 0
        """)
        row = cur.fetchone()
        if row:
            print(f"   📉 Base64 en BD: ~{row[1]:.2f} MB")
            print(f"   📁 Archivos en disco: ~{migradas * 0.3:.2f} MB (estimado)")
            print(f"   💰 Ahorro: ~{row[1] - (migradas * 0.3):.2f} MB")
        
        print()
        print("🎯 SIGUIENTE PASO: Ahora puedes eliminar la columna 'imagen'")
        print("   de la tabla Pedidos_detalle_OLD si todo funciona correctamente")
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if conn:
            conn.close()
            print()
            print("🔌 Conexión cerrada")


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == '__main__':
    main()
