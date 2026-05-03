# Correcciones aplicadas — Migración SQL Server → PostgreSQL

## Resumen de cambios

### 1. `backend/api_python/requirements.txt`
- ❌ Eliminado `pyodbc==5.3.0` (driver SQL Server — incompatible con PostgreSQL)
- ✅ Mantenido `psycopg2-binary>=2.9.9` (driver PostgreSQL)
- ✅ Agregado `requests>=2.31.0` (faltaba para el router admin)

### 2. `backend/api_python/app.py`
- ❌ **DEPRECADO** — tenía toda la lógica con placeholders `?` (SQL Server)
- ✅ Ahora redirige al archivo activo: `app_v2.py`
- 🚀 **Iniciar servidor**: `uvicorn app_v2:app --host 0.0.0.0 --port 8000 --reload`

### 3. `backend/api_python/api/routers/auth.py`
- ✅ Ya estaba correctamente migrado (usa `%s` y tablas en minúscula)

### 4. `backend/api_python/api/routers/pedidos.py`
- ✅ `FROM Usuarios` → `FROM usuarios`
- ✅ `activo = TRUE` → `activo = true`
- ✅ `pi.id_diseno = ad.id_diseno` → `pi.archivo_diseno = ad.id_archivo` (nombre de columna correcto)

### 5. `backend/api_python/api/routers/productos.py`
- ✅ `activo = TRUE` → `activo = true` (en las 3 queries)

### 6. `backend/api_python/api/routers/cupones.py`
- ✅ `activo = TRUE` → `activo = true`

### 7. `backend/api_python/api/routers/admin.py`
- ✅ `pedidos_Items` → `pedidos_items` (PostgreSQL es case-sensitive)
- ✅ `Producto_Variantes`, `Productos`, `Pedidos`, `Usuarios` → todos en minúscula
- ✅ `activo = TRUE` → `activo = true`
- ✅ `u.Nombre LIKE` → `u.nombre ILIKE` (ILIKE para búsqueda case-insensitive en PostgreSQL)
- ✅ `u.Email`, `u.Tipo`, `u.Nombre` → `u.email`, `u.tipo`, `u.nombre` en todas las queries
- ✅ Subconsultas de clientes y dashboard corregidas

### 8. Todos los routers — Nombres de tablas
Todas las tablas ahora en minúscula según el schema PostgreSQL:
- `Productos` → `productos`
- `Usuarios` → `usuarios`
- `Pedidos` → `pedidos`
- `Pedidos_Items` → `pedidos_items`
- `Producto_Variantes` → `producto_variantes`
- `Producto_Atributos` → `producto_atributos`
- `Producto_Atributo_Valores` → `producto_atributo_valores`
- `Variante_Atributos` → `variante_atributos`
- `Archivos_Diseno` → `archivos_diseno`
- `Cupones` → `cupones`
- `Pagos` → `pagos`

### 9. `frontend/src/composables/useApi.js`
- ✅ `uploadDesign()` corregido: `user_id` ahora se envía como query param (`?user_id=X`)
  en lugar de como campo de FormData, ya que el backend FastAPI lo espera como parámetro de URL.

### 10. `agentes-Ollama/agente-cupones/agente_descuentos.py`
- ✅ `import pyodbc` → `import psycopg2, os`
- ✅ Conexión `pyodbc.connect(DRIVER=...)` → `psycopg2.connect(host=..., port=..., ...)`
- ✅ Placeholders `?` → `%s`
- ✅ `GETDATE()` → `NOW()`
- ✅ `activo = 0/1` → `activo = TRUE/FALSE`

### 11. `agentes-Ollama/agente-precios/agente_precios.py`
- ✅ `import pyodbc` → `import psycopg2, os`
- ✅ Conexión SQL Server → PostgreSQL
- ✅ Placeholders `?` → `%s`
- ✅ Funciones SQL Server: `GETDATE()→NOW()`, `ISNULL()→COALESCE()`, `@@IDENTITY→lastval()`

### 12. `agentes-Ollama/agente-productos/agente_productos.py`
- ✅ Mismas correcciones que los otros agentes

### 13. `agentes-Ollama/agente-cupones/requirements.txt`
- ✅ Reemplazado `pyodbc` con `psycopg2-binary`

### 14. `agentes-Ollama/agente-precios/requirements.txt`
- ✅ Creado desde cero con dependencias correctas para PostgreSQL

## Cómo iniciar el proyecto

```bash
# Backend
cd backend/api_python
pip install -r requirements.txt
uvicorn app_v2:app --host 0.0.0.0 --port 8000 --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Variables de entorno requeridas (`.env`)
```
PG_HOST=127.0.0.1
PG_PORT=5432
PG_DB=PrendeteRock
PG_USER=postgres
PG_PASSWORD=tu_password
JWT_SECRET=un_secreto_seguro
OPENAI_API_KEY=sk-...           # Para generación de imágenes
MERCADOPAGO_ACCESS_TOKEN=...    # Para pagos
```
