# 🎯 ESTADO ACTUAL Y TAREAS PARA HACER TODO FUNCIONAL

> **Fecha:** 22 de abril de 2026  
> **Objetivo:** Completar funcionalidades faltantes antes de optimizar

---

## ✅ LO QUE YA FUNCIONA (100%)

### 1. Sistema de Autenticación ✅
- **Backend:** FastAPI (puerto 8000)
- **Endpoints:**
  - `POST /api/register` → Registro de usuarios ✅
  - `POST /api/login` → Autenticación ✅
- **Frontend:**
  - `CreateUser.vue` → Formulario de registro ✅
  - `Login.vue` → Formulario de login ✅
- **Base de Datos:**
  - Tabla `Usuarios` con hasheo PBKDF2-SHA256 ✅
- **Tests:** `test_register_complete.py`, `test_auth_flow.py` ✅

**Status:** 🟢 **COMPLETAMENTE FUNCIONAL**

---

### 2. Panel de Administrador - Gestión de Pedidos ✅
- **Backend:** FastAPI (puerto 8000)
- **Endpoints:**
  - `GET /api/admin/pedidos` → Listar todos los pedidos ✅
  - `PUT /api/admin/pedidos/{id}/estado` → Cambiar estado ✅
  - `PUT /api/admin/pedidos/{id}/pago` → Cambiar estado de pago ✅
- **Frontend:**
  - `AdminDashboard.vue` → Panel principal ✅
  - `GestionPedidos.vue` → Tabla de pedidos con filtros ✅
- **Funcionalidades:**
  - Ver todos los pedidos ✅
  - Filtrar por estado (pendientes, pagados, etc.) ✅
  - Actualizar estado de pedido ✅
  - Actualizar estado de pago ✅
  - Paginación ✅

**Status:** 🟢 **COMPLETAMENTE FUNCIONAL**

---

## 🟡 LO QUE FUNCIONA CON LIMITACIONES

### 3. Gestión de Productos 🟡
- **Backend:** Agente IA (puerto 5001) + FastAPI (puerto 8000)
- **Problemas:**
  - ⚠️ El agente IA corre por separado y puede no estar iniciado
  - ⚠️ Si el agente falla, usa productos hardcodeados en `App.vue`
  - ⚠️ Los precios NO vienen de la base de datos
  - ⚠️ No hay CRUD de productos desde el admin
- **Frontend:**
  - `GestionProductos.vue` → Carga productos del agente ✅
  - Pero no puede crear/editar productos ❌

**Status:** 🟡 **FUNCIONA PARCIALMENTE** (depende del agente)

**Tareas Pendientes:**
1. ✅ El agente ya está funcional según `FLUJO_NUEVO_AGENTE.md`
2. ❌ Hacer que el admin pueda agregar productos SIN el agente
3. ❌ Conectar precios de productos con la base de datos

---

## ❌ LO QUE AÚN NO FUNCIONA

### 4. Generación de Imágenes con IA ❌

**Backend PHP:** `backend/api/generate-image.php`

**Problema Principal:** Falta configurar API Key

```php
// backend/config/app.php línea 12
'openai' => [
    'api_key' => 'TU_OPENAI_API_KEY',  // ❌ Necesita ser reemplazado
    'api_url' => 'https://api.openai.com/v1/images/generations',
],
```

**Opciones:**

#### **OPCIÓN A: Usar OpenAI DALL-E** (backend PHP actual)
- Costo: ~$0.04 USD por imagen
- Requiere: Cuenta de OpenAI con créditos
- URL: https://platform.openai.com/api-keys

#### **OPCIÓN B: Implementar en FastAPI con alternativa gratis**
- Alternativas:
  - **Replicate** (Stable Diffusion gratis/barato)
  - **Hugging Face** (modelos gratuitos)
  - **Stability AI** (tiene planes gratuitos limitados)

#### **OPCIÓN C: Mock/Simulación (para desarrollo)**
- Devolver imágenes de ejemplo/placeholder
- Permite probar el flujo sin gastar dinero

**Frontend:** `PromptGenerator.vue` → Ya está listo esperando el endpoint

