from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from agente_descuentos import AgenteDescuentos

app = FastAPI(
    title="Agente de Descuentos - Prendete Rock",
    description="API para gestión inteligente de descuentos",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar agente
agente = AgenteDescuentos()

# ==================== MODELOS ====================

class Pedido(BaseModel):
    id_cliente: int
    id_pedido: Optional[int] = None
    cantidad: int
    total: float
    productos: Optional[List[dict]] = []
    cupon: Optional[str] = None

class ValidarCuponRequest(BaseModel):
    codigo: str

class CrearCuponRequest(BaseModel):
    codigo: str
    descripcion: str
    descuento_porcentaje: float
    usos_maximos: Optional[int] = None
    fecha_expiracion: Optional[str] = None

class ActualizarCuponRequest(BaseModel):
    descripcion: Optional[str] = None
    descuento_porcentaje: Optional[float] = None
    usos_maximos: Optional[int] = None
    fecha_expiracion: Optional[str] = None
    activo: Optional[bool] = None

# ==================== ENDPOINTS ====================

@app.get("/")
def root():
    """Endpoint raíz - información de la API"""
    return {
        "mensaje": "Agente de Descuentos - Prendete Rock",
        "version": "1.0.0",
        "endpoints": {
            "/calcular-descuento": "POST - Calcular descuento para un pedido",
            "/validar-cupon": "POST - Validar un cupón sin aplicarlo",
            "/descuentos-activos": "GET - Listar descuentos activos",
            "/health": "GET - Estado del servicio"
        }
    }

@app.post("/calcular-descuento")
def calcular_descuento(pedido: Pedido):
    """
    Calcular el descuento total aplicable a un pedido
    
    Ejemplo de uso:
    ```json
    {
        "id_cliente": 1,
        "cantidad": 5,
        "total": 60000,
        "productos": [...],
        "cupon": "PRIMERACOMPRA10"
    }
    ```
    """
    try:
        resultado = agente.calcular_descuento(pedido.dict())
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/validar-cupon")
def validar_cupon(request: ValidarCuponRequest):
    """
    Validar si un cupón es válido sin aplicarlo
    
    Retorna información sobre el cupón sin incrementar el contador de usos
    """
    try:
        resultado = agente.validar_cupon_disponible(request.codigo)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/descuentos-activos")
def descuentos_activos():
    """
    Obtener lista de todos los descuentos activos
    
    Incluye descuentos temporales y reglas permanentes
    """
    try:
        descuentos = agente.obtener_descuentos_activos()
        return {
            "descuentos": descuentos,
            "total": len(descuentos)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """Verificar estado del servicio"""
    try:
        # Intentar conectar a la BD
        conn = agente.get_db_connection()
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "servicio": "activo"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }

# ==================== GESTIÓN DE CUPONES ====================

@app.get("/api/cupones")
def listar_cupones(incluir_inactivos: bool = False):
    """
    Listar todos los cupones
    
    Query params:
    - incluir_inactivos: incluir cupones desactivados o expirados
    """
    try:
        cupones = agente.listar_cupones(incluir_inactivos)
        return {
            "success": True,
            "cupones": cupones,
            "total": len(cupones)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cupones")
def crear_cupon(cupon: CrearCuponRequest):
    """
    Crear un nuevo cupón
    
    Ejemplo:
    ```json
    {
        "codigo": "VERANO2026",
        "descripcion": "Descuento de verano",
        "descuento_porcentaje": 20,
        "usos_maximos": 100,
        "fecha_expiracion": "2026-06-30"
    }
    ```
    """
    try:
        resultado = agente.crear_cupon(cupon.dict())
        if resultado['success']:
            return resultado
        else:
            raise HTTPException(status_code=400, detail=resultado['mensaje'])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/cupones/{id_cupon}")
def actualizar_cupon(id_cupon: int, datos: ActualizarCuponRequest):
    """
    Actualizar un cupón existente
    
    Solo se actualizan los campos proporcionados
    """
    try:
        # Filtrar campos None
        datos_dict = {k: v for k, v in datos.dict().items() if v is not None}
        
        resultado = agente.actualizar_cupon(id_cupon, datos_dict)
        if resultado['success']:
            return resultado
        else:
            raise HTTPException(status_code=400, detail=resultado['mensaje'])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/cupones/{id_cupon}")
def eliminar_cupon(id_cupon: int, permanente: bool = False):
    """
    Eliminar un cupón
    
    Por defecto solo lo desactiva (soft delete).
    Con permanente=true lo elimina de la BD.
    """
    try:
        resultado = agente.eliminar_cupon(id_cupon, soft_delete=not permanente)
        if resultado['success']:
            return resultado
        else:
            raise HTTPException(status_code=400, detail=resultado['mensaje'])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANÁLISIS E INTELIGENCIA ====================

@app.get("/api/estadisticas")
def obtener_estadisticas():
    """
    Obtener estadísticas de ventas y cupones para análisis
    """
    try:
        stats = agente.obtener_estadisticas_ventas()
        return {
            "success": True,
            "estadisticas": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cupones/proponer")
def proponer_cupones():
    """
    Usar IA (Ollama) para proponer cupones estratégicos
    
    Analiza datos de ventas, comportamiento de clientes y tendencias
    para sugerir cupones optimizados.
    
    Requiere: Ollama corriendo localmente
    """
    try:
        resultado = agente.proponer_cupones_ia()
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Ejecutar con: uvicorn api_descuentos:app --host 0.0.0.0 --port 5003 --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003)
