from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json

from db import get_connection
from schemas import UserIn, UserOut, LoginIn
from security import hash_password, verify_password

app = FastAPI()

# CORS liberal para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def success(data):
    return {"success": True, "data": data}


def error(msg, code=400):
    raise HTTPException(status_code=code, detail={"success": False, "error": msg})


@app.get('/api/users')
def get_users():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id_usuario AS Id, Nombre, Email FROM Usuarios ORDER BY Nombre")
        rows = cur.fetchall()
        users = [{"Id": r.Id, "Nombre": r.Nombre, "Email": r.Email} for r in rows]
        cur.close()
        conn.close()
        return success(users)
    except Exception as e:
        return error(f'Error al obtener usuarios: {e}', 500)


@app.post('/api/register')
def register(user: UserIn):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # verificar email único
        cur.execute("SELECT COUNT(*) FROM Usuarios WHERE Email = ?", (user.email,))
        cnt = cur.fetchone()[0]
        if cnt and int(cnt) > 0:
            cur.close()
            conn.close()
            return error('El email ya está registrado', 409)

        hashed = hash_password(user.password)
        cur.execute(
            "INSERT INTO Usuarios (Nombre, Email, telefono, [contraseña], Tipo) VALUES (?, ?, ?, ?, ?)",
            (user.fullname, user.email, user.phone, hashed, 'cliente')
        )
        # Obtener id insertado
        cur.execute("SELECT SCOPE_IDENTITY() AS id")
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return success({"id_usuario": int(new_id), "Nombre": user.fullname, "Email": user.email, "telefono": user.phone})
    except Exception as e:
        return error(f'Error al registrar usuario: {e}', 500)


@app.post('/api/login')
def login(payload: LoginIn):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id_usuario, Nombre, Email, [contraseña], Tipo FROM Usuarios WHERE Email = ?", (payload.email,))
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            return error('Credenciales inválidas', 401)

        stored_hash = getattr(row, 'contraseña', None)
        # algunos drivers mapean nombres, intentar por índice si es None
        if stored_hash is None:
            # intentar índice 3 (orden de SELECT)
            stored_hash = row[3]

        if not verify_password(payload.password, stored_hash):
            cur.close()
            conn.close()
            return error('Credenciales inválidas', 401)

        user = {"id_usuario": row.id_usuario if hasattr(row, 'id_usuario') else row[0], "Nombre": row.Nombre if hasattr(row, 'Nombre') else row[1], "Email": row.Email if hasattr(row, 'Email') else row[2], "Tipo": row.Tipo if hasattr(row, 'Tipo') else row[4]}
        cur.close()
        conn.close()
        return success(user)
    except Exception as e:
        return error(f'Error en login: {e}', 500)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=int(__import__('os').environ.get('PORT', 8000)), reload=True)
