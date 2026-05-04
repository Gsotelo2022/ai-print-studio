"""
Router: cupones disponibles para clientes
Ruta: GET /api/cupones/disponibles/{id_cliente}
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone

from db import get_connection
from api.dependencies import json_success, get_current_user

router = APIRouter(prefix="/api", tags=["cupones"])


@router.get("/cupones/disponibles/{id_cliente}")
def obtener_cupones_disponibles_cliente(
    id_cliente: int,
    user: dict = Depends(get_current_user),
):
    """Obtener cupones disponibles para un cliente según su perfil de compras"""
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        # 1. cupones ACTIVOS
        cur.execute("""
            SELECT id_cupon, codigo, descripcion, descuento_porcentaje,
                   fecha_expiracion, usos_actuales, usos_maximos
            FROM cupones
            WHERE activo = true
              AND (fecha_expiracion IS NULL OR fecha_expiracion > NOW())
              AND (usos_maximos IS NULL OR usos_actuales < usos_maximos)
            ORDER BY descuento_porcentaje DESC
        """)
        cupones_db = cur.fetchall()

        if not cupones_db:
            return json_success({
                "cupones": [],
                "total": 0,
                "perfil_cliente": None,
                "mensaje": "No hay cupones disponibles en este momento",
            })

        # 2. PERFIL DEL CLIENTE
        cur.execute("""
            SELECT COUNT(*) as total_pedidos,
                   MAX(fecha_pedido) as ultima_compra,
                   SUM(total) as gasto_total
            FROM pedidos
            WHERE id_usuario = %s AND estado != 'cancelado'
        """, (id_cliente,))

        perfil = cur.fetchone()
        total_pedidos  = perfil[0] if perfil else 0
        ultima_compra  = perfil[1] if perfil else None
        gasto_total    = float(perfil[2]) if perfil and perfil[2] else 0.0

        dias_inactivo = 999
        if ultima_compra:
            # Asegurar que ambos datetime tengan timezone para la resta
            ahora = datetime.now(timezone.utc)
            # Si ultima_compra no tiene timezone, usarlo como naive con UTC
            if ultima_compra.tzinfo is None:
                ultima_compra = ultima_compra.replace(tzinfo=timezone.utc)
            dias_inactivo = (ahora - ultima_compra).days

        # 3. FILTRAR cupones POR PERFIL
        cupones_aplicables = []
        ORDEN = {"primera_compra": 1, "reactivacion": 2, "fidelidad": 3, "alto_valor": 4, "general": 5}

        for cupon in cupones_db:
            id_cupon, codigo, descripcion, descuento, expiracion, usos_actuales, usos_maximos = cupon
            cu = codigo.upper()

            es_aplicable = False
            razon = None
            categoria = "general"

            if any(p in cu for p in ["BIENVENIDA", "PRIMERA", "WELCOME", "NUEVO"]):
                if total_pedidos == 0:
                    es_aplicable, razon, categoria = True, "🎉 ¡Bienvenido! Tu primera compra", "primera_compra"
            elif any(p in cu for p in ["FIDELIDAD", "VIP", "PREMIUM", "FRECUENTE"]):
                if total_pedidos >= 5:
                    es_aplicable, razon, categoria = True, f"⭐ Cliente VIP — {total_pedidos} compras", "fidelidad"
            elif any(p in cu for p in ["REGRESO", "VUELVE", "COMEBACK", "EXTRAÑAMOS"]):
                if total_pedidos > 0 and dias_inactivo > 30:
                    es_aplicable, razon, categoria = True, f"💌 ¡Te extrañamos! ({dias_inactivo} días inactivo)", "reactivacion"
            elif any(p in cu for p in ["ESPECIAL", "EXCLUSIVO", "ELITE"]):
                if gasto_total >= 10000:
                    es_aplicable, razon, categoria = True, f"💎 Cliente especial — ${gasto_total:.0f} en compras", "alto_valor"
            else:
                es_aplicable, categoria = True, "general"

            if es_aplicable:
                usos_restantes = (usos_maximos - (usos_actuales or 0)) if usos_maximos else None
                fecha_exp_str = expiracion.strftime("%Y-%m-%d") if expiracion and hasattr(expiracion, "strftime") else str(expiracion) if expiracion else None

                cupones_aplicables.append({
                    "id_cupon": id_cupon,
                    "codigo": codigo,
                    "descripcion": descripcion,
                    "descuento": int(descuento),
                    "expiracion": fecha_exp_str,
                    "usos_restantes": usos_restantes,
                    "razon": razon,
                    "categoria": categoria,
                    "es_limitado": usos_maximos is not None,
                })

        cupones_aplicables.sort(key=lambda x: (ORDEN.get(x["categoria"], 99), -x["descuento"]))

        return json_success({
            "cupones": cupones_aplicables,
            "total": len(cupones_aplicables),
            "perfil_cliente": {
                "total_pedidos": total_pedidos,
                "dias_inactivo": dias_inactivo if total_pedidos > 0 else None,
                "gasto_total": gasto_total,
                "es_cliente_nuevo": total_pedidos == 0,
                "es_cliente_vip": total_pedidos >= 5,
                "es_cliente_inactivo": dias_inactivo > 30 if total_pedidos > 0 else False,
            },
            "mensaje": f"Se encontraron {len(cupones_aplicables)} cupón(es) disponible(s)" if cupones_aplicables else "No hay cupones para tu perfil",
        })

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en cupones: {e}")
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
