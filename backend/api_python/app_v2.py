from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from db import get_connection
import hashlib
import secrets
import base64
import io
import os
from pathlib import Path
from PIL import Image
from datetime import datetime
from typing import Optional

from rembg import remove  # ✔ corregido (solo una vez)
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


# ============================================================
# APP
# ============================================================

app = FastAPI(title="AI Print Studio API v2", version="2.0.0")

BASE_DIR = Path(__file__).resolve().parent.parent

IMAGENES_IA_DIR = BASE_DIR / "backend" / "api" / "imagenes-generadas-con-IA"
IMAGENES_IA_DIR.mkdir(parents=True, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/imagenes", StaticFiles(directory=str(IMAGENES_IA_DIR)), name="imagenes")

def json_success(data):
    return {"success": True, "data": data}

@app.get("/api/health")
def health():
    return {"success": True}

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
# ============================================================
# CONFIGURACIÓN
# ============================================================

# CORS: permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directorios de uploads
BASE_DIR = Path(__file__).parent.parent
UPLOADS_DIR = BASE_DIR / 'uploads' / 'designs'
THUMBNAILS_DIR = BASE_DIR / 'uploads' / 'thumbnails'

# Crear directorios si no existen
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# MODELOS PYDANTIC
# ============================================================

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


class CreateOrderItemIn(BaseModel):
    """Item individual de un pedido"""
    id_variante: int
    cantidad: int
    archivo_diseno: int | None = None
    posicion_x: int = 0
    posicion_y: int = 0
    zoom: float = 1.0


class CreateOrderIn(BaseModel):
    """Crear pedido con múltiples items"""
    user_id: int
    items: list[CreateOrderItemIn]
    direccion_envio: str | None = None
    ciudad: str | None = None
    telefono_contacto: str | None = None
    notas_cliente: str | None = None


class UpdateOrderStatusIn(BaseModel):
    """Actualizar estado de pedido"""
    estado: str


class UpdatePaymentStatusIn(BaseModel):
    """Actualizar estado de pago"""
    estado_pago: str
    metodo_pago: str | None = None
    referencia_externa: str | None = None


class UpdateClienteIn(BaseModel):
    """Actualizar datos de un cliente"""
    nombre: str
    email: str
    telefono: Optional[str] = None
    tipo: str
    cuenta_bloqueada: bool

# ============================================================
# UTILIDADES
# ============================================================

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


# Manejador personalizado de excepciones HTTP
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Maneja las excepciones HTTP de manera personalizada"""
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": str(exc.detail)}
    )


# ============================================================
# ENDPOINTS: SALUD
# ============================================================

@app.get('/api/health')
def health():
    """Health check"""
    return json_success({"status": "ok", "version": "2.0.0"})


# ============================================================
# ENDPOINTS: AUTENTICACIÓN
# ============================================================

@app.post('/api/register')
def register(payload: RegisterIn):
    """Registrar un nuevo usuario"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Verificar si el email ya existe
        cur.execute("SELECT COUNT(*) FROM Usuarios WHERE Email = ?", (payload.email,))
        count = cur.fetchone()[0]
        if count > 0:
            raise HTTPException(
                status_code=409,
                detail={"success": False, "error": "El email ya está registrado"}
            )

        # Hashear contraseña
        hashed_pw = hash_password(payload.password)

        # Insertar usuario
        cur.execute("""
            INSERT INTO Usuarios (Nombre, Email, telefono, password_user, Tipo)
            OUTPUT INSERTED.id_usuario
            VALUES (?, ?, ?, ?, 'cliente')
        """, (payload.fullname, payload.email, payload.phone, hashed_pw))

        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return json_success({
            "user_id": user_id,
            "nombre": payload.fullname,
            "email": payload.email,
            "tipo": "cliente"
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
    """Login de usuario"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Buscar usuario por email
        cur.execute("""
            SELECT id_usuario, Nombre, Email, password_user, Tipo, cuenta_bloqueada
            FROM Usuarios
            WHERE Email = ?
        """, (payload.email,))

        row = cur.fetchone()
        if not row:
            raise HTTPException(
                status_code=401,
                detail={"success": False, "error": "Email o contraseña incorrectos"}
            )

        user_id, nombre, email, password_hash, tipo, bloqueado = row

        # Verificar si la cuenta está bloqueada
        if bloqueado:
            raise HTTPException(
                status_code=403,
                detail={"success": False, "error": "Cuenta bloqueada. Contacte al administrador"}
            )

        # Verificar contraseña
        if not verify_password(payload.password, password_hash):
            # Incrementar intentos fallidos
            cur.execute("""
                UPDATE Usuarios 
                SET intentos_login_fallidos = intentos_login_fallidos + 1,
                    cuenta_bloqueada = CASE WHEN intentos_login_fallidos >= 5 THEN 1 ELSE 0 END
                WHERE id_usuario = ?
            """, (user_id,))
            conn.commit()
            
            raise HTTPException(
                status_code=401,
                detail={"success": False, "error": "Email o contraseña incorrectos"}
            )

        # Login exitoso: resetear intentos fallidos y actualizar último login
        cur.execute("""
            UPDATE Usuarios 
            SET intentos_login_fallidos = 0,
                fecha_ultimo_login = GETDATE()
            WHERE id_usuario = ?
        """, (user_id,))
        conn.commit()

        cur.close()
        conn.close()

        return json_success({
            "user_id": user_id,
            "nombre": nombre,
            "email": email,
            "tipo": tipo
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": str(e)}
        )


# ============================================================
# ENDPOINTS: PRODUCTOS Y VARIANTES
# ============================================================

@app.get('/api/productos')
def get_productos():
    """Obtener catálogo de productos con sus variantes"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Obtener productos activos
        cur.execute("""
            SELECT id_producto, nombre, descripcion, categoria, imagen_mockup, 
                   area_impresion_ancho, area_impresion_alto
            FROM Productos
            WHERE activo = 1
            ORDER BY orden_visualizacion, nombre
        """)

        productos = []
        for row in cur.fetchall():
            id_prod, nombre, desc, categ, img, ancho, alto = row

            # Obtener variantes del producto
            cur.execute("""
                SELECT 
                    pv.id_variante,
                    pv.sku,
                    pv.precio,
                    pv.stock_actual
                FROM Producto_Variantes pv
                WHERE pv.id_producto = ? AND pv.activo = 1
                ORDER BY pv.precio
            """, (id_prod,))

            variantes = []
            for vrow in cur.fetchall():
                id_var, sku, precio, stock = vrow

                # Obtener atributos de esta variante
                cur.execute("""
                    SELECT pa.nombre, pav.valor, pav.codigo_color
                    FROM Variante_Atributos va
                    INNER JOIN Producto_Atributo_Valores pav ON va.id_valor = pav.id_valor
                    INNER JOIN Producto_Atributos pa ON pav.id_atributo = pa.id_atributo
                    WHERE va.id_variante = ?
                    ORDER BY pa.orden
                """, (id_var,))

                atributos = {}
                for arow in cur.fetchall():
                    attr_nombre, attr_valor, attr_color = arow
                    atributos[attr_nombre.lower()] = {
                        "valor": attr_valor,
                        "codigo_color": attr_color
                    }

                variantes.append({
                    "id_variante": id_var,
                    "sku": sku,
                    "precio": float(precio),
                    "stock": stock,
                    "atributos": atributos
                })

            # Obtener opciones de atributos disponibles para este producto
            cur.execute("""
                SELECT 
                    pa.id_atributo,
                    pa.nombre,
                    pa.tipo,
                    paa.requerido,
                    pa.orden
                FROM Producto_Atributos_Asignados paa
                INNER JOIN Producto_Atributos pa ON paa.id_atributo = pa.id_atributo
                WHERE paa.id_producto = ?
                ORDER BY pa.orden
            """, (id_prod,))

            opciones_atributos = []
            for orow in cur.fetchall():
                attr_id, attr_nombre, attr_tipo, requerido, _orden = orow

                # Obtener valores disponibles
                cur.execute("""
                    SELECT pav.id_valor, pav.valor, pav.codigo_color, pav.orden
                    FROM Producto_Atributo_Valores pav
                    WHERE pav.id_atributo = ?
                    ORDER BY pav.orden
                """, (attr_id,))

                valores = []
                for vrow in cur.fetchall():
                    val_id, val, color_code, val_orden = vrow
                    valores.append({
                        "valor": val,
                        "codigo_color": color_code
                    })

                opciones_atributos.append({
                    "nombre": attr_nombre,
                    "tipo": attr_tipo,
                    "requerido": bool(requerido),
                    "valores": valores
                })

            productos.append({
                "id_producto": id_prod,
                "nombre": nombre,
                "descripcion": desc,
                "categoria": categ,
                "imagen_mockup": img,
                "area_impresion": {
                    "ancho": ancho,
                    "alto": alto
                },
                "opciones_atributos": opciones_atributos,
                "variantes": variantes,
                "precio_desde": min([v["precio"] for v in variantes]) if variantes else 0
            })

        cur.close()
        conn.close()

        return json_success(productos)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": str(e)}
        )


@app.get('/api/variante/{id_variante}')
def get_variante_detalle(id_variante: int):
    """Obtener detalles de una variante específica"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                pv.id_variante,
                pv.sku,
                pv.precio,
                pv.stock_actual,
                p.nombre AS producto_nombre,
                p.descripcion,
                p.imagen_mockup
            FROM Producto_Variantes pv
            INNER JOIN Productos p ON pv.id_producto = p.id_producto
            WHERE pv.id_variante = ? AND pv.activo = 1
        """, (id_variante,))

        row = cur.fetchone()
        if not row:
            raise HTTPException(404, {"success": False, "error": "Variante no encontrada"})

        id_var, sku, precio, stock, prod_nombre, desc, img = row

        # Obtener atributos
        cur.execute("""
            SELECT pa.nombre, pav.valor, pav.codigo_color
            FROM Variante_Atributos va
            INNER JOIN Producto_Atributo_Valores pav ON va.id_valor = pav.id_valor
            INNER JOIN Producto_Atributos pa ON pav.id_atributo = pa.id_atributo
            WHERE va.id_variante = ?
        """, (id_var,))

        atributos = {}
        for arow in cur.fetchall():
            attr_nombre, attr_valor, attr_color = arow
            atributos[attr_nombre.lower()] = {
                "valor": attr_valor,
                "codigo_color": attr_color
            }

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
            "atributos": atributos
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


# ============================================================
# ENDPOINTS: ARCHIVOS/DISEÑOS
# ============================================================

@app.post('/api/upload-design')
async def upload_design(file: UploadFile, user_id: int):
    """Subir diseño personalizado"""
    try:
        # Validar tipo de archivo
        if not file.content_type.startswith('image/'):
            raise HTTPException(400, {"success": False, "error": "Solo se permiten imágenes"})

        # Leer archivo
        contents = await file.read()
        
        # Procesar con PIL
        img = Image.open(io.BytesIO(contents))
        ancho, alto = img.size

        # Calcular hash MD5
        hash_md5 = hashlib.md5(contents).hexdigest()

        # Generar nombre único
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = file.filename.split('.')[-1] if '.' in file.filename else 'png'
        nombre_almacenado = f"user{user_id}_{timestamp}_{hash_md5[:8]}.{ext}"

        # Guardar archivo
        ruta_completa = UPLOADS_DIR / nombre_almacenado
        with open(ruta_completa, 'wb') as f:
            f.write(contents)

        # Crear thumbnail
        thumbnail_nombre = f"thumb_{nombre_almacenado}"
        thumbnail_path = THUMBNAILS_DIR / thumbnail_nombre
        img_thumb = img.copy()
        img_thumb.thumbnail((200, 200), Image.Resampling.LANCZOS)
        img_thumb.save(thumbnail_path)

        # Rutas relativas
        ruta_relativa = f"uploads/designs/{nombre_almacenado}"
        ruta_thumb_relativa = f"uploads/thumbnails/{thumbnail_nombre}"

        # Insertar en BD
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO Archivos_Diseno (
                id_usuario, nombre_original, nombre_almacenado, ruta_archivo,
                ruta_thumbnail, tipo_mime, tamano_bytes, ancho_px, alto_px, hash_md5
            )
            OUTPUT INSERTED.id_archivo
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, file.filename, nombre_almacenado, ruta_relativa,
            ruta_thumb_relativa, file.content_type, len(contents), ancho, alto, hash_md5
        ))

        id_archivo = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return json_success({
            "id_archivo": id_archivo,
            "nombre": nombre_almacenado,
            "ruta": ruta_relativa,
            "thumbnail": ruta_thumb_relativa,
            "ancho": ancho,
            "alto": alto
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


@app.get('/uploads/{folder}/{filename}')
def serve_upload(folder: str, filename: str):
    """Servir archivos de upload"""
    if folder == 'designs':
        file_path = UPLOADS_DIR / filename
    elif folder == 'thumbnails':
        file_path = THUMBNAILS_DIR / filename
    else:
        raise HTTPException(404, {"success": False, "error": "Carpeta no válida"})

    if not file_path.exists():
        raise HTTPException(404, {"success": False, "error": "Archivo no encontrado"})

    return FileResponse(file_path)


# ============================================================
# ENDPOINTS: PEDIDOS
# ============================================================
from fastapi import HTTPException
from datetime import datetime

@app.post("/api/create-order")
def create_order(payload: dict):
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        # =========================
        # 1. VALIDAR USER
        # =========================
        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(status_code=400, detail="user_id es obligatorio")

        cur.execute(
            "SELECT COUNT(*) FROM Usuarios WHERE id_usuario = ?",
            (user_id,)
        )

        if cur.fetchone()[0] == 0:
            raise HTTPException(status_code=404, detail="Usuario no existe")

        # =========================
        # 2. VALIDAR ITEMS
        # =========================
        items = payload.get("items")

        if not items:
            raise HTTPException(status_code=400, detail="items es obligatorio")

        total = 0
        items_data = []

        for item in items:
            id_variante = item.get("id_variante")
            cantidad = item.get("cantidad", 1)

            if not id_variante:
                raise HTTPException(status_code=400, detail="id_variante faltante")

            cur.execute("""
                SELECT pv.precio, pv.stock_actual, p.nombre
                FROM Producto_Variantes pv
                INNER JOIN Productos p ON pv.id_producto = p.id_producto
                WHERE pv.id_variante = ? AND pv.activo = 1
            """, (id_variante,))

            row = cur.fetchone()

            if not row:
                raise HTTPException(status_code=400, detail="Variante no existe")

            precio, stock, nombre_prod = row

            if stock < cantidad:
                raise HTTPException(status_code=400, detail="Stock insuficiente")

            subtotal = float(precio) * cantidad
            total += subtotal

            items_data.append({
                "id_variante": id_variante,
                "cantidad": cantidad,
                "precio_unitario": float(precio),
                "subtotal": subtotal,
                "archivo_diseno": item.get("archivo_diseno"),
                "posicion_x": item.get("posicion_x", 0),
                "posicion_y": item.get("posicion_y", 0),
                "zoom": item.get("zoom", 1)
            })

        # =========================
        # 🎟️ VALIDAR Y APLICAR CUPÓN
        # =========================
        codigo_cupon = payload.get("codigo_cupon")
        id_cupon_usado = None
        descuento_porcentaje = 0
        monto_descuento = 0
        subtotal_original = total
        
        if codigo_cupon:
            # Verificar que el cupón existe y está activo
            cur.execute("""
                SELECT id_cupon, descuento_porcentaje, usos_maximos, usos_actuales, 
                       fecha_expiracion, activo
                FROM Cupones
                WHERE codigo = ? AND activo = 1
            """, (codigo_cupon,))
            
            cupon = cur.fetchone()
            
            if not cupon:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Cupón '{codigo_cupon}' no válido o inactivo"
                )
            
            id_cupon, porcentaje, usos_max, usos_actual, fecha_exp, activo = cupon
            
            # Validar fecha de expiración
            if fecha_exp and datetime.now().date() > fecha_exp:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cupón '{codigo_cupon}' expirado"
                )
            
            # Validar usos restantes
            if usos_max and usos_actual >= usos_max:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cupón '{codigo_cupon}' alcanzó el límite de usos"
                )
            
            id_cupon_usado = id_cupon
            descuento_porcentaje = float(porcentaje)
            monto_descuento = (float(total) * float(porcentaje)) / 100
            total = float(total) - monto_descuento
            
            # Incrementar contador de usos
            cur.execute("""
                UPDATE Cupones
                SET usos_actuales = usos_actuales + 1
                WHERE id_cupon = ?
            """, (id_cupon,))
            
            print(f"✅ Cupón aplicado: {codigo_cupon} (-{porcentaje}%, -${monto_descuento:.2f})")

        # =========================
        # 3. GUARDAR ARCHIVOS DE DISEÑO
        # =========================
        for item in items_data:
            archivo_data = item.get("archivo_diseno")
            
            if archivo_data:
                print(f"🔍 Procesando archivo_diseno: tipo={type(archivo_data)}, length={len(str(archivo_data)) if archivo_data else 0}")
                
                # Detectar si es base64 y guardar como archivo en disco
                if isinstance(archivo_data, str) and archivo_data.startswith("data:image"):
                    print(f"📸 Detectado base64, procesando imagen de {len(archivo_data)} caracteres...")
                    try:
                        # Decodificar base64
                        header, encoded = archivo_data.split(",", 1)
                        image_bytes = base64.b64decode(encoded)
                        
                        # Procesar con PIL
                        img = Image.open(io.BytesIO(image_bytes))
                        ancho, alto = img.size
                        
                        # Calcular hash MD5
                        hash_md5 = hashlib.md5(image_bytes).hexdigest()
                        
                        # Generar nombre único
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        nombre_almacenado = f"user{user_id}_{timestamp}_{hash_md5[:8]}.png"
                        
                        # Guardar archivo en disco
                        ruta_completa = UPLOADS_DIR / nombre_almacenado
                        with open(ruta_completa, 'wb') as f:
                            f.write(image_bytes)
                        
                        # Crear thumbnail
                        thumbnail_nombre = f"thumb_{nombre_almacenado}"
                        thumbnail_path = THUMBNAILS_DIR / thumbnail_nombre
                        img_thumb = img.copy()
                        img_thumb.thumbnail((200, 200), Image.Resampling.LANCZOS)
                        img_thumb.save(thumbnail_path)
                        
                        # Rutas relativas para guardar en BD
                        ruta_relativa = f"uploads/designs/{nombre_almacenado}"
                        ruta_thumb_relativa = f"uploads/thumbnails/{thumbnail_nombre}"
                        
                        # Prompt usado
                        prompt_usado = payload.get("prompt") or payload.get("notas_cliente") or "Diseño personalizado"
                        
                        # Insertar en BD
                        cur.execute("""
                            INSERT INTO Archivos_Diseno (
                                id_usuario, nombre_original, nombre_almacenado, ruta_archivo,
                                ruta_thumbnail, tipo_mime, tamano_bytes, ancho_px, alto_px, 
                                hash_md5, es_generado_ia, prompt_usado, fecha_subida
                            )
                            OUTPUT INSERTED.id_archivo
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
                        """, (
                            user_id,
                            "diseno_generado.png",
                            nombre_almacenado,
                            ruta_relativa,
                            ruta_thumb_relativa,
                            "image/png",
                            len(image_bytes),
                            ancho,
                            alto,
                            hash_md5,
                            1,  # es_generado_ia
                            prompt_usado
                        ))
                        
                        id_archivo = cur.fetchone()[0]
                        item["id_archivo"] = id_archivo
                        
                        print(f"✅ Archivo guardado: {ruta_relativa} ({len(image_bytes)} bytes)")
                        
                    except Exception as e:
                        print(f"❌ Error guardando archivo de diseño: {e}")
                        item["id_archivo"] = None
                else:
                    # Si es un ID de archivo existente, úsalo directamente
                    item["id_archivo"] = archivo_data if isinstance(archivo_data, int) else None
            else:
                item["id_archivo"] = None

        # =========================
        # 4. ORDEN
        # =========================
        cur.execute("SELECT ISNULL(MAX(id_pedido), 0) FROM Pedidos")
        last_id = cur.fetchone()[0]

        numero_orden = f"ORD-{datetime.now().year}-{str(last_id + 1).zfill(5)}"

        cur.execute("""
            INSERT INTO Pedidos (
                numero_orden, id_usuario, subtotal, descuento, total,
                direccion_envio, ciudad, telefono_contacto, notas_cliente
            )
            OUTPUT INSERTED.id_pedido
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            numero_orden,
            user_id,
            subtotal_original,  # Precio sin descuento
            monto_descuento,  # Monto del descuento (0 si no hay cupón)
            total,  # Precio final con descuento
            payload.get("direccion_envio"),
            payload.get("ciudad"),
            payload.get("telefono_contacto"),
            payload.get("notas_cliente")
        ))

        id_pedido = cur.fetchone()[0]

        for item in items_data:
            cur.execute("""
                INSERT INTO Pedidos_Items (
                    id_pedido, id_variante, cantidad, precio_unitario,
                    archivo_diseno, diseno_posicion_x, diseno_posicion_y, diseno_zoom,
                    tiene_diseno
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                id_pedido,
                item["id_variante"],
                item["cantidad"],
                item["precio_unitario"],
                item["id_archivo"],  # Ahora es INT, no string
                item["posicion_x"],
                item["posicion_y"],
                item["zoom"],
                1 if item["id_archivo"] else 0
            ))

        conn.commit()

        return {
            "success": True,
            "data": {
                "order_id": id_pedido,
                "numero_orden": numero_orden,
                "total": total,
                "items_count": len(items_data)
            }
        }

    except HTTPException as e:
        if conn:
            conn.rollback()
        raise e

    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            
