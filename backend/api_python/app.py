raise RuntimeError(
    "app.py está DEPRECADO (era la versión SQL Server con '?'). "
    "Usar: uvicorn app_v2:app --host 0.0.0.0 --port 8000 --reload"
)
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from db import get_connection
import hashlib
import secrets
import base64
import io
from PIL import Image

app = FastAPI()

# CORS: permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejador personalizado de excepciones HTTP
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Maneja las excepciones HTTP de manera personalizada"""
    # Si el detail es un dict, devolverlo como está
    if isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )
    # Si es un string, envolver en un dict
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": str(exc.detail)}
    )


class RegisterIn(BaseModel):
    """Esquema para registro de usuario"""
    fullname: str
    email: str
    phone: str | None = None
    password: str


class LoginIn(BaseModel):
    """Esquema para login de usuario"""
    email: str
    password: str


class PaymentIn(BaseModel):
    """Esquema para crear pago en Mercado Pago"""
    producto: str
    precio: float
    cantidad: int


class CreateOrderIn(BaseModel):
    """Esquema para crear un pedido"""
    user_id: int  # ID del usuario autenticado
    id_variante: Optional[int] = None  # ID de la variante del producto (opcional)
    # Alternativa: buscar variante por atributos
    producto: Optional[str] = None  # nombre del producto (ej: "Remera", "Taza")
    talle: Optional[str] = None
    color: Optional[str] = None
    # Campos comunes
    cantidad: int
    prompt: str
    imagen_url: str  # URL o base64 de la imagen del diseño
    posicion_x: int = 0
    posicion_y: int = 0
    zoom: float = 1.0


def hash_password(pw: str) -> str:
    """Hashear contraseña con PBKDF2 (SHA256)"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', pw.encode(), bytes.fromhex(salt), 100000)
    return f"{salt}${hash_obj.hex()}"


def verify_password(plain: str, hashed: str) -> bool:
    """Verificar contraseña hasheada"""
    try:
        salt, hash_hex = hashed.split('$')
        hash_obj = hashlib.pbkdf2_hmac('sha256', plain.encode(), bytes.fromhex(salt), 100000)
        return hash_obj.hex() == hash_hex
    except:
        return False


def json_success(data):
    """Formato de respuesta exitosa"""
    return {"success": True, "data": data}


@app.get('/api/health')
def health():
    """Health check para verificar que el servidor está vivo"""
    return {"success": True}


@app.post('/api/register')
def register(payload: RegisterIn):
    """Registrar un nuevo usuario"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Verificar si el email ya existe
        cur.execute("SELECT COUNT(*) FROM Usuarios WHERE Email = ?", (payload.email,))
        row = cur.fetchone()
        cnt = int(row[0]) if row else 0
        if cnt > 0:
            cur.close()
            conn.close()
            raise HTTPException(
                status_code=409,
                detail={"success": False, "error": "El email ya está registrado"}
            )

        # Hashear la contraseña
        hashed = hash_password(payload.password)

        # Insertar nuevo usuario en la BD
        # Columnas: Nombre, Email, telefono, password_user, Tipo
        cur.execute(
            "INSERT INTO Usuarios (Nombre, Email, telefono, password_user, Tipo) VALUES (?, ?, ?, ?, ?)",
            (payload.fullname, payload.email, payload.phone, hashed, "cliente")
        )
        conn.commit()

        # Obtener el ID del usuario recién creado
        cur.execute("SELECT id_usuario FROM Usuarios WHERE Email = ?", (payload.email,))
        id_row = cur.fetchone()
        user_id = int(id_row[0]) if id_row else None

        cur.close()
        conn.close()

        return json_success({
            "id_usuario": user_id,
            "Nombre": payload.fullname,
            "Email": payload.email
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": str(e)}
        )


@app.post('/api/login')
def login(payload: LoginIn):
    """Autenticar un usuario existente"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Buscar usuario por email
        cur.execute(
            "SELECT id_usuario, Nombre, Email, password_user, Tipo FROM Usuarios WHERE Email = ?",
            (payload.email,)
        )
        row = cur.fetchone()

        cur.close()
        conn.close()

        if not row:
            raise HTTPException(
                status_code=401,
                detail={"success": False, "error": "Credenciales inválidas"}
            )

        # Verificar contraseña (index 3 es la columna contraseña)
        stored_hash = row[3]
        if not verify_password(payload.password, stored_hash):
            raise HTTPException(
                status_code=401,
                detail={"success": False, "error": "Credenciales inválidas"}
            )

        # Retornar datos del usuario autenticado
        user = {
            "id_usuario": row[0],
            "Nombre": row[1],
            "Email": row[2],
            "Tipo": row[4]
        }
        return json_success(user)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": str(e)}
        )