**Status:** ❌ **NO FUNCIONA** (falta API key)

---

### 5. Remover Fondo de Imágenes ❌

**Backend FastAPI:** `POST /api/remove-background`

**Problema:** Usa librería `rembg` que es pesada

```python
# database/source/app.py línea 379
from rembg import remove  # Descarga modelo ~350MB la primera vez
```

**Status actual:**
- ✅ El código está implementado
- ❌ Puede ser lento (30-60 segundos la primera vez)
- ⚠️ Requiere mucha memoria RAM

**Frontend:** `BackgroundRemover.vue` → Ya está listo

**Recomendación:** 
- Hacer que el botón "Remover fondo" sea opcional
- Mostrar mensaje "Procesando... esto puede tardar 30-60 segundos"

**Status:** 🟡 **IMPLEMENTADO PERO LENTO**

---

### 6. Creación de Pedidos ⚠️

**Problema:** Hay DOS implementaciones

#### **Implementación A: Backend PHP**
- Archivo: `backend/api/create-order.php`
- **NO se usa actualmente** en el frontend

#### **Implementación B: Backend FastAPI** ✅
- Archivo: `database/source/app.py` → `POST /api/create-order`
- **SÍ se usa** desde `PreviewPanel.vue`

**Confusión en useApi.js:**
```javascript
// Línea 164 - apunta a PHP (INCORRECTO)
async function createOrder(orderData) {
  return post('/api/create-order.php', orderData)
}
```

**Debería ser:**
```javascript
async function createOrder(orderData) {
  return post(`${baseApi}/create-order`, orderData)  // FastAPI
}
```

**Status:** 🟢 **FUNCIONA** (pero con configuración incorrecta en useApi.js)

**Tarea:** Corregir la ruta en `useApi.js`

---

### 7. Pago con Mercado Pago ❌

**Backend PHP:** `backend/api/create-payment.php`

**Problema Principal:** Falta configurar credenciales

```php
// backend/config/app.php línea 19
'mercadopago' => [
    'access_token' => 'TU_MERCADOPAGO_ACCESS_TOKEN',  // ❌ Necesita ser reemplazado
],
```

**Backend FastAPI TAMBIÉN tiene implementación:**
- `database/source/app.py` línea 295 → `POST /api/create-payment`
- Usa: `mercadopago` SDK de Python
- Tiene token hardcodeado de prueba (TEST-xxxxx)

**Problema:** Dos implementaciones, ninguna configurada correctamente

**Opciones:**

#### **OPCIÓN A: Usar Mercado Pago real**
- Registrarse en: https://www.mercadopago.com.ar/developers
- Obtener credenciales de prueba (sandbox)
- Configurar webhook para notificaciones

#### **OPCIÓN B: Simular pago (para desarrollo)**
- Botón "Simular Pago Exitoso"
- Actualizar pedido directamente en BD
- Permite probar flujo sin cuenta de MP

**Status:** ❌ **NO FUNCIONA** (faltan credenciales)

---

### 8. Subir Imágenes Propias ⚠️

**Frontend:** `ImageUploader.vue`

**Status:**
- ✅ El componente existe
- ✅ Puede recibir archivos
- ❌ NO tiene endpoint backend para guardar

**Necesita:**
- Endpoint FastAPI: `POST /api/upload-image`
- Guardar archivo en `uploads/`
- Devolver URL o base64

**Workaround actual:** El usuario puede generar con IA, no subir

**Status:** 🟡 **COMPONENTE LISTO, FALTA BACKEND**

---

### 9. Visualización Previa (Preview) ⚠️

**Frontend:** `PreviewPanel.vue`

**Funcionalidades:**
- ✅ Muestra producto seleccionado
- ✅ Muestra imagen generada/subida
- ✅ Permite ajustar posición (X, Y)
- ✅ Permite ajustar zoom
- ❌ NO muestra preview visual real (solo datos)

**Mejora pendiente:**
- Overlay de imagen sobre mockup del producto
- Canvas para posicionar visualmente

**Status:** 🟡 **FUNCIONALIDAD BÁSICA, FALTA VISUALIZACIÓN**