# ============================================================
# ENDPOINTS: ADMIN - DASHBOARD
# ============================================================

@app.get('/api/admin/dashboard-stats')
def admin_get_dashboard_stats(page: int = 1, limit: int = 10):
    """Obtener estadísticas del dashboard"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # =========================
        # STATS
        # =========================
        # Total usuarios
        cur.execute("SELECT COUNT(*) as total FROM Usuarios")
        total_usuarios = cur.fetchone()[0]

        # Usuarios última semana
        cur.execute("""
            SELECT COUNT(*) as total 
            FROM Usuarios 
            WHERE fecha_registro >= DATEADD(day, -7, GETDATE())
        """)
        usuarios_semana = cur.fetchone()[0]

        # Usuarios por tipo
        cur.execute("""
            SELECT tipo as tipo_usuario, COUNT(*) as total
            FROM Usuarios
            GROUP BY tipo
        """)
        usuarios_por_tipo = [{"tipo_usuario": row[0], "total": row[1]} for row in cur.fetchall()]

        # =========================
        # ACTIVIDAD (últimos 5 usuarios)
        # =========================
        cur.execute("""
            SELECT TOP 5 
                id_usuario,
                Nombre as nombre,
                '' as apellido,
                tipo as tipo_usuario,
                DATEDIFF(MINUTE, fecha_registro, GETDATE()) as minutos_desde_registro
            FROM Usuarios
            ORDER BY fecha_registro DESC
        """)
        actividad = []
        for row in cur.fetchall():
            actividad.append({
                "id_usuario": row[0],
                "nombre": row[1],
                "apellido": row[2],
                "tipo_usuario": row[3],
                "minutos_desde_registro": row[4]
            })

        # =========================
        # PAGINACIÓN
        # =========================
        offset = (page - 1) * limit
        total_registros = total_usuarios
        total_paginas = (total_registros + limit - 1) // limit  # ceil division

        # =========================
        # USUARIOS PAGINADOS
        # =========================
        cur.execute("""
            SELECT 
                id_usuario,
                Nombre as nombre,
                Email as email,
                tipo as tipo_usuario,
                fecha_registro
            FROM Usuarios
            ORDER BY id_usuario
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
        """, (offset, limit))

        usuarios = []
        for row in cur.fetchall():
            fecha_registro = row[4]
            if fecha_registro:
                fecha_registro = fecha_registro.isoformat() if hasattr(fecha_registro, 'isoformat') else str(fecha_registro)
            
            usuarios.append({
                "id_usuario": row[0],
                "nombre": row[1],
                "email": row[2],
                "tipo_usuario": row[3],
                "fecha_registro": fecha_registro
            })

        return {
            "success": True,
            "stats": {
                "total_usuarios": total_usuarios,
                "usuarios_semana": usuarios_semana,
                "usuarios_por_tipo": usuarios_por_tipo
            },
            "usuarios": usuarios,
            "actividad": actividad,
            "paginacion": {
                "pagina_actual": page,
                "total_paginas": total_paginas,
                "total_registros": total_registros,
                "registros_por_pagina": limit
            }
        }

    except Exception as e:
        print(f"❌ Error en admin_get_dashboard_stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# ============================================================
# ENDPOINTS: CUPONES PARA CLIENTES
# ============================================================

@app.get('/api/cupones/disponibles/{id_cliente}')
def obtener_cupones_disponibles_cliente(id_cliente: int):
    """
    Obtener cupones disponibles para un cliente específico según su perfil
    
    Lógica de negocio:
    - Cupones con 'BIENVENIDA' o 'PRIMERA': Solo para clientes sin compras
    - Cupones con 'FIDELIDAD' o 'VIP': Para clientes con 5+ compras
    - Cupones con 'REGRESO' o 'VUELVE': Para clientes inactivos (>30 días)
    - Cupones genéricos: Para todos los clientes
    
    Retorna cupones activos, no expirados y con usos disponibles
    """
    conn = None
    cur = None
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # ============================================================
        # 1. OBTENER CUPONES ACTIVOS
        # ============================================================
        cur.execute("""
            SELECT 
                id_cupon,
                codigo, 
                descripcion, 
                descuento_porcentaje, 
                fecha_expiracion, 
                usos_actuales, 
                usos_maximos
            FROM Cupones
            WHERE activo = 1 
            AND (fecha_expiracion IS NULL OR fecha_expiracion > GETDATE())
            AND (usos_maximos IS NULL OR usos_actuales < usos_maximos)
            ORDER BY descuento_porcentaje DESC
        """)
        
        cupones_db = cur.fetchall()
        
        if not cupones_db:
            return json_success({
                'cupones': [],
                'total': 0,
                'perfil_cliente': None,
                'mensaje': 'No hay cupones disponibles en este momento'
            })
        
        # ============================================================
        # 2. OBTENER PERFIL DEL CLIENTE
        # ============================================================
        cur.execute("""
            SELECT 
                COUNT(*) as total_pedidos,
                MAX(fecha_pedido) as ultima_compra,
                SUM(total) as gasto_total
            FROM Pedidos
            WHERE id_usuario = ? AND estado != 'cancelado'
        """, (id_cliente,))
        
        perfil = cur.fetchone()
        total_pedidos = perfil[0] if perfil else 0
        ultima_compra = perfil[1] if perfil else None
        gasto_total = float(perfil[2]) if perfil and perfil[2] else 0.0
        
        # ============================================================
        # 3. CALCULAR DÍAS DESDE ÚLTIMA COMPRA
        # ============================================================
        dias_inactivo = 999
        if ultima_compra:
            dias_inactivo = (datetime.now() - ultima_compra).days
        
        # ============================================================
        # 4. APLICAR LÓGICA DE NEGOCIO - FILTRAR CUPONES
        # ============================================================
        cupones_aplicables = []
        
        for cupon in cupones_db:
            id_cupon, codigo, descripcion, descuento, expiracion, usos_actuales, usos_maximos = cupon
            codigo_upper = codigo.upper()
            
            # Variables para determinar aplicabilidad
            es_aplicable = False
            razon = None
            categoria = 'general'
            
            # ============================================================
            # REGLA 1: CUPONES DE BIENVENIDA (Clientes nuevos)
            # ============================================================
            if any(palabra in codigo_upper for palabra in ['BIENVENIDA', 'PRIMERA', 'WELCOME', 'NUEVO']):
                if total_pedidos == 0:
                    es_aplicable = True
                    razon = '🎉 ¡Bienvenido! Tu primera compra'
                    categoria = 'primera_compra'
            
            # ============================================================
            # REGLA 2: CUPONES DE FIDELIDAD (Clientes recurrentes)
            # ============================================================
            elif any(palabra in codigo_upper for palabra in ['FIDELIDAD', 'VIP', 'PREMIUM', 'FRECUENTE']):
                if total_pedidos >= 5:
                    es_aplicable = True
                    razon = f'⭐ Cliente VIP - {total_pedidos} compras realizadas'
                    categoria = 'fidelidad'
            
            # ============================================================
            # REGLA 3: CUPONES DE REGRESO (Clientes inactivos)
            # ============================================================
            elif any(palabra in codigo_upper for palabra in ['REGRESO', 'VUELVE', 'COMEBACK', 'EXTRAÑAMOS']):
                if total_pedidos > 0 and dias_inactivo > 30:
                    es_aplicable = True
                    razon = f'💌 ¡Te extrañamos! (Inactivo {dias_inactivo} días)'
                    categoria = 'reactivacion'
            
            # ============================================================
            # REGLA 4: CUPONES POR MONTO GASTADO (Alto valor)
            # ============================================================
            elif any(palabra in codigo_upper for palabra in ['ESPECIAL', 'EXCLUSIVO', 'ELITE']):
                if gasto_total >= 10000:  # $10,000+ en compras
                    es_aplicable = True
                    razon = f'💎 Cliente especial - ${gasto_total:.0f} en compras'
                    categoria = 'alto_valor'
            
            # ============================================================
            # REGLA 5: CUPONES GENÉRICOS (Para todos)
            # ============================================================
            else:
                es_aplicable = True
                razon = None
                categoria = 'general'
            
            # ============================================================
            # AGREGAR CUPÓN SI ES APLICABLE
            # ============================================================
            if es_aplicable:
                # Calcular usos restantes
                usos_restantes = None
                if usos_maximos:
                    usos_restantes = usos_maximos - (usos_actuales or 0)
                
                # Formatear fecha de expiración
                fecha_exp_str = None
                if expiracion:
                    fecha_exp_str = expiracion.strftime('%Y-%m-%d') if hasattr(expiracion, 'strftime') else str(expiracion)
                
                cupones_aplicables.append({
                    'id_cupon': id_cupon,
                    'codigo': codigo,
                    'descripcion': descripcion,
                    'descuento': int(descuento),
                    'expiracion': fecha_exp_str,
                    'usos_restantes': usos_restantes,
                    'razon': razon,
                    'categoria': categoria,
                    'es_limitado': usos_maximos is not None
                })
        
        # ============================================================
        # 5. ORDENAR CUPONES POR RELEVANCIA
        # ============================================================
        # Orden de prioridad: primera_compra > reactivacion > fidelidad > alto_valor > general
        orden_categorias = {
            'primera_compra': 1,
            'reactivacion': 2,
            'fidelidad': 3,
            'alto_valor': 4,
            'general': 5
        }
        
        cupones_aplicables.sort(key=lambda x: (orden_categorias.get(x['categoria'], 99), -x['descuento']))
        
        # ============================================================
        # 6. RETORNAR RESPUESTA
        # ============================================================
        return json_success({
            'cupones': cupones_aplicables,
            'total': len(cupones_aplicables),
            'perfil_cliente': {
                'total_pedidos': total_pedidos,
                'dias_inactivo': dias_inactivo if total_pedidos > 0 else None,
                'gasto_total': gasto_total,
                'es_cliente_nuevo': total_pedidos == 0,
                'es_cliente_vip': total_pedidos >= 5,
                'es_cliente_inactivo': dias_inactivo > 30 if total_pedidos > 0 else False
            },
            'mensaje': f'Se encontraron {len(cupones_aplicables)} cupón(es) disponible(s) para ti' if cupones_aplicables else 'No hay cupones disponibles para tu perfil'
        })
        
    except Exception as e:
        print(f"❌ Error en obtener_cupones_disponibles_cliente: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# ============================================================
# ENDPOINTS: ADMIN - PEDIDOS
# ============================================================

@app.get('/api/admin/pedidos')
def admin_get_pedidos(filtro: str = 'todos'):
    """Obtener todos los pedidos para administración"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Construir query según filtro
        where_clause = ""
        if filtro == 'pendientes':
            where_clause = "WHERE p.estado = 'pendiente'"
        elif filtro == 'pagados':
            where_clause = "WHERE p.estado_pago = 'aprobado'"
        elif filtro == 'no-pagados':
            where_clause = "WHERE p.estado_pago IN ('pendiente', 'rechazado')"
        elif filtro == 'entregados':
            where_clause = "WHERE p.estado = 'completado'"

        cur.execute(f"""
            SELECT 
                p.id_pedido,
                p.numero_orden,
                p.fecha_pedido,
                p.estado,
                p.estado_pago,
                p.total,
                u.Nombre AS cliente_nombre,
                u.Email AS cliente_email,
                u.telefono AS cliente_telefono,
                p.direccion_envio,
                p.ciudad
            FROM Pedidos p
            INNER JOIN Usuarios u ON p.id_usuario = u.id_usuario
            {where_clause}
            ORDER BY p.fecha_pedido DESC
        """)

        pedidos = []
        colores = ['#3b82f6', '#8b5cf6', '#ef4444', '#10b981', '#f59e0b', '#06b6d4', '#ec4899', '#8b5cf6']
        
        for idx, row in enumerate(cur.fetchall()):
            id_pedido = row[0]
            
            # Obtener items del pedido con sus variantes y productos
            cur.execute("""
                SELECT 
                    pi.cantidad,
                    pi.precio_unitario,
                    prod.nombre AS producto_nombre,
                    pv.id_variante,
                    MAX(CASE WHEN pa.nombre = 'Color' THEN pav.valor END) AS color,
                    MAX(CASE WHEN pa.nombre = 'Talle' THEN pav.valor END) AS talle
                FROM Pedidos_Items pi
                INNER JOIN Producto_Variantes pv ON pi.id_variante = pv.id_variante
                INNER JOIN Productos prod ON pv.id_producto = prod.id_producto
                LEFT JOIN Variante_Atributos va ON pv.id_variante = va.id_variante
                LEFT JOIN Producto_Atributo_Valores pav ON va.id_valor = pav.id_valor
                LEFT JOIN Producto_Atributos pa ON pav.id_atributo = pa.id_atributo
                WHERE pi.id_pedido = ?
                GROUP BY pi.cantidad, pi.precio_unitario, prod.nombre, pv.id_variante
            """, (id_pedido,))
            
            items = []
            for item_row in cur.fetchall():
                items.append({
                    "cantidad": item_row[0],
                    "precio_unitario": float(item_row[1]),
                    "producto_nombre": item_row[2],
                    "color": item_row[4] or '-',
                    "talle": item_row[5] or '-'
                })
            
            # Usar el primer item como detalle principal (para compatibilidad con frontend actual)
            if items:
                detalle = items[0]
                producto_nombre = detalle["producto_nombre"].lower()
            else:
                detalle = {
                    "producto_nombre": "Sin producto",
                    "color": "-",
                    "talle": "-",
                    "cantidad": 0
                }
                producto_nombre = "sin producto"
            
            # Obtener emoji del producto
            if 'remera' in producto_nombre or 'camiseta' in producto_nombre:
                emoji = '👕'
            elif 'buzo' in producto_nombre or 'sudadera' in producto_nombre:
                emoji = '🧥'
            elif 'taza' in producto_nombre:
                emoji = '☕'
            elif 'gorra' in producto_nombre:
                emoji = '🧢'
            elif 'bolso' in producto_nombre or 'tote' in producto_nombre:
                emoji = '👜'
            else:
                emoji = '📦'
            
            pedidos.append({
                "id": id_pedido,
                "numero": row[1],
                "fecha": {
                    "dia": row[2].strftime('%d/%m/%Y') if row[2] else '-',
                    "hora": row[2].strftime('%H:%M') if row[2] else '-'
                },
                "estado": {
                    "tipo": row[3],
                    "texto": row[3].title()
                },
                "pago": {
                    "tipo": 'pagado' if row[4] == 'aprobado' else 'no-pagado',
                    "texto": 'Pagado' if row[4] == 'aprobado' else 'Pendiente',
                    "valor": row[4]
                },
                "total": float(row[5]),
                "cliente": {
                    "nombre": row[6],
                    "email": row[7],
                    "telefono": row[8] or 'Sin teléfono',
                    "iniciales": "".join([p[0].upper() for p in row[6].split()[:2]]),
                    "color": colores[idx % len(colores)]
                },
                "envio": {
                    "direccion": row[9],
                    "ciudad": row[10]
                },
                "detalle": detalle,
                "producto": {
                    "nombre": detalle["producto_nombre"],
                    "detalles": f"{detalle['color']} • {detalle['talle']} × {detalle.get('cantidad', 1)}",
                    "emoji": emoji
                },
                "items": items
            })

        cur.close()
        conn.close()

        print(f"✅ Devolviendo {len(pedidos)} pedidos")
        for idx, p in enumerate(pedidos[:3]):  # Mostrar solo los primeros 3 para debug
            print(f"  Pedido {idx+1}: id={p.get('id')}, producto={p.get('producto', {}).get('nombre')}, cliente={p.get('cliente', {}).get('nombre')}")

        return json_success(pedidos)

    except Exception as e:
        print(f"❌ Error en admin_get_pedidos: {str(e)}")
        raise HTTPException(500, {"success": False, "error": str(e)})


