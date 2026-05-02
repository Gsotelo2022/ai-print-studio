"""
AI Print Studio — FastAPI v2 (orquestrador delgado)
====================================================
Este archivo sólo configura la app, el middleware y registra los routers.
Toda la lógica de negocio está en api/routers/*.py
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# Cargar variables de entorno desde .env (si existe)
load_dotenv()

# ── Routers ─────────────────────────────────────────────────
from api.routers.auth      import router as auth_router
from api.routers.productos import router as productos_router
from api.routers.cupones   import router as cupones_router
from api.routers.pedidos   import router as pedidos_router
from api.routers.disenos   import router as disenos_router
from api.routers.admin     import router as admin_router

# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="AI Print Studio API",
    version="2.1.0",
    description="Backend principal de AI Print Studio",
)

# ── CORS ─────────────────────────────────────────────────────
_raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
ALLOWED_ORIGINS = [o.strip() for o in _raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Archivos estáticos (imágenes IA) ─────────────────────────
BASE_DIR        = Path(__file__).resolve().parent.parent
IMAGENES_IA_DIR = BASE_DIR / "api" / "imagenes-generadas-con-IA"
IMAGENES_IA_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/imagenes", StaticFiles(directory=str(IMAGENES_IA_DIR)), name="imagenes")

# ── Manejador de errores HTTP ─────────────────────────────────

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": str(exc.detail)},
    )

# ── Health check ─────────────────────────────────────────────

@app.get("/api/health", tags=["util"])
def health():
    return {"success": True, "status": "ok", "version": "2.1.0"}

# ── Registrar routers ────────────────────────────────────────

app.include_router(auth_router)
app.include_router(productos_router)
app.include_router(cupones_router)
app.include_router(pedidos_router)
app.include_router(disenos_router)
app.include_router(admin_router)
