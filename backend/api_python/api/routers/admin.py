"""
Router: administración (pedidos, clientes, productos, dashboard, IA)
Todas las rutas requieren un usuario con tipo == 'admin' (Depends(require_admin)).
Rutas:
  GET  /api/users
  GET  /api/admin/dashboard-stats
  GET  /api/admin/pedidos
  GET  /api/admin/pedidos/{id_pedido}
  PUT  /api/admin/pedidos/{id_pedido}/estado
  PUT  /api/admin/pedidos/{id_pedido}/pago
  GET  /api/admin/clientes
  PUT  /api/admin/clientes/{id_cliente}
  GET  /api/admin/productos
  POST /api/admin/consulta-ia
"""

from datetime import datetime
from typing import Optional

import requests
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel

from db import get_connection
from api.dependencies import json_success, require_admin

router = APIRouter(prefix="/api", tags=["admin"])


# ============================================================
# MODELOS
# ============================================================

class UpdateOrderStatusIn(BaseModel):
    estado: str


class UpdatePaymentStatusIn(BaseModel):
    estado_pago: str
    metodo_pago: Optional[str] = None
    referencia_externa: Optional[str] = None


class UpdateClienteIn(BaseModel):
    nombre: str
    email: str
    telefono: Optional[str] = None
    tipo: str
    cuenta_bloqueada: bool


class ConsultaIA(BaseModel):
    pregunta: str


# ============================================================
# usuarios
# ============================================================

@router.get("/users")
def get_users(user: dict = Depends(require_admin)):
    """Listar todos los usuarios"""
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT id_usuario, nombre, email, tipo
            FROM usuarios ORDER BY nombre
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return json_success([{"id": r[0], "nombre": r[1], "email": r[2], "tipo": r[3]} for r in rows])
    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


# ============================================================
# DASHBOARD
# ============================================================

@router.get("/admin/dashboard-stats")
def admin_get_dashboard_stats(page: int = 1, limit: int = 10, user: dict = Depends(require_admin)):
    """Estadísticas del dashboard de administración"""
    try:
        conn = get_connection()
        cur  = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM usuarios")
        total_usuarios = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM usuarios WHERE fecha_registro >= NOW() - INTERVAL '7 days'")
        usuarios_semana = cur.fetchone()[0]

        cur.execute("SELECT tipo, COUNT(*) FROM usuarios GROUP BY tipo")
        usuarios_por_tipo = [{"tipo_usuario": r[0], "total": r[1]} for r in cur.fetchall()]

        cur.execute("""
            SELECT id_usuario, nombre, '' AS apellido, tipo,
                   EXTRACT(EPOCH FROM (NOW() - fecha_registro))/60
            FROM usuarios ORDER BY fecha_registro DESC
            LIMIT 5
        """)
        actividad = [
            {"id_usuario": r[0], "nombre": r[1], "apellido": r[2],
             "tipo_usuario": r[3], "minutos_desde_registro": r[4]}
            for r in cur.fetchall()
        ]

        offset       = (page - 1) * limit
        total_paginas = (total_usuarios + limit - 1) // limit

        cur.execute("""
            SELECT id_usuario, nombre, email, tipo, fecha_registro
            FROM usuarios ORDER BY id_usuario
            LIMIT %s OFFSET %s
        """, (limit, offset))

        usuarios = []
        for row in cur.fetchall():
            fecha = row[4].isoformat() if row[4] and hasattr(row[4], "isoformat") else str(row[4]) if row[4] else None
            usuarios.append({"id_usuario": row[0], "nombre": row[1], "email": row[2], "tipo_usuario": row[3], "fecha_registro": fecha})

        cur.close()
        conn.close()

        return {
            "success": True,
            "stats": {"total_usuarios": total_usuarios, "usuarios_semana": usuarios_semana, "usuarios_por_tipo": usuarios_por_tipo},
            "usuarios": usuarios,
            "actividad": actividad,
            "paginacion": {"pagina_actual": page, "total_paginas": total_paginas, "total_registros": total_usuarios, "registros_por_pagina": limit},
        }

    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


# ============================================================
# pedidos ADMIN
# ============================================================