@app.get('/api/admin/pedidos/{id_pedido}')
def admin_get_pedido_detalle(id_pedido: int):
    """Obtener detalles completos de un pedido"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Obtener encabezado del pedido
        cur.execute("""
            SELECT 
                p.id_pedido,
                p.numero_orden,
                p.fecha_pedido,
                p.estado,
                p.estado_pago,
                p.subtotal,
                p.descuento,
                p.gastos_envio,
                p.total,
                u.Nombre,
                u.Email,
                u.telefono,
                p.direccion_envio,
                p.ciudad,
                p.provincia,
                p.codigo_postal,
                p.telefono_contacto,
                p.notas_cliente,
                p.notas_admin
            FROM Pedidos p
            INNER JOIN Usuarios u ON p.id_usuario = u.id_usuario
            WHERE p.id_pedido = ?
        """, (id_pedido,))

        row = cur.fetchone()
        if not row:
            raise HTTPException(404, {"success": False, "error": "Pedido no encontrado"})

        pedido = {
            "id_pedido": row[0],
            "numero_orden": row[1],
            "fecha_pedido": row[2].isoformat() if row[2] else None,
            "estado": row[3],
            "estado_pago": row[4],
            "subtotal": float(row[5]),
            "descuento": float(row[6]),
            "gastos_envio": float(row[7]),
            "total": float(row[8]),
            "cliente": {
                "nombre": row[9],
                "email": row[10],
                "telefono": row[11]
            },
            "envio": {
                "direccion": row[12],
                "ciudad": row[13],
                "provincia": row[14],
                "codigo_postal": row[15],
                "telefono_contacto": row[16]
            },
            "notas": {
                "cliente": row[17],
                "admin": row[18]
            }
        }

        # Obtener items
        cur.execute("""
            SELECT 
                pi.id_item,
                pi.cantidad,
                pi.precio_unitario,
                pi.subtotal,
                pi.estado,
                p.nombre AS producto_nombre,
                pv.sku,
                ad.ruta_thumbnail
            FROM Pedidos_Items pi
            INNER JOIN Producto_Variantes pv ON pi.id_variante = pv.id_variante
            INNER JOIN Productos p ON pv.id_producto = p.id_producto
            LEFT JOIN Archivos_Diseno ad ON pi.archivo_diseno = ad.id_archivo
            WHERE pi.id_pedido = ?
        """, (id_pedido,))

        items = []
        for irow in cur.fetchall():
            items.append({
                "id_item": irow[0],
                "cantidad": irow[1],
                "precio_unitario": float(irow[2]),
                "subtotal": float(irow[3]),
                "estado": irow[4],
                "producto": irow[5],
                "sku": irow[6],
                "thumbnail": irow[7]
            })

        pedido["items"] = items

        cur.close()
        conn.close()

        return json_success(pedido)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


@app.put('/api/admin/pedidos/{id_pedido}/estado')
def admin_update_pedido_estado(id_pedido: int, payload: UpdateOrderStatusIn):
    """Actualizar estado de un pedido"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Validar que el pedido existe
        cur.execute("SELECT COUNT(*) FROM Pedidos WHERE id_pedido = ?", (id_pedido,))
        if cur.fetchone()[0] == 0:
            raise HTTPException(404, {"success": False, "error": "Pedido no encontrado"})

        # Actualizar estado
        cur.execute("""
            UPDATE Pedidos
            SET estado = ?
            WHERE id_pedido = ?
        """, (payload.estado, id_pedido))

        conn.commit()
        cur.close()
        conn.close()

        return json_success({"id_pedido": id_pedido, "estado": payload.estado})

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


