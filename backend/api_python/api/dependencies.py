"""
Dependencias compartidas por todos los routers:
- Utilidades de respuesta (json_success)
- Hash y verificación de contraseñas
- Rutas de directorios de uploads
- Generación y validación de JWT (get_current_user, require_admin)
"""

import os
import hashlib
import secrets
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, Header


# ============================================================
# PATHS COMPARTIDOS
# ============================================================

# dependencies.py está en backend/api_python/api/
# parent       → backend/api_python/api/
# parent.parent → backend/api_python/
# parent.parent.parent → backend/
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent

UPLOADS_DIR    = BACKEND_DIR / "uploads" / "designs"
THUMBNAILS_DIR = BACKEND_DIR / "uploads" / "thumbnails"
IMAGENES_IA_DIR = BACKEND_DIR / "api" / "imagenes-generadas-con-IA"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)
IMAGENES_IA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# RESPUESTA ESTÁNDAR
# ============================================================

def json_success(data, extra: dict | None = None):
    """Formato de respuesta exitosa uniforme. `extra` agrega claves al nivel raíz (ej: paginacion)."""
    resp = {"success": True, "data": data}
    if extra:
        resp.update(extra)
    return resp


# ============================================================
# CONTRASEÑAS
# ============================================================

def hash_password(pw: str) -> str:
    """Hashear contraseña con PBKDF2 (SHA256)"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 100_000)
    return f"{salt}${hash_obj.hex()}"


def verify_password(plain: str, hashed: str) -> bool:
    """Verificar contraseña hasheada"""
    try:
        salt, hash_hex = hashed.split("$")
        hash_obj = hashlib.pbkdf2_hmac("sha256", plain.encode(), bytes.fromhex(salt), 100_000)
        return hash_obj.hex() == hash_hex
    except Exception:
        return False


# ============================================================
# JWT
# ============================================================

def _jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET", "")
    if not secret or len(secret) < 32:
        raise RuntimeError("JWT_SECRET no configurado o muy débil. El servidor no puede iniciar sin una clave segura en .env (¿mínimo 32 caracteres)")
    return secret


def create_token(payload: dict) -> str:
    """Generar JWT con expiración de 24 h"""
    from jose import jwt
    from datetime import datetime, timedelta

    data = {**payload, "exp": datetime.utcnow() + timedelta(hours=24)}
    return jwt.encode(data, _jwt_secret(), algorithm="HS256")


def get_current_user(authorization: Optional[str] = Header(default=None)) -> dict:
    """
    Dependencia FastAPI: extrae y valida el JWT del header Authorization.
    Uso: `user = Depends(get_current_user)`
    """
    from jose import jwt, JWTError

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail={"success": False, "error": "Token no provisto o formato inválido (Bearer <token>)"},
        )

    token = authorization.split(" ", 1)[1]

    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail={"success": False, "error": "Token inválido o expirado"},
        )


def require_admin(authorization: Optional[str] = Header(default=None)) -> dict:
    """
    Dependencia FastAPI: igual que get_current_user pero además exige tipo == 'admin'.
    Uso: `user = Depends(require_admin)`
    """
    user = get_current_user(authorization)
    if user.get("tipo") != "admin":
        raise HTTPException(
            status_code=403,
            detail={"success": False, "error": "Acceso restringido a administradores"},
        )
    return user
