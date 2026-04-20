from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
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

