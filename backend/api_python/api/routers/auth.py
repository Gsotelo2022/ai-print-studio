"""
Router: autenticación
Rutas: POST /api/register, POST /api/login
El login emite un JWT que el frontend debe enviar como Bearer token.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from db import get_connection
from api.dependencies import json_success, hash_password, verify_password, create_token

router = APIRouter(prefix="/api", tags=["auth"])


# =========================
# MODELOS
# =========================
class RegisterIn(BaseModel):
    fullname: str
    email: str
    phone: Optional[str] = None
    password: str


class LoginIn(BaseModel):
    email: str
    password: str


# =========================
# REGISTER
# =========================
@router.post("/register")
def register(payload: RegisterIn):
    """Registrar un nuevo usuario (tipo cliente)"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # ✔️ PostgreSQL: todo en minúscula
        cur.execute(
            "SELECT COUNT(*) FROM usuarios WHERE email = %s",
            (payload.email,)
        )

        if cur.fetchone()[0] > 0:
            raise HTTPException(
                status_code=409,
                detail={"success": False, "error": "El email ya está registrado"},
            )

        hashed_pw = hash_password(payload.password)

        # ✔️ columnas en minúscula
        cur.execute(
            """
            INSERT INTO usuarios (nombre, email, telefono, password_user, tipo)
            VALUES (%s, %s, %s, %s, 'cliente')
            RETURNING id_usuario
            """,
            (payload.fullname, payload.email, payload.phone, hashed_pw),
        )

        user_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()

        token = create_token({
            "user_id": user_id,
            "email": payload.email,
            "tipo": "cliente"
        })

        return json_success({
            "user_id": user_id,
            "nombre": payload.fullname,
            "email": payload.email,
            "tipo": "cliente",
            "token": token,
        })

    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Error registrando usuario: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Error interno del servidor"}
        )


# =========================
# LOGIN
# =========================
@router.post("/login")
def login(payload: LoginIn):
    """Login: devuelve datos de usuario + JWT"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # ✔️ columnas y tabla en minúscula
        cur.execute(
            """
            SELECT id_usuario, nombre, email, password_user, tipo, cuenta_bloqueada
            FROM usuarios
            WHERE email = %s
            """,
            (payload.email,),
        )

        row = cur.fetchone()

        if not row:
            raise HTTPException(
                status_code=401,
                detail={"success": False, "error": "Email o contraseña incorrectos"},
            )

        user_id, nombre, email, password_hash, tipo, bloqueado = row

        if bloqueado:
            raise HTTPException(
                status_code=403,
                detail={"success": False, "error": "Cuenta bloqueada. Contacte al administrador"},
            )

        # ✔️ validación de password
        if not verify_password(payload.password, password_hash):
            raise HTTPException(
                status_code=401,
                detail={"success": False, "error": "Email o contraseña incorrectos"},
            )

        cur.close()
        conn.close()

        token = create_token({
            "user_id": user_id,
            "email": email,
            "tipo": tipo
        })

        return json_success({
            "user_id": user_id,
            "nombre": nombre,
            "email": email,
            "tipo": tipo,
            "token": token,
        })

    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Error en login: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Error interno del servidor"}
        )