@app.get('/api/productos')
def get_productos():
    """Obtener catálogo de productos con sus variantes y atributos"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Consultar productos con sus variantes y atributos
        query = """
        SELECT 
            pv.id_variante,
            pv.SKU,
            p.nombre AS producto,
            p.descripcion,
            pv.precio,
            pv.stock_actual,
            pa.nombre AS nombre_atributo,
            pav.valor
        FROM Producto_Variantes pv
        INNER JOIN Productos p ON pv.id_producto = p.id_producto
        LEFT JOIN Variante_Atributos va ON pv.id_variante = va.id_variante
        LEFT JOIN Producto_Atributo_Valores pav ON va.id_valor = pav.id_valor
        LEFT JOIN Producto_Atributos pa ON pav.id_atributo = pa.id_atributo
        WHERE pv.activo = 1 AND p.activo = 1
        ORDER BY p.nombre, pv.SKU
        """
        
        cur.execute(query)
        rows = cur.fetchall()
        
        cur.close()
        conn.close()

        # Agrupar variantes por id_variante
        variantes_dict = {}
        for row in rows:
            id_variante = row[0]
            if id_variante not in variantes_dict:
                variantes_dict[id_variante] = {
                    'id_variante': row[0],
                    'SKU': row[1],
                    'producto': row[2],
                    'descripcion': row[3] if row[3] else '',
                    'precio': float(row[4]),
                    'stock_actual': int(row[5]),
                    'atributos': {}
                }
            
            # Agregar atributo si existe
            if row[6] and row[7]:
                variantes_dict[id_variante]['atributos'][row[6]] = row[7]

        # Convertir a lista
        variantes = list(variantes_dict.values())

        return json_success({'productos': variantes})

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": str(e)}
        )


@app.post('/api/create-order')
def create_order(payload: CreateOrderIn):
    """Crear un nuevo pedido usando la nueva estructura: Pedidos + Pedidos_Items"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # 1. Validar que el usuario existe
        cur.execute("SELECT COUNT(*) FROM Usuarios WHERE id_usuario = ?", (payload.user_id,))
        row = cur.fetchone()
        if not row or int(row[0]) == 0:
            cur.close()
            conn.close()
            raise HTTPException(
                status_code=404,
                detail={"success": False, "error": f"Usuario {payload.user_id} no existe"}
            )

        # 2. Buscar la variante del producto
        # Si no se proporciona id_variante, buscar por producto/talle/color
        id_variante = payload.id_variante
        
        if not id_variante and payload.producto:
            # Buscar variante por atributos (producto + talle + color)
            query = """
                SELECT TOP 1 pv.id_variante
                FROM Producto_Variantes pv
                INNER JOIN Productos p ON pv.id_producto = p.id_producto
                LEFT JOIN Variante_Atributos va_talle ON pv.id_variante = va_talle.id_variante
                LEFT JOIN Producto_Atributos pa_talle ON va_talle.id_atributo = pa_talle.id_atributo AND pa_talle.nombre = 'Talle'
                LEFT JOIN Producto_Atributo_Valores pav_talle ON va_talle.id_valor = pav_talle.id_valor
                LEFT JOIN Variante_Atributos va_color ON pv.id_variante = va_color.id_variante
                LEFT JOIN Producto_Atributos pa_color ON va_color.id_atributo = pa_color.id_atributo AND pa_color.nombre = 'Color'
                LEFT JOIN Producto_Atributo_Valores pav_color ON va_color.id_valor = pav_color.id_valor
                WHERE p.nombre = ? 
                  AND pv.activo = 1 AND p.activo = 1
                  AND (pav_color.valor = ? OR ? IS NULL)
                  AND (pav_talle.valor = ? OR ? IS NULL)
            """
            cur.execute(query, (payload.producto, payload.color, payload.color, payload.talle, payload.talle))
            variante_row = cur.fetchone()
            if not variante_row:
                cur.close()
                conn.close()
                raise HTTPException(
                    status_code=404,
                    detail={"success": False, "error": f"No se encontró variante para {payload.producto} (Talle: {payload.talle}, Color: {payload.color})"}
                )
            id_variante = variante_row[0]
        
        if not id_variante:
            cur.close()
            conn.close()
            raise HTTPException(
                status_code=400,
                detail={"success": False, "error": "Debe proporcionar id_variante o producto/talle/color"}
            )
        
        # Ahora obtener los detalles de la variante
        cur.execute("""
            SELECT pv.id_variante, pv.SKU, pv.precio, pv.stock_actual, p.nombre
            FROM Producto_Variantes pv
            INNER JOIN Productos p ON pv.id_producto = p.id_producto
            WHERE pv.id_variante = ? AND pv.activo = 1 AND p.activo = 1
        """, (id_variante,))
        
        variante_row = cur.fetchone()
        if not variante_row:
            cur.close()
            conn.close()
            raise HTTPException(
                status_code=404,
                detail={"success": False, "error": f"Variante {payload.id_variante} no encontrada"}
            )

        id_variante, sku, precio_unitario, stock_actual, nombre_producto = variante_row
        precio_unitario = float(precio_unitario)
        stock_actual = int(stock_actual)

        # 3. Validar stock disponible
        if stock_actual < payload.cantidad:
            cur.close()
            conn.close()
            raise HTTPException(
                status_code=400,
                detail={"success": False, "error": f"Stock insuficiente. Disponible: {stock_actual}, Solicitado: {payload.cantidad}"}
            )

        # 4. Generar número de orden único
        from datetime import datetime
        fecha_str = datetime.now().strftime('%Y%m%d')
        cur.execute("""
            SELECT COUNT(*) FROM Pedidos 
            WHERE numero_orden LIKE ?
        """, (f"ORD-{fecha_str}-%",))
        count_row = cur.fetchone()
        count = int(count_row[0]) if count_row else 0
        numero_orden = f"ORD-{fecha_str}-{count + 1:04d}"

        # 5. Calcular total
        subtotal = precio_unitario * payload.cantidad
        total = subtotal  # Por ahora sin impuestos ni envío

        # 6. Insertar en tabla Pedidos
        cur.execute("""
            INSERT INTO Pedidos (numero_orden, id_usuario, total, estado, estado_pago)
            OUTPUT INSERTED.id_pedido
            VALUES (?, ?, ?, ?, ?)
        """, (numero_orden, payload.user_id, total, 'pendiente', 'pendiente'))
        
        pedido_row = cur.fetchone()
        id_pedido = pedido_row[0] if pedido_row else None

        if not id_pedido:
            cur.close()
            conn.close()
            raise Exception('No se pudo obtener el ID del pedido')

        # 7. Insertar en tabla Pedidos_Items
        # Nota: Si hay prompt e imagen, se debería guardar primero en Archivos_Diseno
        # Por ahora, dejamos archivo_diseno = NULL y guardamos las coordenadas del diseño
        cur.execute("""
            INSERT INTO Pedidos_Items (
                id_pedido, id_variante, cantidad, precio_unitario, descuento_unitario,
                tiene_diseno, archivo_diseno, diseno_posicion_x, diseno_posicion_y, 
                diseno_zoom, estado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_pedido,
            id_variante,
            payload.cantidad,
            precio_unitario,
            0.0,  # descuento_unitario
            1 if payload.imagen_url else 0,  # tiene_diseno
            None,  # archivo_diseno (NULL por ahora, TODO: implementar Archivos_Diseno)
            payload.posicion_x,
            payload.posicion_y,
            payload.zoom,
            'pendiente'  # estado
        ))

        # 8. Opcional: Guardar imagen en Archivos_Diseno (por ahora guardamos solo la URL en detalle)
        # TODO: Implementar guardado de archivo real en filesystem + entrada en tabla Archivos_Diseno

        # 9. Actualizar stock de la variante (descontar)
        nuevo_stock = stock_actual - payload.cantidad
        cur.execute("""
            UPDATE Producto_Variantes
            SET stock_actual = ?
            WHERE id_variante = ?
        """, (nuevo_stock, id_variante))

        conn.commit()
        cur.close()
        conn.close()

        return json_success({
            'id_pedido': id_pedido,
            'numero_orden': numero_orden,
            'producto': nombre_producto,
            'sku': sku,
            'precio_unitario': precio_unitario,
            'cantidad': payload.cantidad,
            'subtotal': subtotal,
            'total': total,
            'stock_restante': nuevo_stock
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": str(e)}
        )


@app.post('/api/create-payment')
def create_payment(payload: PaymentIn):
    """Crear una preferencia de pago en Mercado Pago"""
    try:
        import mercadopago
        
        print(f'[create-payment] Iniciando con datos: producto={payload.producto}, precio={payload.precio}, cantidad={payload.cantidad}')
        
        # Configurar el SDK de Mercado Pago
        sdk = mercadopago.SDK("TEST-1492177583757030-032120-4e536f078e8cf2e2f51b871b89dea0c7-193328483")
        print('[create-payment] SDK configurado')
        
        # Crear la preferencia
        preference_data = {
            "items": [
                {
                    "title": payload.producto,
                    "quantity": payload.cantidad,
                    "unit_price": payload.precio,
                    "currency_id": "ARS"
                }
            ],
            "payer": {
                "email": "test_user_123456@testuser.com"
            },
            "back_urls": {
                "success": "http://127.0.0.1:5173/success",
                "failure": "http://127.0.0.1:5173/failure",
                "pending": "http://127.0.0.1:5173/pending"
            }
        }
        
        print(f'[create-payment] Enviando preferencia a Mercado Pago...')
        preference_response = sdk.preference().create(preference_data)
        print(f'[create-payment] Respuesta completa: {preference_response}')
        
        preference = preference_response.get("response", {})
        print(f'[create-payment] Preference extraida: {preference}')
        
        init_point = preference.get("init_point")
        print(f'[create-payment] Init point: {init_point}')
        
        if not init_point:
            print('[create-payment] ⚠ init_point está vacío o None')
            return json_success({
                "init_point": None,
                "debug": {
                    "full_response": preference_response,
                    "preference": preference
                }
            })
        
        return json_success({
            "init_point": init_point
        })
    
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f'[create-payment] ERROR: {error_msg}')
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": f"Error al crear pago: {str(e)}"}
        )


@app.post('/api/remove-background')
async def remove_background(file: UploadFile = File(...)):
    """Remover el fondo de una imagen usando rembg"""
    try:
        print(f'[remove-background] Recibido archivo: {file.filename}, tamaño aprox: {file.size}')
        
        # Leer el archivo de imagen
        contents = await file.read()
        print(f'[remove-background] Archivo leído, bytes: {len(contents)}')
        
        # Abrir la imagen con PIL
        input_image = Image.open(io.BytesIO(contents))
        print(f'[remove-background] Imagen abierta, tamaño: {input_image.size}')
        
        # Importar rembg aquí para evitar cargar el modelo si no se usa
        print('[remove-background] Importando rembg...')
        from rembg import remove
        
        # Remover el fondo
        print('[remove-background] Iniciando remoción de fondo (esto puede tomar tiempo)...')
        output_image = remove(input_image)
        print('[remove-background] Fondo removido exitosamente')
        
        # Convertir la imagen a bytes
        img_byte_arr = io.BytesIO()
        output_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # Convertir a base64
        print('[remove-background] Convirtiendo a base64...')
        img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        print(f'[remove-background] Base64 listo, tamaño: {len(img_base64)} caracteres')
        
        result = json_success({
            "imagen_url": f"data:image/png;base64,{img_base64}",
            "message": "Fondo removido exitosamente"
        })
        print('[remove-background] Respondiendo al cliente...')
        return result
    
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f'[remove-background] ERROR: {error_msg}')
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": f"Error al remover fondo: {str(e)}"}
        )


@app.get('/api/admin/pedidos')
def get_all_orders():
    """Obtener todos los pedidos con detalles para el panel de administración"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Query con JOINs para obtener toda la información necesaria (nueva estructura)
        query = """
            SELECT 
                p.id_pedido,
                p.fecha_pedido,
                p.estado as pedido_estado,
                u.id_usuario,
                u.Nombre,
                u.Email,
                u.telefono,
                pi.id_item,
                'Pedido personalizado' as detalle,
                prod.nombre as producto_nombre,
                '' as Color,
                '' as talle,
                pi.estado as detalle_estado,
                p.estado_pago as pago,
                p.total,
                p.fecha_pedido as fecha_detalle
            FROM Pedidos p
            INNER JOIN Usuarios u ON p.id_usuario = u.id_usuario
            INNER JOIN Pedidos_Items pi ON p.id_pedido = pi.id_pedido
            INNER JOIN Producto_Variantes pv ON pi.id_variante = pv.id_variante
            INNER JOIN Productos prod ON pv.id_producto = prod.id_producto
            ORDER BY p.fecha_pedido DESC
        """
        
        cur.execute(query)
        rows = cur.fetchall()

        pedidos = []
        for row in rows:
            pedido = {
                "id": row[0],
                "numero": f"#{str(row[0]).zfill(5)}",  # Formato #00001
                "fecha": {
                    "dia": row[1].strftime("%d/%m/%Y") if row[1] else "",
                    "hora": row[1].strftime("%H:%M") + " hs" if row[1] else ""
                },
                "pedido_estado": row[2],
                "cliente": {
                    "id": row[3],
                    "nombre": row[4],
                    "email": row[5],
                    "telefono": row[6] or "Sin teléfono",
                    "iniciales": "".join([n[0].upper() for n in row[4].split()[:2]]) if row[4] else "XX"
                },
                "detalle": {
                    "id": row[7],
                    "descripcion": row[8] or "",
                    "producto_nombre": row[9] or "Producto",
                    "color": row[10] or "",
                    "talle": row[11] or "",
                },
                "estado": {
                    "tipo": row[12] or "pendiente",
                    "texto": (row[12] or "pendiente").capitalize()
                },
                "pago": {
                    "tipo": "pagado" if row[13] == "aprobado" else "no-pagado",
                    "texto": "Pagado" if row[13] == "aprobado" else "No pagado"
                },
                "total": float(row[14]) if row[14] else 0.0
            }
            pedidos.append(pedido)

        cur.close()
        conn.close()

        return json_success(pedidos)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": f"Error al obtener pedidos: {str(e)}"}
        )


