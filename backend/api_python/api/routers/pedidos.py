"""
Router: pedidos (crear, pagar, historial del cliente)
Rutas:
  POST /api/create-order       → autenticado
  GET  /api/mis-pedidos/{id}   → autenticado
  POST /api/create-payment     → autenticado
  POST /api/save-payment       → público (back_url MercadoPago)
"""

import os
import base64
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends

from db import get_connection
from api.dependencies import json_success, get_current_user, UPLOADS_DIR, THUMBNAILS_DIR
from PIL import Image
import io
import hashlib

router = APIRouter(prefix="/api", tags=["pedidos"])


# ============================================================
# CREAR PEDIDO
# ============================================================

@router.post("/create-order")
def create_order(payload: dict, user: dict = Depends(get_current_user)):
    """Crear pedido con uno o más ítems. Requiere autenticación."""
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id es obligatorio")

        cur.execute("SELECT COUNT(*) FROM usuarios WHERE id_usuario = %s", (user_id,))
        if cur.fetchone()[0] == 0:
            raise HTTPException(status_code=404, detail="Usuario no existe")

        items = payload.get("items")
        if not items:
            raise HTTPException(status_code=400, detail="items es obligatorio")

        total = 0
        items_data = []

        for item in items:
            id_variante = item.get("id_variante")
            cantidad    = item.get("cantidad", 1)

            if not id_variante:
                raise HTTPException(status_code=400, detail="id_variante faltante")

            cur.execute("""
                SELECT pv.precio, pv.stock_actual, p.nombre
                FROM producto_variantes pv
                INNER JOIN productos p ON pv.id_producto = p.id_producto
                WHERE pv.id_variante = %s AND pv.activo = true
            """, (id_variante,))

            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=400, detail="Variante no existe")

            precio, stock, _ = row
            if stock < cantidad:
                raise HTTPException(status_code=400, detail="Stock insuficiente")

            subtotal = float(precio) * cantidad
            total   += subtotal

            items_data.append({
                "id_variante":    id_variante,
                "cantidad":       cantidad,
                "precio_unitario":float(precio),
                "subtotal":       subtotal,
                "archivo_diseno": item.get("archivo_diseno"),
                "posicion_x":     item.get("posicion_x", 0),
                "posicion_y":     item.get("posicion_y", 0),
                "zoom":           item.get("zoom", 1),
            })

        # ── CUPÓN ──────────────────────────────────────────────
        codigo_cupon      = payload.get("codigo_cupon")
        id_cupon_usado    = None
        monto_descuento   = 0
        subtotal_original = total

        if codigo_cupon:
            cur.execute("""
                SELECT id_cupon, descuento_porcentaje, usos_maximos, usos_actuales,
                       fecha_expiracion, activo
                FROM cupones WHERE codigo = %s AND activo = true
            """, (codigo_cupon,))

            cupon = cur.fetchone()
            if not cupon:
                raise HTTPException(status_code=400, detail=f"Cupón '{codigo_cupon}' no válido o inactivo")

            id_cupon, porcentaje, usos_max, usos_actual, fecha_exp, _ = cupon

            if fecha_exp and datetime.now().date() > fecha_exp:
                raise HTTPException(status_code=400, detail=f"Cupón '{codigo_cupon}' expirado")
            if usos_max and usos_actual >= usos_max:
                raise HTTPException(status_code=400, detail=f"Cupón '{codigo_cupon}' alcanzó el límite de usos")

            id_cupon_usado  = id_cupon
            monto_descuento = (float(total) * float(porcentaje)) / 100
            total           = float(total) - monto_descuento

            cur.execute("UPDATE cupones SET usos_actuales = usos_actuales + 1 WHERE id_cupon = %s", (id_cupon,))

        # ── GUARDAR ARCHIVOS DE DISEÑO ─────────────────────────
        for item in items_data:
            archivo_data = item.get("archivo_diseno")

            if archivo_data and isinstance(archivo_data, str) and archivo_data.startswith("data:image"):
                try:
                    _, encoded = archivo_data.split(",", 1)
                    image_bytes = base64.b64decode(encoded)

                    img = Image.open(io.BytesIO(image_bytes))
                    ancho, alto = img.size
                    hash_md5    = hashlib.md5(image_bytes).hexdigest()
                    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
                    nombre_alm  = f"user{user_id}_{timestamp}_{hash_md5[:8]}.png"

                    (UPLOADS_DIR / nombre_alm).write_bytes(image_bytes)

                    thumb_nombre = f"thumb_{nombre_alm}"
                    img_thumb    = img.copy()
                    img_thumb.thumbnail((200, 200), Image.Resampling.LANCZOS)
                    img_thumb.save(THUMBNAILS_DIR / thumb_nombre)

                    ruta      = f"uploads/designs/{nombre_alm}"
                    ruta_tmb  = f"uploads/thumbnails/{thumb_nombre}"
                    prompt    = payload.get("prompt") or payload.get("notas_cliente") or "Diseño personalizado"
                    es_ia     = 0 if prompt.lower() == "imagen subida por usuario" else 1

                    cur.execute("""
                        INSERT INTO archivos_diseno (
                            id_usuario, nombre_original, nombre_almacenado, ruta_archivo,
                            ruta_thumbnail, tipo_mime, tamano_bytes, ancho_px, alto_px,
                            hash_md5, es_generado_ia, prompt_usado, fecha_subida
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                        RETURNING id_archivo
                    """, (
                        user_id, "diseno_generado.png", nombre_alm, ruta, ruta_tmb,
                        "image/png", len(image_bytes), ancho, alto,
                        hash_md5, es_ia, prompt,
                    ))
                    item["id_archivo"] = cur.fetchone()[0]
                except Exception as e:
                    print(f"❌ Error guardando diseño: {e}")
                    item["id_archivo"] = None
            elif isinstance(archivo_data, int):
                item["id_archivo"] = archivo_data
            else:
                item["id_archivo"] = None

        # ── INSERTAR PEDIDO ────────────────────────────────────
        cur.execute("SELECT COALESCE(MAX(id_pedido), 0) FROM pedidos")
        last_id      = cur.fetchone()[0]
        numero_orden = f"ORD-{datetime.now().year}-{str(last_id + 1).zfill(5)}"

        cur.execute("""
            INSERT INTO pedidos (
                numero_orden, id_usuario, subtotal, descuento, total,
                direccion_envio, ciudad, telefono_contacto, notas_cliente
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_pedido
        """, (
            numero_orden, user_id, subtotal_original, monto_descuento, total,
            payload.get("direccion_envio"), payload.get("ciudad"),
            payload.get("telefono_contacto"), payload.get("notas_cliente"),
        ))

        id_pedido = cur.fetchone()[0]

        for item in items_data:
            cur.execute("""
                INSERT INTO pedidos_items (
                    id_pedido, id_variante, cantidad, precio_unitario,
                    archivo_diseno, diseno_posicion_x, diseno_posicion_y, diseno_zoom,
                    tiene_diseno
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                id_pedido, item["id_variante"], item["cantidad"], item["precio_unitario"],
                item["id_archivo"], item["posicion_x"], item["posicion_y"], item["zoom"],
                True if item["id_archivo"] else False,
            ))

        conn.commit()

        return json_success({
            "order_id":    id_pedido,
            "numero_orden":numero_orden,
            "total":       total,
            "items_count": len(items_data),
        })

    except HTTPException as e:
        if conn:
            conn.rollback()
        raise e
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# ============================================================
# MIS PEDIDOS (historial del cliente)
# ============================================================

@router.get("/mis-pedidos/{id_usuario}")
def get_mis_pedidos(id_usuario: int, user: dict = Depends(get_current_user)):
    """Historial de pedidos del usuario autenticado"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        if cur.fetchone()[0] == 0:
            raise HTTPException(status_code=404, detail={"success": False, "error": "Usuario no encontrado"})

        cur.execute("""
            SELECT p.id_pedido, p.numero_orden, p.fecha_pedido,
                   p.estado, p.estado_pago, p.total, p.direccion_envio, p.ciudad
            FROM pedidos p
            WHERE p.id_usuario = %s
            ORDER BY p.fecha_pedido DESC
        """, (id_usuario,))
        filas_pedidos = cur.fetchall()

        pedidos = []
        for fila in filas_pedidos:
            id_pedido = fila[0]

            cur.execute("""
                SELECT pi.cantidad, pi.precio_unitario,
                       prod.nombre AS nombre_producto,
                       MAX(CASE WHEN pa.nombre='Color' THEN pav.valor END) AS color,
                       MAX(CASE WHEN pa.nombre='Talle' THEN pav.valor END) AS talle,
                       ad.ruta_thumbnail
                FROM pedidos_items pi
                INNER JOIN producto_variantes pv ON pi.id_variante = pv.id_variante
                INNER JOIN productos prod ON pv.id_producto = prod.id_producto
                LEFT JOIN variante_atributos va ON pv.id_variante = va.id_variante
                LEFT JOIN producto_atributo_valores pav ON va.id_valor = pav.id_valor
                LEFT JOIN producto_atributos pa ON pav.id_atributo = pa.id_atributo
                LEFT JOIN archivos_diseno ad ON pi.archivo_diseno = ad.id_archivo
                WHERE pi.id_pedido = %s
                GROUP BY pi.cantidad, pi.precio_unitario, prod.nombre, ad.ruta_thumbnail
            """, (id_pedido,))

            items = []
            for item in cur.fetchall():
                items.append({
                    "cantidad":         item[0],
                    "precio_unitario":  float(item[1]),
                    "nombre_producto":  item[2],
                    "variante_info":    f"{item[3] or '-'} / {item[4] or '-'}",
                    "ruta_thumbnail":   item[5] or None,
                })

            pedidos.append({
                "id_pedido":    id_pedido,
                "numero_orden": fila[1],
                "fecha_pedido": fila[2].isoformat() if fila[2] else None,
                "estado":       fila[3],
                "estado_pago":  fila[4],
                "total":        float(fila[5]) if fila[5] else 0.0,
                "envio":        {"direccion": fila[6], "ciudad": fila[7]},
                "items":        items,
            })

        cur.close()
        conn.close()
        return json_success(pedidos)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en get_mis_pedidos: {e}")
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})