---

## 📋 RESUMEN DE TAREAS PENDIENTES

### 🔴 CRÍTICAS (bloquean funcionalidad principal)

| # | Tarea | Componente | Prioridad | Esfuerzo |
|---|-------|------------|-----------|----------|
| 1 | Configurar API de generación de imágenes | Backend | 🔴 Alta | 30 min |
| 2 | Configurar Mercado Pago (o simularlo) | Backend | 🔴 Alta | 1 hora |
| 3 | Corregir ruta de create-order en useApi.js | Frontend | 🔴 Alta | 5 min |

### 🟡 IMPORTANTES (mejoran experiencia)

| # | Tarea | Componente | Prioridad | Esfuerzo |
|---|-------|------------|-----------|----------|
| 4 | Implementar upload de imágenes | Backend | 🟡 Media | 45 min |
| 5 | Mejorar preview visual con canvas | Frontend | 🟡 Media | 2 horas |
| 6 | Optimizar rembg (o hacerlo opcional) | Backend | 🟡 Media | 30 min |
| 7 | CRUD de productos desde admin | Backend + Frontend | 🟡 Media | 3 horas |

### 🟢 OPCIONALES (nice to have)

| # | Tarea | Componente | Prioridad | Esfuerzo |
|---|-------|------------|-----------|----------|
| 8 | Dashboard con métricas para admin | Frontend | 🟢 Baja | 2 horas |
| 9 | Historial de pedidos para clientes | Frontend | 🟢 Baja | 1.5 horas |
| 10 | Exportar pedidos a Excel | Backend | 🟢 Baja | 1 hora |

---

## 🚀 PLAN DE ACCIÓN RECOMENDADO

### FASE 1: Hacer el flujo principal funcional (4-5 horas)

#### Paso 1: Configurar Generación de Imágenes (30 min)

**Opción Rápida - Mock/Simulación:**
```python
# En database/source/app.py, agregar:

@app.post('/api/generate-image')
def generate_image_mock(payload: dict):
    """Mock para testing - devuelve imagen de ejemplo"""
    import random
    
    # Imágenes de placeholder de diferentes estilos
    placeholders = [
        "https://picsum.photos/seed/design1/1024/1024",
        "https://picsum.photos/seed/design2/1024/1024",
        "https://picsum.photos/seed/design3/1024/1024",
    ]
    
    return json_success({
        "imagen_url": random.choice(placeholders),
        "prompt": payload.get("prompt", "")
    })
```

**Opción Real - OpenAI DALL-E:**
1. Ir a: https://platform.openai.com/api-keys
2. Crear API key
3. Editar `backend/config/app.php` línea 12
4. Agregar crédito ($5 USD mínimo)

#### Paso 2: Corregir ruta de create-order (5 min)

Editar `frontend/src/composables/useApi.js` línea 164:
```javascript
// ANTES:
async function createOrder(orderData) {
  return post('/api/create-order.php', orderData)
}

// DESPUÉS:
async function createOrder(orderData) {
  return post(`${baseApi}/create-order`, orderData)
}
```

#### Paso 3: Configurar Mercado Pago (1 hora)

**Opción Rápida - Simulación:**
```python
# En database/source/app.py, modificar create-payment:

@app.post('/api/create-payment')
def create_payment_mock(payload: PaymentIn):
    """Mock para testing - simula pago exitoso"""
    import time
    time.sleep(2)  # Simular delay
    
    # URL de "pago exitoso" que redirige a la app
    return json_success({
        "init_point": "http://localhost:5173/success?payment=mock_success"
    })
```

**Opción Real - Mercado Pago Sandbox:**
1. Ir a: https://www.mercadopago.com.ar/developers
2. Crear aplicación de prueba
3. Copiar credenciales de TEST
4. Editar `backend/config/app.php` línea 19

#### Paso 4: Testing del Flujo Completo (30 min)

1. Iniciar todo: `RUN.bat`
2. Registrarse como usuario nuevo
3. Generar imagen con prompt
4. Seleccionar producto + color + talle
5. Confirmar pedido
6. "Pagar" (mock o real)
7. Ver pedido en panel admin