@router.get("/admin/pedidos")
def admin_get_pedidos(
    filtro: str = "todos",
    page: int = 1,
    limit: int = 20,
    user: dict = Depends(require_admin),
):
    """Listar pedidos con filtros y paginación"""
    try:
        conn = get_connection()
        cur  = conn.cursor()

        where = ""
        if filtro == "pendientes":
            where = "WHERE p.estado = 'pendiente'"
        elif filtro == "pagados":
            where = "WHERE p.estado_pago = 'aprobado'"
        elif filtro == "no-pagados":
            where = "WHERE p.estado_pago IN ('pendiente', 'rechazado')"
        elif filtro == "entregados":
            where = "WHERE p.estado = 'completado'"

        # Contar total para metadatos de paginación
        cur.execute(f"""
            SELECT COUNT(*)
            FROM pedidos p
            INNER JOIN usuarios u ON p.id_usuario = u.id_usuario
            {where}
        """)
        total_registros = cur.fetchone()[0]
        total_paginas   = max(1, (total_registros + limit - 1) // limit)
        offset          = (page - 1) * limit

        cur.execute(f"""
            SELECT p.id_pedido, p.numero_orden, p.fecha_pedido, p.estado, p.estado_pago,
                   p.total, u.nombre, u.email, u.telefono, p.direccion_envio, p.ciudad
            FROM pedidos p
            INNER JOIN usuarios u ON p.id_usuario = u.id_usuario
            {where}
            ORDER BY p.fecha_pedido DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))

        COLORES = ["#3b82f6","#8b5cf6","#ef4444","#10b981","#f59e0b","#06b6d4","#ec4899"]
        pedidos = []

        for idx, row in enumerate(cur.fetchall()):
            id_pedido = row[0]

            cur.execute("""
                SELECT pi.cantidad, pi.precio_unitario, prod.nombre,
                       MAX(CASE WHEN pa.nombre='Color' THEN pav.valor END),
                       MAX(CASE WHEN pa.nombre='Talle' THEN pav.valor END)
                FROM pedidos_items pi
                INNER JOIN producto_variantes pv ON pi.id_variante = pv.id_variante
                INNER JOIN productos prod ON pv.id_producto = prod.id_producto
                LEFT JOIN variante_atributos va ON pv.id_variante = va.id_variante
                LEFT JOIN producto_atributo_valores pav ON va.id_valor = pav.id_valor
                LEFT JOIN producto_atributos pa ON pav.id_atributo = pa.id_atributo
                WHERE pi.id_pedido = %s
                GROUP BY pi.cantidad, pi.precio_unitario, prod.nombre
            """, (id_pedido,))

            items = [{"cantidad": r[0], "precio_unitario": float(r[1]), "producto_nombre": r[2], "color": r[3] or "-", "talle": r[4] or "-"} for r in cur.fetchall()]
            detalle = items[0] if items else {"producto_nombre": "Sin producto", "color": "-", "talle": "-", "cantidad": 0}
            pn = detalle["producto_nombre"].lower()
            emoji = "👕" if any(x in pn for x in ["remera","camiseta"]) else "🧥" if any(x in pn for x in ["buzo","sudadera"]) else "☕" if "taza" in pn else "🧢" if "gorra" in pn else "👜" if "bolso" in pn else "📦"

            pedidos.append({
                "id": id_pedido,
                "numero": row[1],
                "fecha": {"dia": row[2].strftime("%d/%m/%Y") if row[2] else "-", "hora": row[2].strftime("%H:%M") if row[2] else "-"},
                "estado": {"tipo": row[3], "texto": row[3].title() if row[3] else ""},
                "pago": {"tipo": "pagado" if row[4] == "aprobado" else "no-pagado", "texto": "Pagado" if row[4] == "aprobado" else "Pendiente", "valor": row[4]},
                "total": float(row[5]),
                "cliente": {"nombre": row[6], "email": row[7], "telefono": row[8] or "Sin teléfono",
                             "iniciales": "".join([p[0].upper() for p in row[6].split()[:2]]),
                             "color": COLORES[(offset + idx) % len(COLORES)]},
                "envio": {"direccion": row[9], "ciudad": row[10]},
                "detalle": detalle,
                "producto": {"nombre": detalle["producto_nombre"], "detalles": f"{detalle['color']} • {detalle['talle']} × {detalle.get('cantidad',1)}", "emoji": emoji},
                "items": items,
            })

        cur.close()
        conn.close()
        return json_success(pedidos, extra={
            "paginacion": {
                "pagina_actual":    page,
                "total_paginas":    total_paginas,
                "total_registros":  total_registros,
                "registros_por_pagina": limit,
            }
        })

    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


@router.get("/admin/pedidos/{id_pedido}")
def admin_get_pedido_detalle(id_pedido: int, user: dict = Depends(require_admin)):
    """Detalle completo de un pedido"""
    try:
        conn = get_connection()
        cur  = conn.cursor()

        cur.execute("""
            SELECT p.id_pedido, p.numero_orden, p.fecha_pedido, p.estado, p.estado_pago,
                   p.subtotal, p.descuento, p.gastos_envio, p.total,
                   u.nombre, u.email, u.telefono,
                   p.direccion_envio, p.ciudad, p.provincia, p.codigo_postal,
                   p.telefono_contacto, p.notas_cliente, p.notas_admin
            FROM pedidos p
            INNER JOIN usuarios u ON p.id_usuario = u.id_usuario
            WHERE p.id_pedido = %s
        """, (id_pedido,))

        row = cur.fetchone()
        if not row:
            raise HTTPException(404, {"success": False, "error": "Pedido no encontrado"})

        pedido = {
            "id_pedido": row[0], "numero_orden": row[1],
            "fecha_pedido": row[2].isoformat() if row[2] else None,
            "estado": row[3], "estado_pago": row[4],
            "subtotal": float(row[5]), "descuento": float(row[6]),
            "gastos_envio": float(row[7]), "total": float(row[8]),
            "cliente": {"nombre": row[9], "email": row[10], "telefono": row[11]},
            "envio": {"direccion": row[12], "ciudad": row[13], "provincia": row[14], "codigo_postal": row[15], "telefono_contacto": row[16]},
            "notas": {"cliente": row[17], "admin": row[18]},
        }

        cur.execute("""
            SELECT pi.id_item, pi.cantidad, pi.precio_unitario, pi.subtotal, pi.estado,
                   p.nombre, pv.sku, ad.ruta_thumbnail
            FROM pedidos_items pi
            INNER JOIN producto_variantes pv ON pi.id_variante = pv.id_variante
            INNER JOIN productos p ON pv.id_producto = p.id_producto
            LEFT JOIN archivos_diseno ad ON pi.archivo_diseno = ad.id_archivo
            WHERE pi.id_pedido = %s
        """, (id_pedido,))

        pedido["items"] = [
            {"id_item": r[0], "cantidad": r[1], "precio_unitario": float(r[2]),
             "subtotal": float(r[3]), "estado": r[4], "producto": r[5], "sku": r[6], "thumbnail": r[7]}
            for r in cur.fetchall()
        ]

        cur.close()
        conn.close()
        return json_success(pedido)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


@router.put("/admin/pedidos/{id_pedido}/estado")
def admin_update_pedido_estado(id_pedido: int, payload: UpdateOrderStatusIn, user: dict = Depends(require_admin)):
    """Actualizar estado de un pedido"""
    try:
        conn = get_connection()
        cur  = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM pedidos WHERE id_pedido = %s", (id_pedido,))
        if cur.fetchone()[0] == 0:
            raise HTTPException(404, {"success": False, "error": "Pedido no encontrado"})

        cur.execute("UPDATE pedidos SET estado = %s WHERE id_pedido = %s", (payload.estado, id_pedido))
        conn.commit()
        cur.close()
        conn.close()

        return json_success({"id_pedido": id_pedido, "estado": payload.estado})

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


@router.put("/admin/pedidos/{id_pedido}/pago")
def admin_update_pedido_pago(id_pedido: int, payload: UpdatePaymentStatusIn, user: dict = Depends(require_admin)):
    """Actualizar estado de pago y registrar en tabla pagos"""
    try:
        conn = get_connection()
        cur  = conn.cursor()

        cur.execute("""
            UPDATE pedidos
            SET estado_pago = %s,
                fecha_pago = CASE WHEN %s = 'aprobado' THEN NOW() ELSE fecha_pago END
            WHERE id_pedido = %s
        """, (payload.estado_pago, payload.estado_pago, id_pedido))

        if payload.estado_pago in ("aprobado", "rechazado"):
            cur.execute("SELECT total FROM pedidos WHERE id_pedido = %s", (id_pedido,))
            total = cur.fetchone()[0]
            cur.execute("""
                INSERT INTO pagos (id_pedido, metodo_pago, referencia_externa, monto, estado, fecha_aprobacion)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                id_pedido, payload.metodo_pago or "manual",
                payload.referencia_externa, total, payload.estado_pago,
                datetime.now() if payload.estado_pago == "aprobado" else None,
            ))

        conn.commit()
        cur.close()
        conn.close()

        return json_success({"id_pedido": id_pedido, "estado_pago": payload.estado_pago})

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