@app.put('/api/admin/pedidos/{id_pedido}/pago')
def admin_update_pedido_pago(id_pedido: int, payload: UpdatePaymentStatusIn):
    """Actualizar estado de pago de un pedido"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Actualizar estado de pago
        cur.execute("""
            UPDATE Pedidos
            SET estado_pago = ?,
                fecha_pago = CASE WHEN ? = 'aprobado' THEN GETDATE() ELSE fecha_pago END
            WHERE id_pedido = ?
        """, (payload.estado_pago, payload.estado_pago, id_pedido))

        # Crear registro en tabla Pagos
        if payload.estado_pago in ['aprobado', 'rechazado']:
            # Obtener total del pedido
            cur.execute("SELECT total FROM Pedidos WHERE id_pedido = ?", (id_pedido,))
            total = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO Pagos (
                    id_pedido, metodo_pago, referencia_externa, monto, estado,
                    fecha_aprobacion
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                id_pedido,
                payload.metodo_pago or 'manual',
                payload.referencia_externa,
                total,
                payload.estado_pago,
                datetime.now() if payload.estado_pago == 'aprobado' else None
            ))

        conn.commit()
        cur.close()
        conn.close()

        return json_success({
            "id_pedido": id_pedido,
            "estado_pago": payload.estado_pago
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


# ============================================================
# ENDPOINTS: ADMIN - CLIENTES
# ============================================================

@app.get('/api/admin/clientes')
def admin_get_clientes():
    """Obtener listado de clientes con estadísticas"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                u.id_usuario,
                u.Nombre,
                u.Email,
                u.telefono,
                u.fecha_registro,
                u.Tipo,
                u.cuenta_bloqueada,
                COUNT(p.id_pedido) AS pedidos_count,
                ISNULL(SUM(CASE WHEN p.estado_pago = 'aprobado' THEN p.total ELSE 0 END), 0) AS total_gastado
            FROM Usuarios u
            LEFT JOIN Pedidos p ON u.id_usuario = p.id_usuario
            WHERE u.Tipo = 'cliente'
            GROUP BY u.id_usuario, u.Nombre, u.Email, u.telefono, u.fecha_registro, u.Tipo, u.cuenta_bloqueada
            ORDER BY total_gastado DESC
        """)

        clientes = []
        colores = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']

        for idx, row in enumerate(cur.fetchall()):
            nombre_partes = row[1].strip().split()
            iniciales = "".join([p[0].upper() for p in nombre_partes[:2]])

            clientes.append({
                "id": row[0],
                "nombre": row[1],
                "email": row[2],
                "telefono": row[3],
                "fechaRegistro": row[4].isoformat() if row[4] else None,
                "tipo": row[5],
                "cuenta_bloqueada": bool(row[6]),
                "pedidos": row[7],
                "totalGastado": float(row[8]),
                "iniciales": iniciales,
                "color": colores[idx % len(colores)]
            })

        cur.close()
        conn.close()

        return json_success(clientes)

    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


@app.put('/api/admin/clientes/{id_cliente}')
def admin_update_cliente(id_cliente: int, payload: UpdateClienteIn):
    """Actualizar información de un cliente"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Verificar si el cliente existe
        cur.execute("SELECT COUNT(*) FROM Usuarios WHERE id_usuario = ?", (id_cliente,))
        if cur.fetchone()[0] == 0:
            raise HTTPException(404, {"success": False, "error": "Cliente no encontrado"})

        # Verificar si el nuevo email ya está en uso por otro usuario
        cur.execute("SELECT id_usuario FROM Usuarios WHERE Email = ? AND id_usuario != ?", (payload.email, id_cliente))
        otro_usuario = cur.fetchone()
        if otro_usuario:
            raise HTTPException(409, {"success": False, "error": "El email ya está en uso por otro cliente"})

        # Actualizar datos
        cur.execute("""
            UPDATE Usuarios
            SET Nombre = ?,
                Email = ?,
                telefono = ?,
                Tipo = ?,
                cuenta_bloqueada = ?
            WHERE id_usuario = ?
        """, (
            payload.nombre,
            payload.email,
            payload.telefono,
            payload.tipo,
            1 if payload.cuenta_bloqueada else 0,
            id_cliente
        ))

        conn.commit()
        cur.close()
        conn.close()

        return json_success({"id_cliente": id_cliente, "message": "Cliente actualizado correctamente"})

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})


