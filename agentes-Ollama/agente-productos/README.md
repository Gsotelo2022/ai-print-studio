# 🎨 Agente de Productos - Catálogo Dinámico con IA

Agente inteligente que proporciona un catálogo dinámico de productos utilizando OLLAMA (modelo de lenguaje local).

## 🚀 Inicio Rápido

### Windows (Batch)
```bash
cd agentes-Ollama\agente-productos
start-agente-productos.bat
```

### Manual
```bash
cd agentes-Ollama\agente-productos
python agente_productos.py
```

## 📋 Características

- 📦 Carga productos directamente desde SQL Server
- 🤖 Procesa y agrupa con OLLAMA (qwen2.5:1.5b)
- 🔄 Fallback automático si OLLAMA falla
- ⚡ Endpoint REST para frontend
- 🎯 Agrupa por producto, talles y colores
- 📊 Procesa TODOS los productos (sin límite)

## 📡 API Endpoints

### Base URL
```
http://localhost:5001
```

### GET /productos-ia

Retorna catálogo completo de productos agrupados y estructurados.

**Respuesta (Ejemplo con productos reales):**
```json
[
  {
    "id_producto": 1,
    "producto": "Buzo",
    "talles": ["S", "M", "L", "X", "XL", "XXL"],
    "colores": ["Blanca", "Negra", "Roja", "Azul"],
    "precio": 12000,
    "variantes": [
      {
        "id_variante": 1,
        "talle": "S",
        "color": "Negra",
        "precio": 12000,
        "stock": 50
      }
    ]
  },
  {
    "id_producto": 2,
    "producto": "Remera",
    "talles": ["S", "M", "L", "XL"],
    "colores": ["Blanco", "Negro", "Rojo"],
    "precio": 8000,
    "variantes": [...]
  },
  {
    "id_producto": 3,
    "producto": "Taza",
    "talles": [],
    "colores": ["Blanco", "Negro"],
    "precio": 5000,
    "variantes": [...]
  }
]
```

**Tiempo de respuesta:**
- Con 10 productos: ~15-30 segundos
- Con 20 productos: ~30-45 segundos
- Con 50 productos: ~45-60 segundos
- Con 85 productos: ~60-90 segundos (puede usar fallback)

### GET /health

Verifica el estado del agente.

**Respuesta:**
```json
{
  "status": "ok",
  "servicio": "Agente de Productos",
  "modelo": "qwen2.5:1.5b",
  "fallback": "disponible"
}
```

## 🔧 Funcionamiento

### Flujo Completo: BD → OLLAMA → Frontend

```
┌─────────────────────────────────────────────────────────────┐
│                  CIRCUITO DEL AGENTE IA                     │
└─────────────────────────────────────────────────────────────┘

1. CONSULTA A BACKEND (FastAPI)
   └─→ GET http://localhost:8000/api/productos
   └─→ Obtiene productos con variantes desde SQL Server

2. FALLBACK DIRECTO (MODO ACTUAL)
   └─→ Ya viene agrupado del backend
   └─→ Simplemente retorna la estructura

3. LLAMADA A OLLAMA (OPCIONAL - Deshabilitado por defecto)
   └─→ POST http://localhost:11434/api/generate
   └─→ Model: qwen2.5:1.5b
   └─→ Timeout: 60 segundos
   └─→ OLLAMA procesa y agrupa inteligentemente

4. PARSEO DE RESPUESTA
   └─→ Extrae JSON de respuesta OLLAMA
   └─→ Limpia markdown, code blocks, etc.
   └─→ Valida estructura del JSON

5. FALLBACK (si necesario)
   └─→ Si OLLAMA timeout o error:
   └─→ Usa agrupamiento Python directo
   └─→ Garantiza disponibilidad 100%

6. RESPUESTA AL FRONTEND
   └─→ JSON estructurado listo para renderizar

7. FRONTEND RENDERIZA
   └─→ ProductSelector.vue muestra opciones dinámicas
   └─→ Usuario selecciona producto, talle y color
   └─→ Opciones siempre actualizadas desde BD
```

## 🎯 Integración con Frontend

El frontend (App.vue) carga productos del agente al iniciar:

```javascript
async function cargarProductosDelAgente() {
  try {
    const response = await fetch('http://localhost:5001/productos-ia')
    const data = await response.json()
    
    // Transforma a formato del frontend
    data.forEach(item => {
      const key = item.producto.toLowerCase()
      productos[key] = {
        id_producto: item.id_producto,
        nombre: item.producto,
        talles: item.talles,
        colores: item.colores,
        variantes: item.variantes,
        precio: item.precio
      }
    })
    
    console.log('✅ Productos cargados del agente IA')
  } catch (error) {
    console.warn('⚠️ Agente IA no disponible, usando lista estática')
    // Fallback a lista hardcoded
  }
}
```