@app.put('/api/admin/pedidos/{id_detalle}/estado')
def update_order_status(id_detalle: int, body: dict):
    """Actualizar el estado de un pedido"""
    try:
        nuevo_estado = body.get('estado')
        if not nuevo_estado:
            raise HTTPException(
                status_code=400,
                detail={"success": False, "error": "El estado es requerido"}
            )

        conn = get_connection()
        cur = conn.cursor()

        # Actualizar el estado en Pedidos_Items
        query = """
            UPDATE Pedidos_Items 
            SET estado = ? 
            WHERE id_item = ?
        """
        cur.execute(query, (nuevo_estado, id_detalle))
        conn.commit()

        # Verificar que se actualizó
        if cur.rowcount == 0:
            cur.close()
            conn.close()
            raise HTTPException(
                status_code=404,
                detail={"success": False, "error": "Pedido no encontrado"}
            )

        cur.close()
        conn.close()

        return json_success({"message": "Estado actualizado correctamente", "estado": nuevo_estado})

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": f"Error al actualizar estado: {str(e)}"}
        )


@app.put('/api/admin/pedidos/{id_detalle}/pago')
def update_order_payment(id_detalle: int, body: dict):
    """Actualizar el estado de pago de un pedido"""
    try:
        nuevo_pago = body.get('pago')
        if not nuevo_pago:
            raise HTTPException(
                status_code=400,
                detail={"success": False, "error": "El estado de pago es requerido"}
            )

        conn = get_connection()
        cur = conn.cursor()

        # Actualizar el estado de pago en Pedidos (ahora a nivel de pedido, no item)
        query = """
            UPDATE Pedidos 
            SET estado_pago = ? 
            WHERE id_pedido = (SELECT id_pedido FROM Pedidos_Items WHERE id_item = ?)
        """
        cur.execute(query, (nuevo_pago, id_detalle))
        conn.commit()

        # Verificar que se actualizó
        if cur.rowcount == 0:
            cur.close()
            conn.close()
            raise HTTPException(
                status_code=404,
                detail={"success": False, "error": "Pedido no encontrado"}
            )

        cur.close()
        conn.close()

        return json_success({"message": "Estado de pago actualizado correctamente", "pago": nuevo_pago})

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": f"Error al actualizar pago: {str(e)}"}
        )


