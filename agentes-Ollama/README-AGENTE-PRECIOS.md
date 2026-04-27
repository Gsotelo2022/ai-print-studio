# 🤖 Agente IA - Actualización de Precios

Agente inteligente que actualiza precios de productos usando OLLAMA para procesar lenguaje natural.

## 🚀 Inicio Rápido

### Windows (Batch)
```bash
cd agentes-Ollama
start-agente-precios.bat
```

### Windows (PowerShell)
```bash
cd agentes-Ollama
.\start-agente-precios.ps1
```

### Manual
```bash
cd agentes-Ollama
.venv\Scripts\activate
python agente_precios.py
```

## 📡 Endpoints

### POST /actualizar-precio

Actualiza el precio de todas las variantes de un producto.

**Formato 1: Lenguaje Natural**
```json
{
  "consulta": "cambiar el precio del buzo a 15000"
}
```

**Formato 2: Parámetros Directos**
```json
{
  "detalle": "Buzo",
  "precio": 15000,
  "nuevo_detalle": "Sudadera" 
}
```

**Respuesta exitosa:**
```json
{
  "message": "Precio actualizado correctamente para 4 variante(s)",
  "detalle": "Buzo",
  "precio_anterior": 12000,
  "precio_nuevo": 15000,
  "variantes_actualizadas": 4
}
```

### GET /health

Verifica el estado del agente.

```json
{
  "status": "ok",
  "servicio": "Agente de Actualización de Precios",
  "modelo": "qwen2.5:1.5b"
}
```

## 🔧 Funcionamiento

1. **Recibe la consulta** (lenguaje natural o parámetros)
2. **Usa OLLAMA** para entender la intención (opcional)
3. **Valida** que el producto existe
4. **Actualiza** todas las variantes en la BD
5. **Retorna** confirmación con detalles

## 📊 Ejemplos de Consultas

### Cambiar solo el precio
```
"cambiar el precio del buzo a 15000"
"actualizar remera a 8500"
"poner la gorra en 5000"
```

### Cambiar precio y nombre
```
"cambiar buzo por sudadera y precio 12000"
"renombrar remera a camiseta con precio 7500"
```

## 🎯 Integración con Frontend

El frontend (GestionProductos.vue) ya está configurado para usar este agente:

```javascript
// Llamada al agente con lenguaje natural
const response = await fetch('http://localhost:5002/actualizar-precio', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    consulta: "cambiar precio del buzo a 15000" 
  })
})
```

## 🗄️ Base de Datos

El agente actualiza la tabla `Productos` en SQL Server:

```sql
UPDATE Productos 
SET precio = 15000 
WHERE Detalle = 'Buzo'
```

**Nota importante:** 
- Un producto puede tener múltiples variantes (talle + color)
- El agente actualiza TODAS las variantes del producto
- Por ejemplo, "Buzo" puede tener: S/Negro, M/Negro, L/Rojo, XL/Azul
- Al cambiar el precio del "Buzo", se actualizan las 4 variantes

## 🔗 Servicios Relacionados

- **Puerto 5001**: Agente de productos (catálogo)
- **Puerto 5002**: Agente de precios (actualización)
- **Puerto 8000**: FastAPI (backend principal)
- **Puerto 8080**: PHP (API legacy)
- **Puerto 11434**: OLLAMA (modelo IA)

## 🐛 Troubleshooting

### Error: "No se puede conectar a OLLAMA"
```bash
# Iniciar OLLAMA
ollama serve

# Verificar que está corriendo
curl http://localhost:11434
```

### Error: "No se encontró el producto"
- Verifica que el nombre del producto exista en la BD
- Los nombres son case-sensitive
- Usa el nombre exacto como aparece en `Productos.Detalle`

### Error: Connection refused (puerto 5002)
```bash
# Verificar que el agente esté corriendo
curl http://localhost:5002/health
```

## 📝 Logs

El agente muestra logs detallados en consola:

```
========================================
[REQUEST] /actualizar-precio
[CONSULTA] 'cambiar el precio del buzo a 15000'
[IA] Construyendo prompt...
[IA] Llamando OLLAMA (qwen2.5:1.5b)...
[IA] ✓ Info extraída: {"producto": "Buzo", "precio": 15000}
[DEBUG] Llamando a FastAPI...
[SUCCESS] ✓ Precio actualizado correctamente
```

## 🎓 Arquitectura

```
Frontend (Vue)
    ↓ POST /actualizar-precio
Agente Precios (Flask:5002)
    ↓ Procesa con OLLAMA
    ↓ PUT /api/admin/productos/detalle/{detalle}/precio  
FastAPI (Python:8000)
    ↓ UPDATE Productos SET precio = ?
SQL Server (PrendeteRock)
```

## ⚙️ Configuración

Edita las variables en `agente_precios.py`:

```python
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:1.5b"
FASTAPI_URL = "http://localhost:8000/api"
```