## 🗄️ Base de Datos

El agente consulta al backend FastAPI que se conecta a SQL Server:

```sql
-- El backend ejecuta:
SELECT 
  p.id_producto,
  p.Detalle as nombre,
  pv.id_variante,
  pv.atributos,
  pv.precio,
  pv.stock
FROM Productos p
LEFT JOIN Producto_Variantes pv ON p.id_producto = pv.id_producto
WHERE pv.activo = 1
```

## ⚙️ Configuración

### Variables en agente_productos.py:

```python
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:1.5b"
LIMITE_PRODUCTOS = None  # None = todos los productos
```

## 🧪 Testing

### Probar con curl

```bash
# Obtener catálogo completo
curl http://localhost:5001/productos-ia

# Health check
curl http://localhost:5001/health
```

### Probar con Python

```python
import requests

response = requests.get('http://localhost:5001/productos-ia')
productos = response.json()

print(f"Total productos: {len(productos)}")
for p in productos:
    print(f"- {p['producto']}: {len(p['talles'])} talles, {len(p['colores'])} colores")
```

## 🐛 Troubleshooting

### Error: "No se puede conectar al backend"
```bash
# Verificar que FastAPI esté corriendo
curl http://localhost:8000/api/productos
```

### Error: Connection refused (puerto 5001)
```bash
# Verificar que el agente esté corriendo
curl http://localhost:5001/health
```

### Error: OLLAMA timeout
- El agente automáticamente usa fallback Python
- No afecta la disponibilidad del servicio
- Los productos se retornan igualmente

## 📝 Logs

El agente muestra logs detallados en consola:

```
[DEBUG] Conectando al backend...
[API] ✓ Respuesta recibida del backend
[API] Obtenidos 85 productos con variantes
[DEBUG] Generando catálogo...
[API] ✓ Retornando 85 productos agrupados
[SERVER] Servicio iniciado en http://0.0.0.0:5001
```

## 🎓 Arquitectura

```
Frontend (Vue:5174)
    ↓ GET /productos-ia
Agente Productos (Flask:5001)
    ↓ GET /api/productos
FastAPI (Python:8000)
    ↓ SELECT FROM Productos + Producto_Variantes
SQL Server (PrendeteRock)
```

## 🔗 Servicios Relacionados

- **Puerto 5001**: Agente de productos (catálogo) ← Este servicio
- **Puerto 5002**: Agente de precios (actualización)
- **Puerto 5003**: Agente de cupones (descuentos)
- **Puerto 8000**: FastAPI (backend principal)
- **Puerto 5174**: Vue + Vite (frontend)
- **Puerto 11434**: OLLAMA (modelo IA)

## 📦 Requisitos

### OLLAMA (Opcional)
```bash
# Instalar OLLAMA
# https://ollama.com

# Descargar modelo
ollama pull qwen2.5:1.5b

# Iniciar servicio
ollama serve

# Verificar
curl http://localhost:11434
```

### Python
```bash
# Crear entorno virtual
python -m venv .venv

# Activar
.venv\Scripts\activate

# Instalar dependencias
pip install flask flask-cors requests pyodbc
```

## 🆕 Modo de Operación Actual

**IMPORTANTE:** Actualmente el agente opera en **modo fallback directo**:

- ✅ No usa OLLAMA (evita latencia)
- ✅ Consulta directamente al backend FastAPI
- ✅ El backend ya retorna productos agrupados
- ✅ Respuesta instantánea (< 1 segundo)
- ✅ 100% de disponibilidad

Este modo es **más rápido y confiable** que procesar con OLLAMA. El código de OLLAMA se mantiene para uso futuro si se necesita procesamiento de lenguaje natural más avanzado.

## 📊 Comparación de Rendimiento

| Modo | Latencia | Disponibilidad | Uso IA |
|------|----------|----------------|--------|
| **Fallback directo** (actual) | < 1s | 100% | No |
| OLLAMA procesamiento | 60-90s | 90% | Sí |
| Backend directo | < 0.5s | 100% | No |

**Recomendación:** Usar el backend directamente (puerto 8000) en lugar del agente para máxima velocidad. El agente se mantiene para compatibilidad con código legacy.
