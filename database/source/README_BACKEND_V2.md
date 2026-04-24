# 🚀 BACKEND V2 - GUÍA DE USO

> **Archivo:** `database/source/app_v2.py`  
> **Versión:** 2.0.0  
> **Fecha:** 22 de abril de 2026

---

## 📋 CAMBIOS RESPECTO A LA VERSIÓN ANTERIOR

### Antes (app.py)
- ❌ Productos hardcodeados en el código
- ❌ Un pedido = un solo producto
- ❌ Imágenes en base64 en BD
- ❌ Sin sistema de variantes
- ❌ Sin gestión de stock

### Ahora (app_v2.py)
- ✅ Productos dinámicos desde BD
- ✅ Sistema de variantes (Color + Talle + etc.)
- ✅ Pedidos multi-item (carrito completo)
- ✅ Imágenes en filesystem (optimizado)
- ✅ Control de stock automático
- ✅ Métricas y dashboard
- ✅ Auditoría de cambios

---

## 🔧 CÓMO ACTIVAR EL NUEVO BACKEND

### Opción A: Probar en Paralelo (Recomendado)

1. **Mantener backend antiguo en puerto 8000**
2. **Ejecutar nuevo backend en puerto 8001**

```bash
cd C:\projects\ai-print-studio\database\source
python app_v2.py --port 8001
```

3. **Cambiar frontend para apuntar a puerto 8001**

```javascript
// frontend/src/composables/useApi.js
const BASE_URL = 'http://localhost:8001/api'  // Era 8000
```

4. **Probar funcionalidad**
5. **Si todo funciona, reemplazar app.py con app_v2.py**

---

### Opción B: Reemplazo Directo (Rápido)

1. **Backup del backend antiguo**

```bash
cd C:\projects\ai-print-studio\database\source
copy app.py app_backup_old.py
```

2. **Reemplazar con la nueva versión**

```bash
copy app_v2.py app.py
```

3. **Reiniciar servidor FastAPI**

```powershell
# Detener servidor actual (Ctrl+C)
# Reiniciar
python app.py
```

---

## 📚 NUEVOS ENDPOINTS

### 🆕 Productos con Variantes

#### GET `/api/productos`
Obtiene catálogo completo con variantes disponibles.

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id_producto": 1,
      "nombre": "Remera Básica",
      "descripcion": "Remera de algodón 100%...",
      "categoria": "Indumentaria",
      "imagen_mockup": "/assets/mockups/remera.png",
      "area_impresion": {
        "ancho": 800,
        "alto": 1000
      },
      "opciones_atributos": [
        {
          "nombre": "Color",
          "tipo": "select",
          "requerido": true,
          "valores": [
            {"valor": "Negro", "codigo_color": "#000000"},
            {"valor": "Blanco", "codigo_color": "#FFFFFF"}
          ]
        },
        {
          "nombre": "Talle",
          "tipo": "select",
          "requerido": true,
          "valores": [
            {"valor": "M"},
            {"valor": "L"},
            {"valor": "XL"}
          ]
        }
      ],
      "variantes": [
        {
          "id_variante": 1,
          "sku": "REM-NEG-M",
          "precio": 12000,
          "stock": 50,
          "atributos": {
            "color": {"valor": "Negro", "codigo_color": "#000000"},
            "talle": {"valor": "M"}
          }
        }
      ],
      "precio_desde": 12000
    }
  ]
}
```

---

#### GET `/api/variante/{id_variante}`
Obtiene detalles de una variante específica.

**Ejemplo:**
```bash
GET /api/variante/1
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "id_variante": 1,
    "sku": "REM-NEG-M",
    "precio": 12000,
    "stock": 50,
    "producto_nombre": "Remera Básica",
    "descripcion": "Remera de algodón 100% ideal para...",
    "imagen_mockup": "/assets/mockups/remera.png",
    "atributos": {
      "color": {"valor": "Negro", "codigo_color": "#000000"},
      "talle": {"valor": "M"}
    }
  }
}
```

---

### 🆕 Upload de Diseños

#### POST `/api/upload-design`
Sube una imagen de diseño personalizada.

**Parámetros:**
- `file`: Archivo de imagen (multipart/form-data)
- `user_id`: ID del usuario

**Ejemplo con JavaScript:**
```javascript
const formData = new FormData()
formData.append('file', imageFile)
formData.append('user_id', userId)

const response = await fetch('http://localhost:8000/api/upload-design', {
  method: 'POST',
  body: formData
})

const data = await response.json()
// data.data.id_archivo → Usar en create-order
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "id_archivo": 123,
    "nombre": "user1_20260422_143025_abc123.png",
    "ruta": "uploads/designs/user1_20260422_143025_abc123.png",
    "thumbnail": "uploads/thumbnails/thumb_user1_20260422_143025_abc123.png",
    "ancho": 1024,
    "alto": 768
  }
}
```

---

### 🆕 Crear Pedido Multi-Item

#### POST `/api/create-order`
Crea un pedido con múltiples productos.

**Body:**
```json
{
  "user_id": 1,
  "items": [
    {
      "id_variante": 1,
      "cantidad": 2,
      "archivo_diseno": 123,
      "posicion_x": 100,
      "posicion_y": 150,
      "zoom": 1.2
    },
    {
      "id_variante": 8,
      "cantidad": 1,
      "archivo_diseno": 124,
      "posicion_x": 50,
      "posicion_y": 75,
      "zoom": 1.0
    }
  ],
  "direccion_envio": "Av. Corrientes 1234",
  "ciudad": "Buenos Aires",
  "telefono_contacto": "+54 11 1234-5678",
  "notas_cliente": "Envío urgente por favor"
}
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "order_id": 42,
    "numero_orden": "ORD-2026-00042",
    "total": 32000,
    "items_count": 2
  }
}
```

---

### 🆕 Admin - Dashboard Métricas

#### GET `/api/admin/dashboard/metricas`
Obtiene métricas para el dashboard del administrador.

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "hoy": {
      "pedidos": 5,
      "ventas": 85000
    },
    "mes": {
      "pedidos": 128,
      "ventas": 1540000
    },
    "pedidos_pendientes": 12,
    "stock_bajo": 3,
    "top_productos": [
      {"nombre": "Remera Básica", "unidades": 45},
      {"nombre": "Taza Personalizada", "unidades": 32},
      {"nombre": "Buzo con Capucha", "unidades": 18}
    ]
  }
}
```

