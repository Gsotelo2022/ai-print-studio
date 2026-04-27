# 🎁 Agente de Descuentos - Prendete Rock

Sistema híbrido inteligente para gestión de descuentos y cupones.

## 📋 Características

- ✅ Descuentos por cantidad (automático)
- ✅ Descuentos por fidelidad de cliente
- ✅ Cupones con validación
- ✅ Promociones temporales
- ✅ Combinación inteligente de descuentos
- ✅ Límite máximo de descuento (35%)

## 🚀 Instalación

### 1. Crear tablas en SQL Server

```bash
# Ejecutar el script SQL en SQL Server Management Studio
# o vía sqlcmd:
sqlcmd -S .\SQLEXPRESS01 -d PrendeteRock -i crear_tablas_descuentos.sql
```

### 2. Instalar dependencias

```bash
cd agentes-Ollama\agente_descuentos
..\..\.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Iniciar el servicio

```bash
# Opción 1: Script batch (Windows)
start-agente-descuentos.bat

# Opción 2: Comando directo
uvicorn api_descuentos:app --host 0.0.0.0 --port 5002 --reload
```

## 📡 API Endpoints

### Base URL
```
http://localhost:5002
```

### 1. Calcular Descuento
**POST** `/calcular-descuento`

Calcula el descuento total aplicable a un pedido.

**Request:**
```json
{
  "id_cliente": 1,
  "cantidad": 5,
  "total": 60000,
  "productos": [],
  "cupon": "PRIMERACOMPRA10"
}
```

**Response:**
```json
{
  "success": true,
  "descuento_total": 20.0,
  "descuentos_aplicados": [
    {
      "tipo": "cantidad",
      "nombre": "5-9 productos",
      "porcentaje": 10
    },
    {
      "tipo": "cupon",
      "nombre": "Cupón: PRIMERACOMPRA10",
      "porcentaje": 10
    }
  ],
  "precio_original": 60000.0,
  "precio_final": 48000.0,
  "ahorro": 12000.0
}
```

### 2. Validar Cupón
**POST** `/validar-cupon`

Verifica si un cupón es válido sin aplicarlo.

**Request:**
```json
{
  "codigo": "PRIMERACOMPRA10"
}
```

**Response:**
```json
{
  "valido": true,
  "codigo": "PRIMERACOMPRA10",
  "descuento": 10.0,
  "descripcion": "Descuento para primera compra",
  "usos_restantes": null
}
```

### 3. Descuentos Activos
**GET** `/descuentos-activos`

Lista todos los descuentos activos.

**Response:**
```json
{
  "descuentos": [
    {
      "tipo": "temporal",
      "nombre": "Black Friday 2024",
      "descripcion": "Descuento especial Black Friday",
      "porcentaje": 25.0
    },
    {
      "tipo": "cantidad",
      "nombre": "Descuento por cantidad",
      "descripcion": "5% (2-4), 10% (5-9), 15% (10+)",
      "permanente": true
    }
  ],
  "total": 2
}
```

### 4. Health Check
**GET** `/health`

Verifica el estado del servicio.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "servicio": "activo"
}
```

## 📊 Reglas de Descuentos

### Descuentos por Cantidad (Automáticos)
- **2-4 productos**: 5% descuento
- **5-9 productos**: 10% descuento
- **10+ productos**: 15% descuento

### Descuentos por Cliente
- **Primera compra**: 10% descuento
- **Cliente frecuente** (3+ compras): 5% descuento
- **Cliente VIP** (10+ compras): 12% descuento

### Cupones Predefinidos
- `PRIMERACOMPRA10`: 10% primera compra (ilimitado)
- `AMIGOS15`: 15% por referido (100 usos)
- `VERANO2024`: 20% temporada verano
- `NAVIDAD2024`: 18% especial navidad
- `VIP25`: 25% exclusivo VIP (20 usos)

### Lógica de Combinación
1. **Con cupón**: Se toma el mayor entre cupón y suma de otros descuentos
2. **Sin cupón**: Se suman todos los descuentos aplicables
3. **Máximo permitido**: 35% descuento total

## 🧪 Testing

### Probar con curl

```bash
# Calcular descuento
curl -X POST http://localhost:5002/calcular-descuento \
  -H "Content-Type: application/json" \
  -d "{\"id_cliente\": 1, \"cantidad\": 5, \"total\": 60000, \"cupon\": \"PRIMERACOMPRA10\"}"

# Validar cupón
curl -X POST http://localhost:5002/validar-cupon \
  -H "Content-Type: application/json" \
  -d "{\"codigo\": \"PRIMERACOMPRA10\"}"

# Descuentos activos
curl http://localhost:5002/descuentos-activos

# Health check
curl http://localhost:5002/health
```

### Probar con Python

```python
import requests

# Calcular descuento
response = requests.post('http://localhost:5002/calcular-descuento', json={
    'id_cliente': 1,
    'cantidad': 5,
    'total': 60000,
    'cupon': 'PRIMERACOMPRA10'
})
print(response.json())
```

## 🔧 Integración con Frontend

### Vue.js Example

```javascript
// En PreviewPanel.vue o CheckoutPanel.vue
async function aplicarDescuento() {
  const response = await fetch('http://localhost:5002/calcular-descuento', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      id_cliente: userId,
      cantidad: cantidadProductos,
      total: precioTotal,
      cupon: cuponIngresado || null
    })
  })
  
  const descuento = await response.json()
  
  if (descuento.success) {
    precioFinal.value = descuento.precio_final
    descuentosAplicados.value = descuento.descuentos_aplicados
    ahorroTotal.value = descuento.ahorro
  }
}
```

## 📁 Estructura de Archivos

```
agente_descuentos/
├── agente_descuentos.py          # Lógica del agente
├── api_descuentos.py             # FastAPI endpoints
├── crear_tablas_descuentos.sql  # Script SQL de instalación
├── requirements.txt              # Dependencias
├── start-agente-descuentos.bat  # Script de inicio
├── test_agente.py               # Tests
└── README.md                     # Documentación
```

## 🔐 Seguridad

- ✅ Validación de cupones con límite de usos
- ✅ Verificación de fechas de expiración
- ✅ Límite máximo de descuento (35%)
- ✅ Auditoría de uso de cupones
- ✅ Protección contra descuentos duplicados

## 🐛 Troubleshooting

### Error: "No se puede conectar a la base de datos"
- Verificar que SQL Server SQLEXPRESS01 está corriendo
- Verificar credenciales en `agente_descuentos.py`
- Ejecutar: `Get-Service MSSQL*` en PowerShell

### Error: "Puerto 5002 en uso"
- Cambiar el puerto en `start-agente-descuentos.bat`
- O matar el proceso: `netstat -ano | findstr 5002`

### Error: "Tabla no existe"
- Ejecutar el script SQL: `crear_tablas_descuentos.sql`
- Verificar base de datos PrendeteRock existe

## 📈 Próximas Mejoras

- [ ] Integración con Ollama para validaciones complejas
- [ ] Dashboard de administración de descuentos
- [ ] Analytics de uso de cupones
- [ ] Descuentos por categoría de producto
- [ ] Sistema de puntos y recompensas
- [ ] Notificaciones de descuentos vía email

## 📞 Soporte

Para más información, consulta la documentación interactiva:
- **Swagger UI**: http://localhost:5002/docs
- **ReDoc**: http://localhost:5002/redoc

---
**Versión**: 1.0.0  
**Autor**: AI Print Studio Team  
**Última actualización**: 2024