# ============================================================
# ENDPOINTS: ADMIN - PRODUCTOS
# ============================================================

@app.get('/api/admin/productos')
def admin_get_productos():
    """Obtener listado de productos"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id_producto, nombre, descripcion, categoria, imagen_mockup, 
                   area_impresion_ancho, area_impresion_alto
            FROM Productos
            WHERE activo = 1
            ORDER BY orden_visualizacion, nombre
        """)

        productos = []
        for row in cur.fetchall():
            id_prod, nombre, desc, categ, img, ancho, alto = row

            productos.append({
                "id_producto": id_prod,
                "nombre": nombre,
                "descripcion": desc,
                "categoria": categ,
                "imagen_mockup": img,
                "area_impresion": {
                    "ancho": ancho,
                    "alto": alto
                }
            })

        cur.close()
        conn.close()

        return json_success(productos)

    except Exception as e:
        raise HTTPException(500, {"success": False, "error": str(e)})

from pydantic import BaseModel
import requests

class ConsultaIA(BaseModel):
    pregunta: str

@app.post("/api/admin/consulta-ia")
def consulta_ia(payload: ConsultaIA):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 🔹 Contexto real de la BD (esto hace inteligente al agente)
        cursor.execute("SELECT COUNT(*) FROM Usuarios")
        total_usuarios = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) 
            FROM Usuarios 
            WHERE fecha_registro >= DATEADD(day, -7, GETDATE())
        """)
        usuarios_semana = cursor.fetchone()[0]

        cursor.execute("""
            SELECT tipo, COUNT(*) 
            FROM Usuarios 
            GROUP BY tipo
        """)
        tipos = cursor.fetchall()

        resumen_tipos = ", ".join([f"{t[0]}: {t[1]}" for t in tipos])

        contexto = f"""
        Total de usuarios: {total_usuarios}
        Usuarios nuevos esta semana: {usuarios_semana}
        Usuarios por tipo: {resumen_tipos}
        """

        prompt = f"""
        Sos un asistente de administración de un sistema de ventas de ropa personalizada.

        Datos actuales del sistema:
        {contexto}

        Respondé de forma clara y breve.

        Pregunta:
        {payload.pregunta}
        """

        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "qwen2.5:1.5b",
            "prompt": prompt,
            "stream": False
        })

        data = response.json()

        return {
            "success": True,
            "respuesta": data["response"]
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================
# ENDPOINT: REMOVER FONDO CON IA (LOCAL)
# ============================================================

@app.post("/api/remove-background")
async def remove_background(file: UploadFile = File(...)):
    try:
        from rembg import remove

        # Validar tipo
        if not file.content_type.startswith("image/"):
            raise HTTPException(400, {"success": False, "error": "Solo imágenes permitidas"})

        # Leer imagen
        input_bytes = await file.read()

        # IA (rembg)
        output_bytes = remove(input_bytes)

        # 📁 Carpeta destino
        carpeta = BASE_DIR / "backend" / "api" / "imagenes-generadas-con-IA"
        carpeta.mkdir(parents=True, exist_ok=True)

        # 🧾 Nombre único (mejorado para evitar colisiones)
        nombre = f"sin_fondo_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
        ruta = carpeta / nombre

        # 💾 Guardar archivo
        with open(ruta, "wb") as f:
            f.write(output_bytes)

        # 🌐 URL
        url = f"http://localhost:8000/api/imagen/{nombre}"

        return {
            "success": True,
            "data": {
                "imagen_url": url
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": str(e)}
        )
    