# ============================================================
# CLIENTES ADMIN
# ============================================================

@router.get("/admin/clientes")
def admin_get_clientes(
    page: int = 1,
    limit: int = 20,
    buscar: str = "",
    user: dict = Depends(require_admin),
):
    """Listado de clientes con estadísticas de compra y paginación"""
    try:
        conn = get_connection()
        cur  = conn.cursor()

        like = f"%{buscar}%" if buscar else "%"
        buscar_where = "AND (u.nombre ILIKE %s OR u.email ILIKE %s)" if buscar else ""

        # Total para paginación
        if buscar:
            cur.execute(f"""
                SELECT COUNT(*) FROM usuarios u
                WHERE u.tipo = 'cliente' {buscar_where}
            """, (like, like))
        else:
            cur.execute("SELECT COUNT(*) FROM usuarios u WHERE u.tipo = 'cliente'")

        total_registros = cur.fetchone()[0]
        total_paginas   = max(1, (total_registros + limit - 1) // limit)
        offset          = (page - 1) * limit

        params_base = (like, like, limit, offset) if buscar else (limit, offset)
        cur.execute(f"""
            SELECT u.id_usuario, u.nombre, u.email, u.telefono, u.fecha_registro,
                   u.tipo, u.cuenta_bloqueada,
                   COUNT(p.id_pedido),
                   COALESCE(SUM(CASE WHEN p.estado_pago='aprobado' THEN p.total ELSE 0 END), 0)
            FROM usuarios u
            LEFT JOIN pedidos p ON u.id_usuario = p.id_usuario
            WHERE u.tipo = 'cliente' {buscar_where}
            GROUP BY u.id_usuario, u.nombre, u.email, u.telefono, u.fecha_registro, u.tipo, u.cuenta_bloqueada
            ORDER BY 9 DESC
            LIMIT %s OFFSET %s
        """, params_base)

        COLORES = ["#3B82F6","#10B981","#F59E0B","#EF4444","#8B5CF6","#EC4899"]
        clientes = []
        for idx, row in enumerate(cur.fetchall()):
            iniciales = "".join([p[0].upper() for p in row[1].strip().split()[:2]])
            clientes.append({
                "id": row[0], "nombre": row[1], "email": row[2], "telefono": row[3],
                "fechaRegistro": row[4].isoformat() if row[4] else None,
                "tipo": row[5], "cuenta_bloqueada": bool(row[6]),
                "pedidos": row[7], "totalGastado": float(row[8]),
                "iniciales": iniciales, "color": COLORES[(offset + idx) % len(COLORES)],
            })

        cur.close()
        conn.close()
        return json_success(clientes, extra={
            "paginacion": {
                "pagina_actual":    page,
                "total_paginas":    total_paginas,
                "total_registros":  total_registros,
                "registros_por_pagina": limit,
            }
        })

    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


@router.put("/admin/clientes/{id_cliente}")
def admin_update_cliente(id_cliente: int, payload: UpdateClienteIn, user: dict = Depends(require_admin)):
    """Actualizar datos de un cliente"""
    try:
        conn = get_connection()
        cur  = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM usuarios WHERE id_usuario = %s", (id_cliente,))
        if cur.fetchone()[0] == 0:
            raise HTTPException(404, {"success": False, "error": "Cliente no encontrado"})

        cur.execute("SELECT id_usuario FROM usuarios WHERE email = %s AND id_usuario != %s", (payload.email, id_cliente))
        if cur.fetchone():
            raise HTTPException(409, {"success": False, "error": "El email ya está en uso"})

        cur.execute("""
            UPDATE usuarios
            SET nombre = %s, email = %s, telefono = %s, tipo = %s, cuenta_bloqueada = %s
            WHERE id_usuario = %s
        """, (payload.nombre, payload.email, payload.telefono, payload.tipo, payload.cuenta_bloqueada, id_cliente))

        conn.commit()
        cur.close()
        conn.close()

        return json_success({"id_cliente": id_cliente, "message": "Cliente actualizado correctamente"})

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


# ============================================================
# PRODUCTOS ADMIN
# ============================================================

@router.get("/admin/productos")
def admin_get_productos(user: dict = Depends(require_admin)):
    """Listado de productos activos"""
    try:
        conn = get_connection()
        cur  = conn.cursor()

        cur.execute("""
            SELECT id_producto, nombre, descripcion, categoria, imagen_mockup,
                   area_impresion_ancho, area_impresion_alto
            FROM productos WHERE activo = true
            ORDER BY orden_visualizacion, nombre
        """)

        productos = [
            {"id_producto": r[0], "nombre": r[1], "descripcion": r[2], "categoria": r[3],
             "imagen_mockup": r[4], "area_impresion": {"ancho": r[5], "alto": r[6]}}
            for r in cur.fetchall()
        ]

        cur.close()
        conn.close()
        return json_success(productos)

    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


# ============================================================
# CONSULTA IA (Ollama)
# ============================================================

@router.post("/admin/consulta-ia")
def consulta_ia(payload: ConsultaIA, user: dict = Depends(require_admin)):
    """Consultar al agente Ollama con contexto real de la BD"""
    try:
        conn   = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total_usuarios = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE fecha_registro >= NOW() - INTERVAL '7 days'")
        usuarios_semana = cursor.fetchone()[0]

        cursor.execute("SELECT tipo, COUNT(*) FROM usuarios GROUP BY tipo")
        resumen_tipos = ", ".join([f"{r[0]}: {r[1]}" for r in cursor.fetchall()])

        cursor.close()
        conn.close()

        contexto = f"""
        Total de usuarios: {total_usuarios}
        usuarios nuevos esta semana: {usuarios_semana}
        usuarios por tipo: {resumen_tipos}
        """

        prompt = f"""Sos un asistente de administración de un sistema de ventas de ropa personalizada.

Datos actuales del sistema:
{contexto}

Respondé de forma clara y breve.

Pregunta:
{payload.pregunta}"""

        response = requests.post("http://localhost:11434/api/generate", json={
            "model":  "qwen2.5:1.5b",
            "prompt": prompt,
            "stream": False,
        })

        data = response.json()
        return json_success({"respuesta": data["response"]})

    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


# ============================================================
# CUPONES (admin)
# ============================================================

from pydantic import BaseModel as _BaseModel
from typing import Optional as _Optional

class CuponIn(_BaseModel):
    codigo: str
    descripcion: _Optional[str] = None
    descuento_porcentaje: float
    fecha_expiracion: _Optional[str] = None
    usos_maximos: _Optional[int] = None
    activo: bool = True

class CuponUpdateIn(_BaseModel):
    codigo: _Optional[str] = None
    descripcion: _Optional[str] = None
    descuento_porcentaje: _Optional[float] = None
    fecha_expiracion: _Optional[str] = None
    usos_maximos: _Optional[int] = None
    activo: _Optional[bool] = None


@router.get("/admin/cupones")
def admin_get_cupones(
    incluir_inactivos: bool = False,
    user: dict = Depends(require_admin),
):
    """Listar todos los cupones (admin)"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        where = "" if incluir_inactivos else "WHERE activo = true"
        cur.execute(f"""
            SELECT id_cupon, codigo, descripcion, descuento_porcentaje,
                   fecha_expiracion, usos_actuales, usos_maximos, activo
            FROM cupones
            {where}
            ORDER BY id_cupon DESC
        """)
        cupones = []
        for r in cur.fetchall():
            id_c, codigo, desc, descuento, exp, usos_act, usos_max, activo = r
            exp_str = exp.strftime("%Y-%m-%d") if exp and hasattr(exp, "strftime") else str(exp) if exp else None
            cupones.append({
                "id_cupon": id_c,
                "codigo": codigo,
                "descripcion": desc,
                "descuento_porcentaje": float(descuento),
                "fecha_expiracion": exp_str,
                "usos_actuales": usos_act or 0,
                "usos_maximos": usos_max,
                "activo": activo,
            })
        cur.close()
        conn.close()
        return json_success(cupones)
    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


@router.post("/admin/cupones")
def admin_crear_cupon(payload: CuponIn, user: dict = Depends(require_admin)):
    """Crear un cupón nuevo"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO cupones (codigo, descripcion, descuento_porcentaje,
                                 fecha_expiracion, usos_maximos, activo)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_cupon
        """, (
            payload.codigo.upper(),
            payload.descripcion,
            payload.descuento_porcentaje,
            payload.fecha_expiracion or None,
            payload.usos_maximos,
            payload.activo,
        ))
        id_cupon = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return json_success({"id_cupon": id_cupon, "mensaje": "Cupón creado"})
    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


@router.put("/admin/cupones/{id_cupon}")
def admin_actualizar_cupon(
    id_cupon: int,
    payload: CuponUpdateIn,
    user: dict = Depends(require_admin),
):
    """Actualizar un cupón existente"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        fields = []
        vals = []
        if payload.codigo is not None:
            fields.append("codigo = %s"); vals.append(payload.codigo.upper())
        if payload.descripcion is not None:
            fields.append("descripcion = %s"); vals.append(payload.descripcion)
        if payload.descuento_porcentaje is not None:
            fields.append("descuento_porcentaje = %s"); vals.append(payload.descuento_porcentaje)
        if payload.fecha_expiracion is not None:
            fields.append("fecha_expiracion = %s"); vals.append(payload.fecha_expiracion or None)
        if payload.usos_maximos is not None:
            fields.append("usos_maximos = %s"); vals.append(payload.usos_maximos)
        if payload.activo is not None:
            fields.append("activo = %s"); vals.append(payload.activo)
        if not fields:
            raise HTTPException(400, {"success": False, "error": "Nada para actualizar"})
        vals.append(id_cupon)
        cur.execute(f"UPDATE cupones SET {', '.join(fields)} WHERE id_cupon = %s", vals)
        conn.commit()
        cur.close()
        conn.close()
        return json_success({"mensaje": "Cupón actualizado"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


@router.delete("/admin/cupones/{id_cupon}")
def admin_eliminar_cupon(id_cupon: int, user: dict = Depends(require_admin)):
    """Eliminar un cupón"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM cupones WHERE id_cupon = %s", (id_cupon,))
        conn.commit()
        cur.close()
        conn.close()
        return json_success({"mensaje": "Cupón eliminado"})
    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


@router.post("/admin/cupones/proponer")
def admin_proponer_cupones(user: dict = Depends(require_admin)):
    """Generar propuestas de cupones analizando datos reales de clientes"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Métricas clave para generar propuestas
        cur.execute("""
            SELECT
              COUNT(*) FILTER (WHERE fecha_registro >= NOW() - INTERVAL '30 days') AS nuevos,
              COUNT(*) FILTER (WHERE fecha_registro <  NOW() - INTERVAL '30 days') AS recurrentes
            FROM usuarios WHERE tipo = 'cliente'
        """)
        rc = cur.fetchone()
        clientes_nuevos     = rc[0] or 0
        clientes_recurrentes = rc[1] or 0

        cur.execute("""
            SELECT COUNT(DISTINCT id_usuario)
            FROM pedidos
            WHERE fecha_pedido < NOW() - INTERVAL '30 days'
              AND id_usuario NOT IN (
                SELECT DISTINCT id_usuario FROM pedidos
                WHERE fecha_pedido >= NOW() - INTERVAL '30 days'
              )
        """)
        clientes_inactivos = cur.fetchone()[0] or 0

        cur.execute("""
            SELECT COUNT(*) FROM (
                SELECT id_usuario
                FROM pedidos
                WHERE estado != 'cancelado'
                GROUP BY id_usuario
                HAVING COUNT(*) >= 5
            ) vip
        """)
        clientes_vip = cur.fetchone()[0] or 0

        cur.execute("""
            SELECT AVG(total)::numeric(10,2) FROM pedidos
            WHERE fecha_pedido >= NOW() - INTERVAL '30 days' AND estado != 'cancelado'
        """)
        ticket_promedio = float(cur.fetchone()[0] or 0)

        cur.close()
        conn.close()

        # Generar propuestas según el análisis
        propuestas = []
        analisis_partes = []

        if clientes_nuevos > 0:
            propuestas.append({
                "codigo": "BIENVENIDA20",
                "descripcion": "20% de descuento en tu primera compra",
                "descuento": 20,
                "duracion_dias": 30,
                "razon": f"Hay {clientes_nuevos} cliente(s) nuevo(s) este mes",
            })
            analisis_partes.append(f"{clientes_nuevos} clientes nuevos detectados → cupón de bienvenida recomendado")

        if clientes_inactivos > 0:
            propuestas.append({
                "codigo": "VUELVE15",
                "descripcion": "15% de descuento — ¡Te extrañamos!",
                "descuento": 15,
                "duracion_dias": 14,
                "razon": f"{clientes_inactivos} cliente(s) inactivos más de 30 días",
            })
            analisis_partes.append(f"{clientes_inactivos} clientes inactivos → cupón de reactivación recomendado")

        if clientes_vip > 0:
            propuestas.append({
                "codigo": "VIP10",
                "descripcion": "10% exclusivo para clientes frecuentes",
                "descuento": 10,
                "duracion_dias": 60,
                "razon": f"{clientes_vip} cliente(s) con 5+ pedidos",
            })
            analisis_partes.append(f"{clientes_vip} clientes VIP → cupón de fidelidad recomendado")

        if ticket_promedio > 0 and not propuestas:
            propuestas.append({
                "codigo": "DESCUENTO10",
                "descripcion": "10% de descuento general",
                "descuento": 10,
                "duracion_dias": 30,
                "razon": f"Ticket promedio ${ticket_promedio:.0f} — descuento general para incentivar ventas",
            })
            analisis_partes.append("Sin segmentos especiales detectados → descuento general recomendado")

        analisis = (
            "Análisis de clientes:\n" + "\n".join(f"• {p}" for p in analisis_partes)
            if analisis_partes else "No hay datos suficientes para generar un análisis detallado."
        )

        return json_success({
            "propuesta": {
                "cupones": propuestas,
                "analisis": analisis,
            },
            "estadisticas": {
                "clientes_nuevos": clientes_nuevos,
                "clientes_recurrentes": clientes_recurrentes,
                "clientes_inactivos": clientes_inactivos,
                "clientes_vip": clientes_vip,
                "ticket_promedio": ticket_promedio,
            },
        })

    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


# ============================================================
# PRODUCTOS ADMIN — POST / PUT / DELETE
# ============================================================

from pydantic import BaseModel as _BM2
from typing import Optional as _Opt2

class ProductoCreateIn(_BM2):
    nombre: str
    descripcion: _Opt2[str] = None
    categoria: _Opt2[str] = None
    imagen_mockup: _Opt2[str] = None
    area_impresion_ancho: _Opt2[float] = None
    area_impresion_alto: _Opt2[float] = None
    orden_visualizacion: _Opt2[int] = 0

class ProductoUpdateIn(_BM2):
    nombre: _Opt2[str] = None
    descripcion: _Opt2[str] = None
    categoria: _Opt2[str] = None
    imagen_mockup: _Opt2[str] = None
    activo: _Opt2[bool] = None

class ProductoPrecioUpdateIn(_BM2):
    precio: float


@router.post("/admin/productos")
async def admin_crear_producto(
    nombre: str = Form(...),
    descripcion: str = Form(""),
    categoria: str = Form(""),
    orden_visualizacion: int = Form(0),
    imagen: _Opt2[UploadFile] = File(None),
    user: dict = Depends(require_admin),
):
    """Crear un nuevo producto (acepta multipart/form-data con imagen opcional)"""
    import os, shutil, uuid as _uuid
    try:
        imagen_mockup = None

        if imagen and imagen.filename:
            ext = os.path.splitext(imagen.filename)[1].lower()
            filename = f"mockup_{_uuid.uuid4().hex}{ext}"
            save_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "api", "imagenes-generadas-con-IA")
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, filename)
            with open(save_path, "wb") as f:
                shutil.copyfileobj(imagen.file, f)
            imagen_mockup = f"/imagenes/{filename}"

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO productos (nombre, descripcion, categoria, imagen_mockup,
                                   activo, orden_visualizacion)
            VALUES (%s, %s, %s, %s, true, %s)
            RETURNING id_producto
        """, (nombre, descripcion or None, categoria or None, imagen_mockup, orden_visualizacion))
        id_producto = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return json_success({"id_producto": id_producto, "nombre": nombre,
                             "mensaje": "Producto creado correctamente"})
    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


@router.put("/admin/productos/{id_producto}")
def admin_actualizar_producto(id_producto: int, payload: ProductoUpdateIn,
                              user: dict = Depends(require_admin)):
    """Actualizar campos de un producto"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        fields, vals = [], []
        if payload.nombre       is not None: fields.append("nombre = %s");       vals.append(payload.nombre)
        if payload.descripcion  is not None: fields.append("descripcion = %s");  vals.append(payload.descripcion)
        if payload.categoria    is not None: fields.append("categoria = %s");    vals.append(payload.categoria)
        if payload.imagen_mockup is not None: fields.append("imagen_mockup = %s"); vals.append(payload.imagen_mockup)
        if payload.activo       is not None: fields.append("activo = %s");       vals.append(payload.activo)
        if not fields:
            raise HTTPException(400, {"success": False, "error": "Nada para actualizar"})
        vals.append(id_producto)
        cur.execute(f"UPDATE productos SET {', '.join(fields)} WHERE id_producto = %s", vals)
        if cur.rowcount == 0:
            raise HTTPException(404, {"success": False, "error": "Producto no encontrado"})
        conn.commit()
        cur.close()
        conn.close()
        return json_success({"mensaje": "Producto actualizado"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


@router.put("/admin/productos/{id_producto}/precio")
def admin_actualizar_precio_producto(id_producto: int, payload: ProductoPrecioUpdateIn,
                                     user: dict = Depends(require_admin)):
    """Actualizar precio de todas las variantes activas de un producto"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE producto_variantes SET precio = %s
            WHERE id_producto = %s AND activo = true
        """, (payload.precio, id_producto))
        filas = cur.rowcount
        if filas == 0:
            raise HTTPException(404, {"success": False,
                                      "error": "No se encontraron variantes activas para ese producto"})
        conn.commit()
        cur.close()
        conn.close()
        return json_success({"variantes_actualizadas": filas, "nuevo_precio": payload.precio})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


@router.delete("/admin/productos/{id_producto}")
def admin_eliminar_producto(id_producto: int, user: dict = Depends(require_admin)):
    """Desactivar un producto (baja lógica) y sus variantes"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT nombre, activo FROM productos WHERE id_producto = %s", (id_producto,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, {"success": False, "error": "Producto no encontrado"})
        if not row[1]:
            raise HTTPException(400, {"success": False, "error": "El producto ya está desactivado"})
        cur.execute("UPDATE producto_variantes SET activo = false WHERE id_producto = %s", (id_producto,))
        cur.execute("UPDATE productos SET activo = false WHERE id_producto = %s", (id_producto,))
        conn.commit()
        cur.close()
        conn.close()
        return json_success({"mensaje": f"Producto '{row[0]}' desactivado correctamente"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


# ============================================================
# ESTADÍSTICAS (alias de dashboard-stats sin paginación)
# ============================================================

@router.get("/admin/estadisticas")
def admin_get_estadisticas(user: dict = Depends(require_admin)):
    """Resumen estadístico para el dashboard de cupones"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Último mes
        cur.execute("""
            SELECT COUNT(*) AS total_pedidos,
                   AVG(total)::numeric(10,2) AS ticket_promedio,
                   SUM(total)::numeric(10,2) AS ingresos
            FROM pedidos
            WHERE fecha_pedido >= NOW() - INTERVAL '30 days'
              AND estado != 'cancelado'
        """)
        r = cur.fetchone()
        ultimo_mes = {
            "total_pedidos": r[0] or 0,
            "ticket_promedio": float(r[1]) if r[1] else 0.0,
            "ingresos": float(r[2]) if r[2] else 0.0,
        }

        # Clientes
        cur.execute("""
            SELECT
              COUNT(*) FILTER (WHERE fecha_registro >= NOW() - INTERVAL '30 days') AS nuevos,
              COUNT(*) FILTER (WHERE fecha_registro <  NOW() - INTERVAL '30 days') AS recurrentes
            FROM usuarios
            WHERE tipo = 'cliente'
        """)
        rc = cur.fetchone()
        clientes = {"nuevos": rc[0] or 0, "recurrentes": rc[1] or 0}

        cur.close()
        conn.close()
        return json_success({"ultimo_mes": ultimo_mes, "clientes": clientes})

    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})