# ============================================================
# ENDPOINTS ADMIN - PRODUCTOS
# ============================================================

class ProductoUpdateIn(BaseModel):
    """Esquema para actualizar producto"""
    Detalle: str
    Color: str
    talle: str
    precio: float


class ProductoPrecioUpdateIn(BaseModel):
    """Esquema para actualizar precio de todas las variantes de un producto"""
    precio: float
    nuevo_detalle: Optional[str] = None  # Opcional: cambiar nombre del detalle


@app.put('/api/admin/productos/{id_producto}/precio')
def update_precio_producto(id_producto: int, body: ProductoPrecioUpdateIn):
    """Actualizar precio de todas las variantes de un producto"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Actualizar precio en todas las variantes del producto
        query = """
            UPDATE Producto_Variantes 
            SET precio = ?
            WHERE id_producto = ? AND activo = 1
        """
        cur.execute(query, (body.precio, id_producto))
        conn.commit()
        
        filas_actualizadas = cur.rowcount

        # Verificar que se actualizó al menos una fila
        if filas_actualizadas == 0:
            cur.close()
            conn.close()
            raise HTTPException(
                status_code=404,
                detail={"success": False, "error": f"No se encontraron variantes activas para el producto {id_producto}"}
            )

        cur.close()
        conn.close()

        return json_success({
            "message": f"Precio actualizado para {filas_actualizadas} variante(s)",
            "variantes_actualizadas": filas_actualizadas,
            "nuevo_precio": body.precio
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": f"Error al actualizar precio: {str(e)}"}
        )


@app.put('/api/admin/productos/{id_producto}')
def update_producto(id_producto: int, body: ProductoUpdateIn):
    """Actualizar un producto existente"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Actualizar producto
        query = """
            UPDATE Productos 
            SET Detalle = ?, Color = ?, talle = ?, precio = ? 
            WHERE id_producto = ?
        """
        cur.execute(query, (body.Detalle, body.Color, body.talle, body.precio, id_producto))
        conn.commit()

        # Verificar que se actualizó
        if cur.rowcount == 0:
            cur.close()
            conn.close()
            raise HTTPException(
                status_code=404,
                detail={"success": False, "error": "Producto no encontrado"}
            )

        cur.close()
        conn.close()

        return json_success({
            "message": "Producto actualizado correctamente",
            "id_producto": id_producto
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": f"Error al actualizar producto: {str(e)}"}
        )


@app.put('/api/admin/productos/detalle/{detalle}/precio')
def update_precio_por_detalle(detalle: str, body: ProductoPrecioUpdateIn):
    """Actualizar precio de TODAS las variantes (talles/colores) de un producto"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Si se proporciona nuevo_detalle, actualizar también el nombre
        if body.nuevo_detalle and body.nuevo_detalle != detalle:
            query = """
                UPDATE Productos 
                SET precio = ?, Detalle = ?
                WHERE Detalle = ?
            """
            cur.execute(query, (body.precio, body.nuevo_detalle, detalle))
        else:
            # Solo actualizar precio
            query = """
                UPDATE Productos 
                SET precio = ?
                WHERE Detalle = ?
            """
            cur.execute(query, (body.precio, detalle))
        
        conn.commit()
        filas_actualizadas = cur.rowcount

        # Verificar que se actualizó al menos una fila
        if filas_actualizadas == 0:
            cur.close()
            conn.close()
            raise HTTPException(
                status_code=404,
                detail={"success": False, "error": f"No se encontraron productos con detalle '{detalle}'"}
            )

        cur.close()
        conn.close()

        return json_success({
            "message": f"Precio actualizado para {filas_actualizadas} variante(s) del producto",
            "detalle": body.nuevo_detalle if body.nuevo_detalle else detalle,
            "variantes_actualizadas": filas_actualizadas,
            "nuevo_precio": body.precio
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": f"Error al actualizar precio: {str(e)}"}
        )


@app.delete('/api/admin/productos/{id_producto}')
def delete_producto(id_producto: int):
    """Desactivar un producto (eliminación lógica) y todas sus variantes"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Verificar si el producto existe
        check_query = "SELECT nombre, activo FROM Productos WHERE id_producto = ?"
        cur.execute(check_query, (id_producto,))
        producto = cur.fetchone()
        
        if not producto:
            cur.close()
            conn.close()
            raise HTTPException(
                status_code=404,
                detail={"success": False, "error": "Producto no encontrado"}
            )
        
        nombre_producto = producto[0]
        ya_inactivo = not producto[1]
        
        if ya_inactivo:
            cur.close()
            conn.close()
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False, 
                    "error": "El producto ya está desactivado"
                }
            )

        # Desactivar todas las variantes del producto
        query_variantes = """
            UPDATE Producto_Variantes 
            SET activo = 0 
            WHERE id_producto = ?
        """
        cur.execute(query_variantes, (id_producto,))
        variantes_desactivadas = cur.rowcount

        # Desactivar el producto base
        query_producto = """
            UPDATE Productos 
            SET activo = 0,
                fecha_modificacion = GETDATE()
            WHERE id_producto = ?
        """
        cur.execute(query_producto, (id_producto,))
        conn.commit()

        cur.close()
        conn.close()

        return json_success({
            "message": f"Producto '{nombre_producto}' desactivado correctamente",
            "id_producto": id_producto,
            "variantes_desactivadas": variantes_desactivadas,
            "tipo": "soft_delete"
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": f"Error al eliminar producto: {str(e)}"}
        )


class ProductoCreateIn(BaseModel):
    """Esquema para crear producto nuevo"""
    nombre: str
    descripcion: Optional[str] = None
    categoria: Optional[str] = None
    imagen_mockup: Optional[str] = None
    area_impresion_ancho: Optional[int] = 800
    area_impresion_alto: Optional[int] = 1000
    orden_visualizacion: Optional[int] = 0


@app.get('/api/admin/productos/siguiente-orden')
def get_siguiente_orden():
    """Obtener el siguiente número de orden disponible"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = "SELECT ISNULL(MAX(orden_visualizacion), 0) + 1 FROM Productos"
        cur.execute(query)
        siguiente_orden = cur.fetchone()[0]

        cur.close()
        conn.close()

        return json_success({
            "siguiente_orden": siguiente_orden
        })

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": f"Error al obtener orden: {str(e)}"}
        )


@app.post('/admin/productos')
@app.post('/api/admin/productos')
def create_producto(body: ProductoCreateIn):
    """Crear un nuevo producto base en la estructura normalizada"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Insertar producto en la tabla normalizada
        query = """
            INSERT INTO Productos (
                nombre, 
                descripcion, 
                categoria, 
                imagen_mockup,
                area_impresion_ancho,
                area_impresion_alto,
                activo,
                orden_visualizacion,
                fecha_creacion,
                fecha_modificacion
            ) 
            VALUES (?, ?, ?, ?, ?, ?, 1, ?, GETDATE(), GETDATE())
        """
        cur.execute(query, (
            body.nombre, 
            body.descripcion, 
            body.categoria,
            body.imagen_mockup,
            body.area_impresion_ancho,
            body.area_impresion_alto,
            body.orden_visualizacion
        ))
        conn.commit()

        # Obtener el ID del producto creado
        cur.execute("SELECT @@IDENTITY")
        id_producto = cur.fetchone()[0]

        cur.close()
        conn.close()

        return json_success({
            "message": "Producto creado correctamente",
            "id_producto": int(id_producto),
            "nombre": body.nombre
        })

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": f"Error al crear producto: {str(e)}"}
        )


