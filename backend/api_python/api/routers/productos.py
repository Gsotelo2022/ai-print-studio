"""
Router: productos y variantes
Rutas: GET /api/productos, GET /api/variante/{id_variante}
"""

from fastapi import APIRouter, HTTPException

from db import get_connection
from api.dependencies import json_success

router = APIRouter(prefix="/api", tags=["productos"])


@router.get("/productos")
def get_productos():
    """Obtener catálogo de productos con sus variantes y atributos"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id_producto, nombre, descripcion, categoria, imagen_mockup,
                   area_impresion_ancho, area_impresion_alto
            FROM Productos
            WHERE activo = TRUE
            ORDER BY orden_visualizacion, nombre
        """)

        productos = []
        for row in cur.fetchall():
            id_prod, nombre, desc, categ, img, ancho, alto = row

            cur.execute("""
                SELECT pv.id_variante, pv.sku, pv.precio, pv.stock_actual
                FROM Producto_Variantes pv
                WHERE pv.id_producto = %s AND pv.activo = TRUE
                ORDER BY pv.precio
            """, (id_prod,))

            variantes = []
            for vrow in cur.fetchall():
                id_var, sku, precio, stock = vrow

                cur.execute("""
                    SELECT pa.nombre, pav.valor
                    FROM Variante_Atributos va
                    INNER JOIN Producto_Atributo_Valores pav ON va.id_valor = pav.id_valor
                    INNER JOIN Producto_Atributos pa ON pav.id_atributo = pa.id_atributo
                    WHERE va.id_variante = %s
                """, (id_var,))

                atributos = {}
                for arow in cur.fetchall():
                    attr_nombre, attr_valor = arow
                    atributos[attr_nombre.lower()] = {"valor": attr_valor, "codigo_color": None}

                variantes.append({
                    "id_variante": id_var,
                    "sku": sku,
                    "precio": float(precio),
                    "stock": stock,
                    "atributos": atributos,
                })

            # Producto_Atributos_Asignados no existe en esquema PostgreSQL
            opciones_atributos = []

            productos.append({
                "id_producto": id_prod,
                "nombre": nombre,
                "descripcion": desc,
                "categoria": categ,
                "imagen_mockup": img,
                "area_impresion": {"ancho": ancho, "alto": alto},
                "opciones_atributos": opciones_atributos,
                "variantes": variantes,
                "precio_desde": min([v["precio"] for v in variantes]) if variantes else 0,
            })

        cur.close()
        conn.close()
        return json_success(productos)

    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})


@router.get("/variante/{id_variante}")
def get_variante_detalle(id_variante: int):
    """Obtener detalles de una variante específica"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT pv.id_variante, pv.sku, pv.precio, pv.stock_actual,
                   p.nombre AS producto_nombre, p.descripcion, p.imagen_mockup
            FROM Producto_Variantes pv
            INNER JOIN Productos p ON pv.id_producto = p.id_producto
            WHERE pv.id_variante = %s AND pv.activo = TRUE
        """, (id_variante,))

        row = cur.fetchone()
        if not row:
            raise HTTPException(404, {"success": False, "error": "Variante no encontrada"})

        id_var, sku, precio, stock, prod_nombre, desc, img = row

        cur.execute("""
            SELECT pa.nombre, pav.valor
            FROM Variante_Atributos va
            INNER JOIN Producto_Atributo_Valores pav ON va.id_valor = pav.id_valor
            INNER JOIN Producto_Atributos pa ON pav.id_atributo = pa.id_atributo
            WHERE va.id_variante = %s
        """, (id_var,))

        atributos = {}
        for arow in cur.fetchall():
            attr_nombre, attr_valor = arow
            atributos[attr_nombre.lower()] = {"valor": attr_valor, "codigo_color": None}

        cur.close()
        conn.close()

        return json_success({
            "id_variante": id_var,
            "sku": sku,
            "precio": float(precio),
            "stock": stock,
            "producto_nombre": prod_nombre,
            "descripcion": desc,
            "imagen_mockup": img,
            "atributos": atributos,
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})
