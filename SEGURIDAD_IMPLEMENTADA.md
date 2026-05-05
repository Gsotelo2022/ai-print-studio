# 🔐 Seguridad — Cambios Implementados

**Fecha:** 4 de mayo de 2026  
**Estado:** ✅ 4 cambios implementados | ⏳ 4 cambios pendientes (producción)

---

## ✅ Cambios Implementados (Hoy)

### 1. ✅ #6 CORS Consistente en Node.js

**Ubicación:** `backend/server.js`

**Cambio realizado:**
```javascript
// ❌ Antes (aceptaba cualquier origen)
app.use(cors())

// ✅ Después (CORS configurado desde .env)
const allowedOrigins = (process.env.ALLOWED_ORIGINS || 'http://localhost:5173,http://localhost:3000').split(',').map(o => o.trim())
app.use(cors({
  origin: allowedOrigins
}))
```

**Beneficio:**
- Backend Node ahora rechaza CORS requests desde orígenes no autorizados
- Consistente con el backend FastAPI
- Configuración centralizada en `.env`

**Verificación:**
```bash
# El backend Node ahora respeta ALLOWED_ORIGINS
# Requests desde otros orígenes serán rechazados con CORS error
```

---

### 2. ✅ #2 JWT_SECRET Validación Fuerte

**Ubicación:** `backend/api_python/api/dependencies.py` (línea ~74)

**Cambio realizado:**
```python
# ❌ Antes (fallback débil)
def _jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET", "")
    if not secret:
        secret = "dev-secret-change-in-production"  # Inseguro
        print("⚠️  JWT_SECRET no configurado...")
    return secret

# ✅ Después (fail fast)
def _jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET", "")
    if not secret or len(secret) < 32:
        raise RuntimeError(
            "JWT_SECRET no configurado o muy débil. "
            "El servidor no puede iniciar sin una clave segura en .env (mínimo 32 caracteres)"
        )
    return secret
```

**Beneficio:**
- El servidor **no arranca** si JWT_SECRET falta o es muy corto
- Imposible ejecutar accidentalmente con secreto débil
- Fuerza a configuración correcta en `.env`

**Verificación:**
```bash
# Si JWT_SECRET no está en .env o tiene < 32 caracteres:
# El servidor lanza RuntimeError y no inicia
```

---

### 3. ✅ #4 Errores Genéricos en Respuestas API

**Ubicación:** `backend/api_python/api/routers/auth.py`

**Cambio realizado — Registro:**
```python
# ❌ Antes (expone detalles internos)
except Exception as e:
    print("ERROR REGISTER:", str(e))
    raise HTTPException(
        status_code=500,
        detail={"success": False, "error": str(e)}  # ← SQL errors, detalles DB, etc.
    )

# ✅ Después (genérico, loguea internamente)
except Exception as e:
    import logging
    logging.error(f"Error registrando usuario: {str(e)}")  # Loguea en el servidor
    raise HTTPException(
        status_code=500,
        detail={"success": False, "error": "Error interno del servidor"}  # Genérico al cliente
    )
```

**Cambio realizado — Login:**
```python
# ❌ Antes (expone detalles)
except Exception as e:
    print("ERROR LOGIN:", str(e))
    raise HTTPException(
        status_code=500,
        detail={"success": False, "error": str(e)}
    )

# ✅ Después (genérico al cliente, loguea en servidor)
except Exception as e:
    import logging
    logging.error(f"Error en login: {str(e)}")
    raise HTTPException(
        status_code=500,
        detail={"success": False, "error": "Error interno del servidor"}
    )
```

**Beneficio:**
- El cliente **nunca** recibe detalles de errores internos
- No expone nombres de tablas, rutas internas, versiones de librerías
- Los errores se loguean en el servidor para debugging
- Mejora profesional de la API

**Ejemplo:**
```
# ❌ Respuesta anterior (expone):
{ "error": "relation 'usuarios' does not exist" }

# ✅ Respuesta ahora:
{ "error": "Error interno del servidor" }
# (El detalle completo está en los logs del servidor)
```

---

### 4. ✅ #8 Lista Blanca de Estados en Pedidos

**Ubicación:** `backend/api_python/api/routers/admin.py` (líneas ~17 y ~35-41)