# ============================================================
# ENDPOINTS ADMIN - ATRIBUTOS Y VARIANTES
# ============================================================

@app.get('/api/admin/atributos')
def get_atributos():
    """Obtener todos los atributos con sus valores posibles"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Obtener atributos
        query_atributos = """
            SELECT id_atributo, nombre, tipo, descripcion, orden
            FROM Producto_Atributos
            ORDER BY orden, nombre
        """
        cur.execute(query_atributos)
        atributos_rows = cur.fetchall()

        atributos = []
        for row in atributos_rows:
            id_atributo = row[0]
            
            # Obtener valores de cada atributo
            query_valores = """
                SELECT id_valor, valor, codigo_color, orden
                FROM Producto_Atributo_Valores
                WHERE id_atributo = ?
                ORDER BY orden, valor
            """
            cur.execute(query_valores, (id_atributo,))
            valores_rows = cur.fetchall()
            
            valores = [
                {
                    "id_valor": v[0],
                    "valor": v[1],
                    "codigo_color": v[2],
                    "orden": v[3]
                }
                for v in valores_rows
            ]
            
            atributos.append({
                "id_atributo": id_atributo,
                "nombre": row[1],
                "tipo": row[2],
                "descripcion": row[3],
                "orden": row[4],
                "valores": valores
            })

        cur.close()
        conn.close()

        return json_success({
            "atributos": atributos
        })

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": f"Error al obtener atributos: {str(e)}"}
        )


class VarianteCreateIn(BaseModel):
    """Esquema para crear una variante"""
    atributos: dict  # {id_atributo: id_valor} ej: {1: 5, 2: 8}
    precio: float
    stock_actual: Optional[int] = 10
    stock_minimo: Optional[int] = 5
    stock_maximo: Optional[int] = 100
    sku: Optional[str] = None  # Si no se proporciona, se genera automáticamente


@app.post('/api/admin/productos/{id_producto}/variantes')
def create_variante(id_producto: int, body: VarianteCreateIn):
    """Crear una nueva variante para un producto"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Verificar que el producto existe
        cur.execute("SELECT nombre FROM Productos WHERE id_producto = ?", (id_producto,))
        producto = cur.fetchone()
        if not producto:
            cur.close()
            conn.close()
            raise HTTPException(
                status_code=404,
                detail={"success": False, "error": "Producto no encontrado"}
            )

        # Generar SKU si no se proporciona
        if not body.sku:
            # Obtener siglas del producto y valores de atributos para generar SKU
            nombre_producto = producto[0]
            siglas = ''.join([c[0] for c in nombre_producto.split()[:2]]).upper()
            
            # Obtener valores de atributos seleccionados
            valores_sku = []
            for id_atributo, id_valor in body.atributos.items():
                cur.execute(
                    "SELECT valor FROM Producto_Atributo_Valores WHERE id_valor = ?",
                    (id_valor,)
                )
                valor_row = cur.fetchone()
                if valor_row:
                    valores_sku.append(valor_row[0][:3].upper())
            
            # Contar variantes existentes para agregar número único
            cur.execute(
                "SELECT COUNT(*) FROM Producto_Variantes WHERE id_producto = ?",
                (id_producto,)
            )
            count = cur.fetchone()[0]
            
            sku = f"{siglas}-{'-'.join(valores_sku)}-{count + 1:03d}"
        else:
            sku = body.sku

        # Insertar variante
        query_variante = """
            INSERT INTO Producto_Variantes (
                id_producto, sku, precio, stock_actual, 
                stock_minimo, stock_maximo, activo
            )
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """
        cur.execute(query_variante, (
            id_producto,
            sku,
            body.precio,
            body.stock_actual,
            body.stock_minimo,
            body.stock_maximo
        ))
        conn.commit()

        # Obtener ID de la variante creada
        cur.execute("SELECT @@IDENTITY")
        id_variante = int(cur.fetchone()[0])

        # Insertar atributos de la variante
        for id_atributo, id_valor in body.atributos.items():
            query_atributo = """
                INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor)
                VALUES (?, ?, ?)
            """
            cur.execute(query_atributo, (id_variante, int(id_atributo), int(id_valor)))
        
        conn.commit()
        cur.close()
        conn.close()

        return json_success({
            "message": "Variante creada correctamente",
            "id_variante": id_variante,
            "sku": sku
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": f"Error al crear variante: {str(e)}"}
        )


class AtributoCreateIn(BaseModel):
    nombre: str

@app.post('/admin/atributos')
@app.post('/api/admin/atributos')
def create_atributo(body: AtributoCreateIn):
    """Crea un atributo si no existe, o retorna el id si ya existe"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Buscar si ya existe (case insensitive simplificado)
        cur.execute("SELECT id_atributo FROM Producto_Atributos WHERE LOWER(nombre) = LOWER(?)", (body.nombre,))
        row = cur.fetchone()
        
        if row:
            id_attr = row[0]
        else:
            # Crear nuevo
            cur.execute("INSERT INTO Producto_Atributos (nombre, tipo) VALUES (?, 'texto')", (body.nombre,))
            conn.commit()
            cur.execute("SELECT @@IDENTITY")
            id_attr = cur.fetchone()[0]
            
        cur.close()
        conn.close()
        return json_success({"id_atributo": int(id_attr)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})

class VarianteAdminCreateIn(BaseModel):
    id_producto: int
    sku: str
    precio: float
    stock: int
    valores: dict # id_atributo -> valor_texto

@app.post('/admin/variantes')
@app.post('/api/admin/variantes')
def create_variante_admin(body: VarianteAdminCreateIn):
    """Endpoint simplificado para la creación masiva desde el admin"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # 1. Crear la variante base
        query_var = "INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual, activo) VALUES (?, ?, ?, ?, 1)"
        cur.execute(query_var, (body.id_producto, body.sku, body.precio, body.stock))
        conn.commit()
        cur.execute("SELECT @@IDENTITY")
        id_variante = int(cur.fetchone()[0])
        
        # 2. Procesar los valores de los atributos
        for id_attr, valor_texto in body.valores.items():
            # Buscar si el valor ya existe para ese atributo
            cur.execute("SELECT id_valor FROM Producto_Atributo_Valores WHERE id_atributo = ? AND LOWER(valor) = LOWER(?)", 
                       (int(id_attr), str(valor_texto)))
            vrow = cur.fetchone()
            
            if vrow:
                id_valor = vrow[0]
            else:
                # Crear el valor
                cur.execute("INSERT INTO Producto_Atributo_Valores (id_atributo, valor) VALUES (?, ?)", 
                           (int(id_attr), str(valor_texto)))
                conn.commit()
                cur.execute("SELECT @@IDENTITY")
                id_valor = cur.fetchone()[0]
                
            # Vincular a la variante
            cur.execute("INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (?, ?, ?)", 
                       (id_variante, int(id_attr), int(id_valor)))
        
        conn.commit()
        cur.close()
        conn.close()
        return json_success({"id_variante": id_variante})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})


