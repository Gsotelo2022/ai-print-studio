from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
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
    user_id: int  # NUEVO: ID del usuario autenticado
    producto: str
    talle: str | None = None
    color: str
    cantidad: int
    prompt: str
    imagen_url: str
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


@app.post('/api/create-order')
def create_order(payload: CreateOrderIn):
    """Crear un nuevo pedido siguiendo la estructura: Pedidos + Pedidos_detalle"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Validar que el usuario existe
        cur.execute("SELECT COUNT(*) FROM Usuarios WHERE id_usuario = ?", (payload.user_id,))
        row = cur.fetchone()
        if not row or int(row[0]) == 0:
            raise HTTPException(
                status_code=404,
                detail={"success": False, "error": f"Usuario {payload.user_id} no existe"}
            )

        # Catálogo de productos con precios (DEFAULT: todos usan id_producto = 1 por ahora)
        catalogo = {
            'camiseta': {'nombre': 'Camiseta', 'precio': 12000, 'id_producto': 1},
            'taza': {'nombre': 'Taza', 'precio': 8000, 'id_producto': 1},
            'sudadera': {'nombre': 'Sudadera', 'precio': 18000, 'id_producto': 1},
            'buzo': {'nombre': 'Buzo', 'precio': 15000, 'id_producto': 1},
            'musculosa': {'nombre': 'Musculosa', 'precio': 10000, 'id_producto': 1},
            'gorra': {'nombre': 'Gorra', 'precio': 5000, 'id_producto': 1},
            'almohada': {'nombre': 'Almohada', 'precio': 9000, 'id_producto': 1},
            'mochila': {'nombre': 'Mochila', 'precio': 20000, 'id_producto': 1},
        }

        # Validar que el producto existe
        if payload.producto not in catalogo:
            raise HTTPException(
                status_code=400,
                detail={"success": False, "error": f"Producto no válido: {payload.producto}"}
            )

        producto_info = catalogo[payload.producto]
        precio_unitario = producto_info['precio']
        precio_total = precio_unitario * payload.cantidad
        id_producto = producto_info['id_producto']

        # 1. INSERTAR EN PEDIDOS con el id_usuario del usuario autenticado
        cur.execute("""
            INSERT INTO Pedidos (id_usuario)
            OUTPUT INSERTED.id_pedido
            VALUES (?)
        """, (payload.user_id,))
        
        row = cur.fetchone()
        order_id = row[0] if row else None

        if not order_id:
            raise Exception('No se pudo obtener el ID del pedido')

        # 2. INSERTAR EN PEDIDOS_DETALLE con los detalles del diseño
        detalle_text = f"Talle: {payload.talle}, Color: {payload.color}, Cantidad: {payload.cantidad}, Prompt: {payload.prompt}, Posición: ({payload.posicion_x}, {payload.posicion_y}), Zoom: {payload.zoom}"
        
        cur.execute("""
            INSERT INTO Pedidos_detalle (id_pedido, id_producto, detalle, imagen, estado, pago, total)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            order_id,
            id_producto,
            detalle_text,
            payload.imagen_url,
            'pendiente',
            'pendiente',
            precio_total
        ))

        conn.commit()
        cur.close()
        conn.close()

        return json_success({
            'order_id': order_id,
            'producto': producto_info['nombre'],
            'precio_unitario': precio_unitario,
            'cantidad': payload.cantidad,
            'precio_total': precio_total
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

