from pydantic import BaseModel, EmailStr
from typing import Optional


class UserIn(BaseModel):
    fullname: str
    email: EmailStr
    phone: Optional[str] = None
    password: str


class UserOut(BaseModel):
    id_usuario: Optional[int]
    Nombre: str
    Email: EmailStr
    telefono: Optional[str] = None
    Tipo: Optional[str] = 'cliente'


class LoginIn(BaseModel):
    email: EmailStr
    password: str