@app.get('/api/admin/productos/{id_producto}/variantes')
def get_variantes_producto(id_producto: int):
    """Obtener todas las variantes de un producto con sus atributos"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT 
                pv.id_variante,
                pv.sku,
                pv.precio,
                pv.stock_actual,
                pv.stock_minimo,
                pv.stock_maximo,
                pv.activo
            FROM Producto_Variantes pv
            WHERE pv.id_producto = ?
            ORDER BY pv.id_variante
        """
        cur.execute(query, (id_producto,))
        variantes_rows = cur.fetchall()

        variantes = []
        for row in variantes_rows:
            id_variante = row[0]
            
            # Obtener atributos de cada variante
            query_atributos = """
                SELECT 
                    pa.nombre as atributo,
                    pav.valor
                FROM Variante_Atributos va
                INNER JOIN Producto_Atributos pa ON va.id_atributo = pa.id_atributo
                INNER JOIN Producto_Atributo_Valores pav ON va.id_valor = pav.id_valor
                WHERE va.id_variante = ?
                ORDER BY pa.orden
            """
            cur.execute(query_atributos, (id_variante,))
            atributos_rows = cur.fetchall()
            
            atributos = {atr[0]: atr[1] for atr in atributos_rows}
            
            variantes.append({
                "id_variante": id_variante,
                "sku": row[1],
                "precio": float(row[2]),
                "stock_actual": row[3],
                "stock_minimo": row[4],
                "stock_maximo": row[5],
                "activo": bool(row[6]),
                "atributos": atributos
            })

        cur.close()
        conn.close()

        return json_success({
            "variantes": variantes,
            "total": len(variantes)
        })

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": f"Error al obtener variantes: {str(e)}"}
        )