# ============================================================
# PAGO MERCADOPAGO
# ============================================================

@router.post("/create-payment")
def create_payment(payload: dict, user: dict = Depends(get_current_user)):
    """Crear preferencia de pago en MercadoPago. Requiere MERCADOPAGO_ACCESS_TOKEN en .env"""
    try:
        import mercadopago

        access_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "")
        if not access_token:
            raise HTTPException(status_code=500, detail={"success": False, "error": "MERCADOPAGO_ACCESS_TOKEN no configurado"})

        sdk = mercadopago.SDK(access_token)

        preference_data = {
            "items": [{
                "title":      payload.get("producto", "Producto AI Print Studio"),
                "quantity":   int(payload.get("cantidad", 1)),
                "unit_price": float(payload.get("precio", 1000)),
                "currency_id":"ARS",
            }],
            "payer": {"email": payload.get("email", "cliente@aiprint.com")},
            "back_urls": {
                "success": os.getenv("MP_URL_SUCCESS", "http://localhost:5173/success"),
                "failure": os.getenv("MP_URL_FAILURE", "http://localhost:5173/failure"),
                "pending": os.getenv("MP_URL_PENDING", "http://localhost:5173/pending"),
            },
            "external_reference": str(payload.get("order_id", "")),
        }

        pref_response = sdk.preference().create(preference_data)
        pref          = pref_response.get("response", {})

        if pref_response.get("status") not in (200, 201):
            raise HTTPException(status_code=502, detail={"success": False, "error": "Error al crear preferencia en MercadoPago"})

        return json_success({
            "init_point":    pref.get("init_point"),
            "sandbox_url":   pref.get("sandbox_init_point"),
            "payment_url":   pref.get("init_point"),
            "preference_id": pref.get("id"),
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})


@router.post("/save-payment")
def save_payment(payload: dict):
    """Registrar notificación de pago de MercadoPago (back_url — público)"""
    try:
        payment_id = payload.get("payment_id")
        status     = payload.get("status")

        if payment_id and status == "approved":
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                UPDATE pedidos
                SET estado_pago = 'pagado', referencia_externa = %s
                WHERE referencia_externa = %s OR referencia_externa IS NULL
            """, (str(payment_id), str(payment_id)))
            conn.commit()
            cur.close()
            conn.close()

        return json_success({"message": "Notificación de pago recibida"})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})