**Cambio realizado:**
```python
# ❌ Antes (acepta cualquier string)
from typing import Optional
from pydantic import BaseModel

class UpdateOrderStatusIn(BaseModel):
    estado: str  # ← Acepta "hackeado", "xyz", lo que sea

class UpdatePaymentStatusIn(BaseModel):
    estado_pago: str  # ← Acepta cualquier valor

# ✅ Después (solo valores permitidos)
from typing import Optional, Literal
from pydantic import BaseModel

class UpdateOrderStatusIn(BaseModel):
    estado: Literal["pendiente", "en_proceso", "listo", "entregado", "cancelado"]

class UpdatePaymentStatusIn(BaseModel):
    estado_pago: Literal["pendiente", "aprobado", "rechazado", "reembolsado"]
```

**Beneficio:**
- Pydantic valida automáticamente antes de procesar
- Solo acepta estados válidos del sistema
- Rechaza automáticamente valores inválidos (400 Bad Request)
- Protege integridad de datos en la base de datos
- Mejora documentación automática en `/docs`

**Ejemplo:**
```bash
# ❌ Antes: Aceptaba
{ "estado": "hackeado" }  # Se guardaba en DB

# ✅ Ahora: Rechaza con 422
{ "detail": [{ "msg": "Input should be 'pendiente', 'en_proceso', 'listo', 'entregado' or 'cancelado'" }] }
```

**Verificación:**
```bash
curl -X PUT http://localhost:8000/api/admin/pedidos/123/estado \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"estado": "estado_invalido"}'
# Respuesta: 422 Unprocessable Entity
```

---

## ⏳ Cambios Pendientes (Para Producción)

Estos cambios aplican cuando se pase a un entorno real. No son prioritarios en desarrollo local.

### 1. 🟡 #1 Remover `.env` del Repositorio

**Prioridad:** CRÍTICA en producción  
**Ubicación:** `.gitignore` + variables de entorno del servidor

**Pasos a seguir cuando pase a producción:**

1. **Crear `.env.example` (template):**
```bash
# .env.example
VITE_API_URL=http://localhost:8000
FASTAPI_HOST=127.0.0.1
FASTAPI_PORT=8000
NODE_HOST=127.0.0.1
NODE_PORT=3000
PG_HOST=tu_host_postgresql
PG_PORT=5432
PG_DB=tu_database_name
PG_USER=tu_usuario
PG_PASSWORD=<REEMPLAZAR_EN_PRODUCCION>
JWT_SECRET=<REEMPLAZAR_EN_PRODUCCION_CON_VALOR_ALEATORIO>
OLLAMA_API_URL=http://localhost:11434
REPLICATE_API_TOKEN=<REEMPLAZAR_EN_PRODUCCION>
REMOVE_BG_API_KEY=<REEMPLAZAR_EN_PRODUCCION>
MERCADOPAGO_ACCESS_TOKEN=<REEMPLAZAR_EN_PRODUCCION>
```

2. **Verificar `.gitignore` tiene `.env`:**
```bash
# .gitignore ya incluye:
.env
```

3. **En servidor de producción, cargar variables de:**
   - AWS Secrets Manager (si es AWS)
   - Vault (si es HashiCorp)
   - Variables de entorno del SO
   - Gestor de configuración del hosting (Vercel, Heroku, etc.)

**Comando para generar JWT_SECRET seguro:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
# Ejemplo: 7f8d3a9c2e5b1f6d4a9e3c7b2f5d8a1c9e3f6b2d5a8c1e4f7b0d3a6c9f2e5
```

---

### 2. 🟡 #3 Rate Limiting en Login

**Prioridad:** MEDIA en producción  
**Ubicación:** `backend/api_python/api/routers/auth.py`

**Pasos a seguir:**

1. **Instalar `slowapi` (wrapper de FastAPI):**
```bash
cd backend/api_python
pip install slowapi
pip freeze > requirements.txt
```

2. **Implementar en `auth.py`:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("10/minute")  # 10 intentos por minuto por IP
async def login(request: Request, payload: LoginIn):
    """Login: devuelve datos de usuario + JWT"""
    # ... resto del código
```

3. **También en `app_v2.py` añadir manejador:**
```python
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"success": False, "error": "Demasiados intentos. Intente más tarde."}
    )
```

---

### 3. 🟡 #5 Validación de Archivos por Magic Bytes

**Prioridad:** MEDIA en producción  
**Ubicación:** `backend/api_python/api/routers/disenos.py`

**Pasos a seguir:**

1. **Instalar `python-magic` o `python-magic-bin`:**
```bash
cd backend/api_python
pip install python-magic-bin  # Windows
# o: pip install python-magic  # Linux/Mac
pip freeze > requirements.txt
```