# ============================================================
# ENDPOINTS ADMIN - CLIENTES
# ============================================================

@app.get('/api/admin/clientes')
def get_all_clientes():
    """Obtener todos los clientes con estadísticas de pedidos"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Query con estadísticas agregadas
        query = """
            SELECT 
                u.id_usuario,
                u.Nombre,
                u.Email,
                u.telefono,
                u.Tipo,
                u.fecha_registro,
                COUNT(DISTINCT p.id_pedido) as total_pedidos,
                ISNULL(SUM(p.total), 0) as total_gastado
            FROM Usuarios u
            LEFT JOIN Pedidos p ON u.id_usuario = p.id_usuario AND p.estado_pago = 'aprobado'
            WHERE u.Tipo = 'cliente'
            GROUP BY u.id_usuario, u.Nombre, u.Email, u.telefono, u.Tipo, u.fecha_registro
            ORDER BY total_gastado DESC, u.fecha_registro DESC
        """
        
        cur.execute(query)
        rows = cur.fetchall()

        clientes = []
        colores = ['#3b82f6', '#8b5cf6', '#ef4444', '#10b981', '#f59e0b', '#06b6d4', '#ec4899', '#14b8a6']
        
        for idx, row in enumerate(rows):
            # Generar iniciales del nombre
            nombre = row[1] or "Usuario"
            palabras = nombre.split()
            iniciales = "".join([p[0].upper() for p in palabras[:2]]) if palabras else "XX"
            
            # Formatear fecha de registro
            fecha_registro = ""
            if row[5]:
                fecha_registro = row[5].strftime("%d/%m/%Y")
            
            cliente = {
                "id": row[0],
                "nombre": nombre,
                "email": row[2] or "",
                "telefono": row[3] or "Sin teléfono",
                "tipo": row[4] or "cliente",
                "iniciales": iniciales,
                "color": colores[idx % len(colores)],
                "pedidos": int(row[6]) if row[6] else 0,
                "totalGastado": float(row[7]) if row[7] else 0.0,
                "fechaRegistro": fecha_registro
            }
            clientes.append(cliente)

        cur.close()
        conn.close()

        return json_success(clientes)

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Error al obtener clientes: {error_detail}")
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": f"Error al obtener clientes: {str(e)}"}
        )