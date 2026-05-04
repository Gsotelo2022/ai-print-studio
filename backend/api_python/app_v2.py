import os
import logging
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Routers
from api.routers.auth      import router as auth_router
from api.routers.productos import router as productos_router
from api.routers.cupones   import router as cupones_router
from api.routers.pedidos   import router as pedidos_router
from api.routers.disenos   import router as disenos_router
from api.routers.admin     import router as admin_router

app = FastAPI(
    title="AI Print Studio API",
    version="2.1.0",
)

# CORS
_raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
ALLOWED_ORIGINS = [o.strip() for o in _raw.split(",") if o.strip()]

print("ALLOWED_ORIGINS:", ALLOWED_ORIGINS)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
BASE_DIR = Path(__file__).resolve().parent.parent
IMAGENES_IA_DIR = BASE_DIR / "api" / "imagenes-generadas-con-IA"
IMAGENES_IA_DIR.mkdir(parents=True, exist_ok=True)

UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/imagenes", StaticFiles(directory=str(IMAGENES_IA_DIR)), name="imagenes")
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# HTTP Errors
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": str(exc.detail)},
    )

# 🔥 Global Errors
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("ERROR NO CONTROLADO", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Error interno del servidor",
            "detail": str(exc)
        },
    )

# Health
@app.get("/api/health", tags=["util"])
def health():
    return {"success": True, "status": "ok", "version": "2.1.0"}

# Routers
app.include_router(auth_router)
app.include_router(productos_router)
app.include_router(cupones_router)
app.include_router(pedidos_router)
app.include_router(disenos_router)
app.include_router(admin_router)