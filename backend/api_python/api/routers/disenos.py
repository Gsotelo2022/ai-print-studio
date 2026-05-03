"""
Router: diseños e imágenes
Rutas:
  POST /api/upload-design      → autenticado
  GET  /api/mis-disenos/{id}   → autenticado
  POST /api/generate-image     → autenticado
  POST /api/remove-background  → autenticado
  GET  /uploads/{folder}/{filename}  → público (servir archivos)
"""

import os
import base64
import hashlib
import io
from datetime import datetime

from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from fastapi.responses import FileResponse
from PIL import Image

from db import get_connection
from api.dependencies import (
    json_success, get_current_user,
    UPLOADS_DIR, THUMBNAILS_DIR, IMAGENES_IA_DIR,
)

router = APIRouter(tags=["disenos"])


# ============================================================
# SUBIR DISEÑO
# ============================================================

@router.post("/api/upload-design")
async def upload_design(
    file: UploadFile,
    user_id: int,
    user: dict = Depends(get_current_user),
):
    """Subir un archivo de diseño personalizado"""
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(400, {"success": False, "error": "Solo se permiten imágenes"})

        contents = await file.read()
        img       = Image.open(io.BytesIO(contents))
        ancho, alto = img.size
        hash_md5  = hashlib.md5(contents).hexdigest()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext       = file.filename.split(".")[-1] if "." in file.filename else "png"
        nombre_alm = f"user{user_id}_{timestamp}_{hash_md5[:8]}.{ext}"

        (UPLOADS_DIR / nombre_alm).write_bytes(contents)

        thumb_nombre = f"thumb_{nombre_alm}"
        img_thumb    = img.copy()
        img_thumb.thumbnail((200, 200), Image.Resampling.LANCZOS)
        img_thumb.save(THUMBNAILS_DIR / thumb_nombre)

        ruta     = f"uploads/designs/{nombre_alm}"
        ruta_tmb = f"uploads/thumbnails/{thumb_nombre}"

        conn = get_connection()
        cur  = conn.cursor()

        cur.execute("""
            INSERT INTO archivos_diseno (
                id_usuario, nombre_original, nombre_almacenado, ruta_archivo,
                ruta_thumbnail, tipo_mime, tamano_bytes, ancho_px, alto_px, hash_md5
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_archivo
        """, (
            user_id, file.filename, nombre_alm, ruta,
            ruta_tmb, file.content_type, len(contents), ancho, alto, hash_md5,
        ))

        id_archivo = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return json_success({
            "id_archivo": id_archivo,
            "nombre":    nombre_alm,
            "ruta":      ruta,
            "thumbnail": ruta_tmb,
            "ancho":     ancho,
            "alto":      alto,
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


# ============================================================
# MIS DISEÑOS
# ============================================================

@router.get("/api/mis-disenos/{id_usuario}")
def get_mis_disenos(id_usuario: int, user: dict = Depends(get_current_user)):
    """Obtener archivos de diseño del usuario autenticado"""
    try:
        conn = get_connection()
        cur  = conn.cursor()

        cur.execute("""
            SELECT ad.id_archivo, ad.nombre_original, ad.nombre_almacenado,
                   ad.ruta_archivo, ad.ruta_thumbnail, ad.tipo_mime, ad.tamano_bytes,
                   ad.ancho_px, ad.alto_px, ad.es_generado_ia, ad.fecha_subida,
                   COUNT(DISTINCT pi.id_pedido) as veces_usado,
                   MAX(p.fecha_pedido) as ultimo_uso
            FROM archivos_diseno ad
            LEFT JOIN pedidos_items pi ON ad.id_archivo = pi.archivo_diseno
            LEFT JOIN pedidos p ON pi.id_pedido = p.id_pedido
            WHERE ad.id_usuario = %s
            GROUP BY ad.id_archivo, ad.nombre_original, ad.nombre_almacenado,
                     ad.ruta_archivo, ad.ruta_thumbnail, ad.tipo_mime, ad.tamano_bytes,
                     ad.ancho_px, ad.alto_px, ad.es_generado_ia, ad.fecha_subida
            ORDER BY ad.fecha_subida DESC
        """, (id_usuario,))

        disenos = []
        for row in cur.fetchall():
            id_archivo, nombre_orig, nombre_alm, ruta, thumbnail, mime, \
            tamano, ancho, alto, es_ia, fecha, veces, ultimo = row

            prompt = None
            if es_ia:
                cur.execute("SELECT prompt_usado FROM archivos_diseno WHERE id_archivo = %s", (id_archivo,))
                pr = cur.fetchone()
                if pr:
                    prompt = pr[0]

            disenos.append({
                "id_archivo":       id_archivo,
                "nombre_original":  nombre_orig,
                "nombre_almacenado":nombre_alm,
                "ruta_archivo":     ruta,
                "ruta_thumbnail":   thumbnail,
                "tipo_mime":        mime,
                "tamano_bytes":     tamano,
                "tamano_kb":        round(tamano / 1024, 2) if tamano else 0,
                "dimensiones":      f"{ancho}x{alto}" if ancho and alto else "N/A",
                "ancho_px":         ancho,
                "alto_px":          alto,
                "es_generado_ia":   bool(es_ia),
                "prompt_usado":     prompt if es_ia else None,
                "fecha_subida":     fecha.strftime("%Y-%m-%d %H:%M:%S") if fecha else None,
                "estadisticas": {
                    "veces_usado": veces or 0,
                    "ultimo_uso":  ultimo.strftime("%Y-%m-%d %H:%M:%S") if ultimo else None,
                },
            })

        cur.close()
        conn.close()

        return json_success({
            "disenos":            disenos,
            "total":              len(disenos),
            "total_generados_ia": sum(1 for d in disenos if d["es_generado_ia"]),
            "total_subidos":      sum(1 for d in disenos if not d["es_generado_ia"]),
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


# ============================================================
# GENERAR IMAGEN CON IA
# ============================================================

@router.post("/api/generate-image")
async def generate_image(payload: dict, user: dict = Depends(get_current_user)):
    """Generar imagen delegando al servidor Node (Replicate/Flux)"""
    import httpx

    prompt = payload.get("prompt", "").strip()
    if not prompt:
        raise HTTPException(400, {"success": False, "error": "El prompt es requerido"})

    # URL del servidor Node — siempre local, puerto fijo
    node_url = "http://127.0.0.1:3000"

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{node_url}/generar-imagen",
                json={"prompt": prompt},
            )

        if resp.status_code != 200:
            body = resp.json() if resp.content else {}
            raise HTTPException(
                502,
                {"success": False, "error": body.get("error", f"Error del servidor de imágenes: HTTP {resp.status_code}")}
            )

        data = resp.json()
        imagen_url = data.get("imagen")

        if not imagen_url:
            raise HTTPException(500, {"success": False, "error": "El servidor de imágenes no devolvió una URL"})

        return json_success({"imagen_url": imagen_url, "prompt": prompt})

    except HTTPException:
        raise
    except httpx.ConnectError:
        raise HTTPException(
            503,
            {"success": False, "error": "No se pudo conectar al servidor de imágenes. ¿Está corriendo el servidor Node en el puerto 3000?"}
        )
    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


# ============================================================
# REMOVER FONDO
# ============================================================

@router.post("/api/remove-background")
async def remove_background(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    """Remover el fondo de una imagen usando rembg (local, sin API externa)"""
    try:
        contents    = await file.read()
        input_image = Image.open(io.BytesIO(contents))

        from rembg import remove as rembg_remove

        output_image = rembg_remove(input_image)

        buf = io.BytesIO()
        output_image.save(buf, format="PNG")
        buf.seek(0)

        img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        return json_success({
            "imagen_url": f"data:image/png;base64,{img_base64}",
            "message":    "Fondo removido exitosamente",
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(500, {"success": False, "error": f"Error al remover fondo: {str(e)}"})


# ============================================================
# SERVIR ARCHIVOS DE UPLOAD (estático)
# ============================================================

@router.get("/uploads/{folder}/{filename}")
def serve_upload(folder: str, filename: str):
    """Servir archivos de diseño desde disco"""
    if folder == "designs":
        file_path = UPLOADS_DIR / filename
    elif folder == "thumbnails":
        file_path = THUMBNAILS_DIR / filename
    else:
        raise HTTPException(404, {"success": False, "error": "Carpeta no válida"})

    if not file_path.exists():
        raise HTTPException(404, {"success": False, "error": "Archivo no encontrado"})

    return FileResponse(file_path)