2. **Reemplazar validación en `disenos.py`:**
```python
import magic  # Nuevo

@router.post("/upload-design")
async def upload_design(
    file: UploadFile,
    user_id: int,
    user: dict = Depends(get_current_user),
):
    """Subir un archivo de diseño personalizado"""
    try:
        # ❌ Antes (solo Content-Type)
        # if not file.content_type.startswith("image/"):
        #     raise HTTPException(400, {"success": False, "error": "Solo se permiten imágenes"})

        # ✅ Después (magic bytes)
        contents = await file.read()
        
        real_mime = magic.from_buffer(contents, mime=True)
        allowed_mimes = {"image/jpeg", "image/png", "image/webp", "image/gif"}
        
        if real_mime not in allowed_mimes:
            raise HTTPException(
                400, 
                {"success": False, "error": f"Tipo de archivo no permitido. Se detectó: {real_mime}"}
            )
        
        # ... resto del código
```

---

### 4. 🟡 #7 Autenticación en Agentes IA

**Prioridad:** BAJA en producción (si agentes están en mismo servidor)  
**ALTA si están en servidores diferentes  
**Ubicación:** Agentes en `agentes-Ollama/`

**Pasos a seguir (solo si agentes en servidores distintos):**

1. **En agentes, validar `X-API-Key`:**

**Agente Prompts (`agente-prompts/agente_prompts.py`):**
```python
from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)
AGENT_API_KEY = os.getenv("AGENT_API_KEY", "")

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != AGENT_API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route("/optimizar-prompt", methods=["POST"])
@require_api_key
def optimizar_prompt():
    # ... código original
```

2. **En backend principal, enviar API key:**
```python
# backend/api_python/api/dependencies.py
AGENT_API_KEY = os.getenv("AGENT_API_KEY", "")

def call_agente_prompts(descripcion: str) -> str:
    """Llamar al agente con autenticación"""
    response = requests.post(
        "http://localhost:5004/optimizar-prompt",
        json={"descripcion": descripcion},
        headers={"X-API-Key": AGENT_API_KEY},
        timeout=30
    )
    return response.json()["prompt"]
```

3. **Configurar en `.env`:**
```env
AGENT_API_KEY=<generar_con> python -c "import secrets; print(secrets.token_hex(16))"
```

---

## 📋 Checklist de Seguridad Implementada

- [x] **#6** CORS consistente en Node.js
- [x] **#2** JWT_SECRET validación fuerte (fail fast)
- [x] **#4** Errores genéricos en respuestas (no expone detalles internos)
- [x] **#8** Lista blanca de estados (Literal en Pydantic)
- [ ] **#1** Remover `.env` del repo (en producción)
- [ ] **#3** Rate limiting en login (en producción)
- [ ] **#5** Magic bytes en upload de imágenes (en producción)
- [ ] **#7** API keys en agentes IA (si están separados)

---

## 🧪 Testing de Cambios Implementados

### Test #6 — CORS Node.js
```bash
# Debería funcionar (mismo origen)
curl -X POST http://localhost:3000/generar-imagen \
  -H "Origin: http://localhost:5173" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}'
# Respuesta: 200 OK

# Debería fallar (origen no permitido)
curl -X POST http://localhost:3000/generar-imagen \
  -H "Origin: http://malicious.com" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}'
# Respuesta: CORS error o 403
```

### Test #2 — JWT_SECRET
```bash
# Si JWT_SECRET falta de .env:
cd backend/api_python
.venv\Scripts\activate
uvicorn app_v2:app --port 8000

# Debe mostrar:
# RuntimeError: JWT_SECRET no configurado o muy débil...
# (servidor no inicia)
```

### Test #4 — Errores Genéricos
```bash
# Provocar un error en login sin sqlite:
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "test"}'

# Respuesta (antes):
# {"success": false, "error": "table 'usuarios' does not exist"}

# Respuesta (después):
# {"success": false, "error": "Error interno del servidor"}
# (Detalles en logs del servidor)
```

### Test #8 — Lista Blanca Estados
```bash
# Estado válido
curl -X PUT http://localhost:8000/api/admin/pedidos/1/estado \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"estado": "en_proceso"}'
# Respuesta: 200 OK

# Estado inválido
curl -X PUT http://localhost:8000/api/admin/pedidos/1/estado \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"estado": "hackeado"}'
# Respuesta: 422 Unprocessable Entity
```

---

## 📚 Referencias

- [OWASP — API Security Top 10](https://owasp.org/API-Security/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [slowapi rate limiting](https://github.com/laurentS/slowapi)
- [python-magic](https://github.com/ahupp/python-magic)
- [Pydantic Validation](https://docs.pydantic.dev/latest/api/validators/)

---

**Última actualización:** 4 de mayo de 2026  
**Estado:** Cambios implementados y documentados ✅