---

### 🆕 Admin - Gestión de Pedidos

#### GET `/api/admin/pedidos?filtro=todos`
Lista de pedidos con filtros.

**Filtros disponibles:**
- `todos` - Todos los pedidos
- `pendientes` - Solo pendientes
- `pagados` - Solo pagados
- `no-pagados` - Sin pago o rechazados
- `entregados` - Solo completados

---

#### GET `/api/admin/pedidos/{id_pedido}`
Detalles completos de un pedido.

---

#### PUT `/api/admin/pedidos/{id_pedido}/estado`
Actualizar estado de un pedido.

**Body:**
```json
{
  "estado": "produccion"
}
```

**Estados válidos:**
- `pendiente`
- `pagado`
- `produccion`
- `empaque`
- `enviado`
- `completado`
- `cancelado`

---

#### PUT `/api/admin/pedidos/{id_pedido}/pago`
Actualizar estado de pago.

**Body:**
```json
{
  "estado_pago": "aprobado",
  "metodo_pago": "mercadopago",
  "referencia_externa": "MP-123456789"
}
```

**Estados de pago válidos:**
- `pendiente`
- `aprobado`
- `rechazado`
- `reembolsado`

---

## 🔄 MIGRACIÓN DEL FRONTEND

### Cambios Necesarios en `ProductSelector.vue`

**Antes:**
```javascript
// Catálogo hardcodeado
const productos = ref([
  { id: 'camiseta', nombre: 'Camiseta', precio: 12000 },
  // ...
])
```

**Ahora:**
```javascript
// Cargar desde API
const productos = ref([])
const variantes = ref([])

onMounted(async () => {
  const response = await fetch('http://localhost:8000/api/productos')
  const data = await response.json()
  productos.value = data.data
})

// Cuando el usuario selecciona color + talle
function buscarVariante(productoId, color, talle) {
  const producto = productos.value.find(p => p.id_producto === productoId)
  return producto.variantes.find(v => 
    v.atributos.color?.valor === color &&
    v.atributos.talle?.valor === talle
  )
}
```

---

### Cambios en `CheckoutPanel.vue`

**Antes:**
```javascript
// Un solo producto
const pedido = {
  producto: 'camiseta',
  talle: 'M',
  color: 'Negro',
  cantidad: 1
}
```

**Ahora:**
```javascript
// Carrito con múltiples items
const carrito = ref([
  {
    id_variante: 1,
    cantidad: 2,
    archivo_diseno: 123
  },
  {
    id_variante: 8,
    cantidad: 1,
    archivo_diseno: 124
  }
])

async function crearPedido() {
  const response = await fetch('http://localhost:8000/api/create-order', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: usuarioActual.value.id,
      items: carrito.value,
      direccion_envio: formulario.direccion,
      ciudad: formulario.ciudad,
      telefono_contacto: formulario.telefono
    })
  })
  
  const data = await response.json()
  if (data.success) {
    // Pedido creado: data.data.numero_orden
  }
}
```

---

## 🧪 TESTING

### Script de Prueba

Ejecutar el script de prueba para verificar todos los endpoints:

```bash
cd C:\projects\ai-print-studio\database\source
python test_api_v2.py
```

Ver archivo `test_api_v2.py` para más detalles.

---

## 🐛 TROUBLESHOOTING

### Error: "Table 'Producto_Variantes' doesn't exist"

**Causa:** No ejecutaste los scripts de migración de BD.

**Solución:**
```sql
-- Ejecutar en orden:
-- 1. database/01-backup-bd-actual.sql
-- 2. database/02-nueva-estructura-bd.sql
-- 3. database/03-datos-iniciales.sql
-- 4. database/04-migrar-datos-antiguos.sql
```

---

### Error: "Cannot find module 'PIL'"

**Solución:**
```bash
pip install pillow
```

---

### Error: "Access denied to directory uploads/"

**Solución:**
```bash
# Crear directorio manualmente
mkdir C:\projects\ai-print-studio\uploads
mkdir C:\projects\ai-print-studio\uploads\designs
mkdir C:\projects\ai-print-studio\uploads\thumbnails

# Verificar permisos de escritura
```

---

## 📞 SOPORTE

Si tienes problemas con el nuevo backend:

1. Verificar logs del servidor FastAPI
2. Revisar que la BD tenga la nueva estructura
3. Confirmar que las migraciones se ejecutaron correctamente
4. Probar endpoints con Postman/Thunder Client

---

## ✅ CHECKLIST DE ACTIVACIÓN

Antes de pasar a producción:

- [ ] Scripts de migración ejecutados sin errores
- [ ] Datos migrados correctamente (usuarios + pedidos)
- [ ] Productos y variantes cargados
- [ ] Backend v2 responde en `/api/health`
- [ ] Endpoint `/api/productos` devuelve catálogo
- [ ] Upload de imágenes funciona
- [ ] Crear pedido funciona
- [ ] Admin puede ver pedidos
- [ ] Admin puede actualizar estados
- [ ] Frontend actualizado y probado

---

**¡Éxito en la migración! 🚀**