---

### FASE 2: Mejorar experiencia de usuario (3-4 horas)

#### Paso 5: Implementar Upload de Imágenes

```python
# En database/source/app.py

from fastapi import UploadFile, File
import shutil
from pathlib import Path

@app.post('/api/upload-image')
async def upload_image(file: UploadFile = File(...)):
    """Subir imagen del usuario"""
    
    # Validar tipo
    allowed_types = ['image/jpeg', 'image/png', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(400, {"error": "Tipo de archivo no permitido"})
    
    # Crear directorio uploads si no existe
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    
    # Guardar archivo con nombre único
    import time
    filename = f"upload_{int(time.time())}_{file.filename}"
    filepath = uploads_dir / filename
    
    with filepath.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Devolver URL
    return json_success({
        "imagen_url": f"http://localhost:8000/uploads/{filename}",
        "filename": filename
    })
```

#### Paso 6: Mejorar Preview Visual

En `PreviewPanel.vue`, agregar canvas HTML5:
```vue
<canvas 
  ref="previewCanvas" 
  width="800" 
  height="1000"
  class="preview-canvas"
></canvas>

<script setup>
import { ref, onMounted, watch } from 'vue'

const previewCanvas = ref(null)

function renderPreview() {
  const canvas = previewCanvas.value
  const ctx = canvas.getContext('2d')
  
  // Cargar imagen del producto (mockup)
  const mockupImg = new Image()
  mockupImg.src = '/mockups/remera.png'
  
  mockupImg.onload = () => {
    // Dibujar mockup
    ctx.drawImage(mockupImg, 0, 0, 800, 1000)
    
    // Cargar diseño del usuario
    const designImg = new Image()
    designImg.src = props.imagen_url
    
    designImg.onload = () => {
      // Aplicar posición y zoom
      const x = previewData.value.posicion_x
      const y = previewData.value.posicion_y
      const zoom = previewData.value.zoom
      
      ctx.save()
      ctx.translate(x, y)
      ctx.scale(zoom, zoom)
      ctx.drawImage(designImg, 0, 0, 300, 400)
      ctx.restore()
    }
  }
}

watch([() => previewData.value.posicion_x, 
       () => previewData.value.posicion_y, 
       () => previewData.value.zoom], renderPreview)

onMounted(renderPreview)
</script>
```

---

### FASE 3: Funcionalidades Admin Completas (3-4 horas)

#### Paso 7: CRUD de Productos

Ya está parcialmente implementado en FastAPI:
- ✅ `GET /api/admin/productos` (falta implementar)
- ✅ `POST /api/admin/productos`
- ✅ `PUT /api/admin/productos/{id}`
- ✅ `DELETE /api/admin/productos/{id}`

Necesita frontend en `GestionProductos.vue`

#### Paso 8: Dashboard con Métricas

Ya propuesto en `PROPUESTA_MEJORAS_BD.md` líneas 1104-1191

---

## 🎯 DECISIÓN RÁPIDA

### ¿Qué quieres hacer AHORA?

#### **OPCIÓN 1: Mínimo Viable (2 horas)**
1. Mock de generación de imágenes
2. Mock de pago
3. Corregir ruta de create-order
4. ✅ **FLUJO COMPLETO FUNCIONANDO**

#### **OPCIÓN 2: Semi-Funcional (4 horas)**
1. Configurar OpenAI DALL-E real
2. Configurar Mercado Pago sandbox real
3. Implementar upload de imágenes
4. ✅ **SISTEMA CASI COMPLETO**

#### **OPCIÓN 3: Full Featured (8-10 horas)**
1. Todo lo de Opción 2
2. Preview visual con canvas
3. CRUD de productos
4. Dashboard admin
5. ✅ **SISTEMA PROFESIONAL**

---

## 📞 PRÓXIMO PASO

**Dime qué opción prefieres y empezamos a implementar:**
- 🟢 Opción 1: Mockear todo y probar flujo
- 🟡 Opción 2: APIs reales + funcionalidades básicas
- 🔴 Opción 3: Sistema completo

O dime: "Empezá con..." y te guío paso a paso.
