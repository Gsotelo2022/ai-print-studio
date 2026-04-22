# 🔄 Nuevo Flujo del Agente IA - Post Login

> **Fecha de implementación:** 22 de abril de 2026  
> **Cambio:** Carga de productos se ejecuta DESPUÉS del login, no al iniciar

---

## 🎯 Objetivo del Cambio

**Optimizar recursos** cargando productos del agente IA solo cuando el usuario está logueado y realmente necesita seleccionar productos.

---

## 📋 Flujo Actual (Después del Cambio)

### 1. Inicio de la Aplicación

```
Usuario abre http://localhost:5173
    ↓
App.vue se monta
    ↓
NO se cargan productos ← CAMBIO PRINCIPAL
    ↓
Usuario ve Hero Section o formularios
```

### 2. Usuario Hace Login

```
Usuario ingresa credenciales
    ↓
POST /api/login → Backend valida
    ↓
onLoginSuccess() se dispara
    ↓
cargarProductosDelAgente() ← SE EJECUTA AQUÍ
    ↓
Estado: productosLoading = true
    ↓
fetch('http://localhost:5001/productos-ia')
    ↓
Agente IA:
  ├─ Consulta BD (SELECT Productos)
  ├─ Llama OLLAMA qwen2.5:1.5b
  └─ Procesa y agrupa productos
    ↓
Respuesta JSON llega (30-90 segundos)
    ↓
productos reactive se llena
    ↓
Estado: productosLoading = false
         productosLoaded = true
```

### 3. Usuario Avanza a Selección de Productos

**Escenario A: Productos ya cargados (rápido)**
```
Usuario selecciona/sube imagen
    ↓
Avanza a ProductSelector
    ↓
productosLoading = false
↓
Muestra grilla de productos inmediatamente
```

**Escenario B: Productos aún cargando (común con 85 productos)**
```
Usuario selecciona/sube imagen
    ↓
Avanza a ProductSelector
    ↓
productosLoading = true ← LOADER ACTIVO
    ↓
Muestra:
  🔄 "Cargando productos disponibles..."
  "El agente IA está consultando el catálogo..."
  Barra de progreso animada
    ↓
[Espera 10-60 segundos restantes]
    ↓
Productos terminan de cargar
    ↓
productosLoading = false
    ↓
Loader desaparece automáticamente
    ↓
Grilla de productos aparece
```

---

## 🧩 Componentes Modificados

### 1. App.vue

**Estados nuevos:**
```javascript
const productosLoading = ref(false) // true mientras carga
const productosLoaded = ref(false)  // true cuando ya cargó
```

**Función modificada:**
```javascript
async function cargarProductosDelAgente() {
  if (productosLoaded.value) {
    console.log('✓ Productos ya cargados, usando caché')
    return // No recargar si ya está
  }
  
  productosLoading.value = true
  console.log('🔄 Cargando productos del agente IA...')
  
  try {
    // ... fetch y procesamiento ...
    productosLoaded.value = true
  } catch (error) {
    // ... fallback ...
    productosLoaded.value = true
  } finally {
    productosLoading.value = false
  }
}
```

**onMounted comentado:**
```javascript
// FLUJO ANTERIOR: Cargar productos al montar el componente
// onMounted(() => {
//   cargarProductosDelAgente()
// })
// FLUJO NUEVO: Cargar productos solo después del login
```

**onLoginSuccess modificado:**
```javascript
function onLoginSuccess(loginData) {
  console.log('Login exitoso:', loginData)
  currentUser.value = loginData
  userLogged.value = true
  showLoginForm.value = false
  
  // ... reset de estados ...
  
  // NUEVO: Cargar productos después del login
  cargarProductosDelAgente() ← AGREGADO
}
```

**ProductSelector con nuevas props:**
```vue
<ProductSelector
  :productos="productos"
  :loading="productosLoading"  ← NUEVO
  :loaded="productosLoaded"    ← NUEVO
  @product-selected="onProductSelected"
  @go-back="onProductSelectorGoBack"
/>
```

---

### 2. ProductSelector.vue

**Props nuevas:**
```javascript
const props = defineProps({
  productos: { type: Object, required: true },
  loading: { type: Boolean, default: false },   ← NUEVO
  loaded: { type: Boolean, default: false },    ← NUEVO
})
```

**Template con loader:**
```vue
<template>
  <div class="product-selector">
    <div class="section-header">
      <h2>Selecciona el producto</h2>
      <button @click="goBack">← Volver</button>
    </div>

    <!-- Loader: aparece mientras loading=true -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <h3>🔄 Cargando productos disponibles...</h3>
      <p>
        El agente IA está consultando el catálogo desde la base de datos.
        Esto puede tardar entre 30 y 90 segundos.
      </p>
      <div class="loading-progress">
        <div class="progress-bar">
          <div class="progress-fill"></div>
        </div>
        <p>Procesando con OLLAMA qwen2.5:1.5b...</p>
      </div>
    </div>

    <!-- Productos: aparecen cuando loading=false -->
    <div v-else class="products-grid">
      <div v-for="[key, prod] in Object.entries(productos)">
        <!-- Cards de productos -->
      </div>
    </div>
  </div>
</template>
```

**Estilos del loader:**
- Spinner rotatorio
- Barra de progreso animada
- Texto informativo
- Centrado verticalmente

---

## ⚡ Ventajas del Nuevo Flujo

✅ **Optimización de recursos**
   - No hace fetch innecesaria si usuario no hace login
   - Ahorra carga del servidor cuando hay muchos visitantes

✅ **Feedback visual claro**
   - Usuario sabe que algo está cargando
   - Mensaje explica qué está pasando y cuánto tardará

✅ **Caché inteligente**
   - `productosLoaded` evita recargar si ya se cargó
   - Solo carga una vez por sesión

✅ **Fallback mantenidomantiene**
   - Si agente falla, usa productos hardcoded
   - Aplicación nunca se queda sin productos

---

## ⚠️ Consideraciones

### Tiempo de Espera

**Con OLLAMA (85 productos):**
- i3/16GB RAM: 60-90 segundos
- i5/16GB RAM: 45-60 segundos
- i7+/32GB RAM: 30-45 segundos

**Recomendaciones:**
- Para hardware limitado (i3): considerar `LIMITE_PRODUCTOS = 20`
- Para producción: usar servidor más potente o cache en backend

### Experiencia del Usuario

**Caso ideal:**
- Usuario hace login
- Productos cargan en background (30-45s)
- Usuario sube/genera imagen (tarda ~30s)
- Al llegar a ProductSelector, productos ya están listos ✅

**Caso no ideal:**
- Usuario hace login
- Productos demoran (60-90s)
- Usuario sube imagen rápido (~10s)
- Al llegar a ProductSelector, aún está cargando
- Ve loader por 40-80s ⏳

**Solución al caso no ideal:**
- Mensaje claro de espera
- Barra de progreso animada
- Opción de "Volver" para editar imagen mientras espera

---

## 🔧 Testing del Nuevo Flujo

### Test Manual

1. **Iniciar sistema:**
   ```powershell
   .\RUN.bat
   ```

2. **Abrir navegador:**
   ```
   http://localhost:5173
   ```

3. **Verificar NO se carga productos:**
   - Abrir DevTools (F12)
   - Consola NO debe mostrar: "🔄 Cargando productos del agente IA..."
   - Network tab NO debe mostrar: GET http://localhost:5001/productos-ia

4. **Hacer login:**
   - Email: cliente@test.com
   - Password: password123

5. **Verificar SI se carga productos después del login:**
   - Consola DEBE mostrar: "🔄 Cargando productos del agente IA..."
   - Network tab DEBE mostrar: GET http://localhost:5001/productos-ia (pending)

6. **Avanzar rápido a ProductSelector:**
   - Hacer clic en "Subir imagen"
   - Seleccionar cualquier imagen
   - Si productos aún cargando, DEBE ver loader:
     - Spinner animado
     - "🔄 Cargando productos disponibles..."
     - Barra de progreso

7. **Esperar a que termine:**
   - Loader desaparece
   - Grilla de productos aparece
   - Puede seleccionar productos normalmente

### Test con LIMITE_PRODUCTOS

Para testing rápido, editar `agentes-Ollama/agente_productos.py`:

```python
LIMITE_PRODUCTOS = 10  # Para pruebas rápidas (15-30s)
```

Reiniciar agente:
```powershell
# En ventana del agente: Ctrl+C
python agente_productos.py
```

---

## 🔄 Cómo Revertir al Flujo Anterior

Ver archivo: **FLUJO_ANTERIOR_AGENTE.md**

**Resumen rápido:**

1. En `App.vue`:
   - Descomentar: `onMounted(() => { cargarProductosDelAgente() })`
   - Eliminar llamada en `onLoginSuccess`

2. En `ProductSelector.vue`:
   - Eliminar props `loading` y `loaded`
   - Eliminar sección `<div v-if="loading">`
   - Cambiar `<div v-else class="products-grid">` a `<div class="products-grid">`

---

## 📊 Comparación de Flujos

| Aspecto | Flujo Anterior | Flujo Nuevo |
|---------|----------------|-------------|
| **Trigger** | onMounted (al cargar app) | onLoginSuccess (después del login) |
| **Timing** | Inmediato | Diferido hasta login |
| **Usuario sin login** | Carga igual | No carga |
| **Espera percibida** | Paralelo (no nota) | Potencialmente visible |
| **Feedback UX** | Silencioso | Loader con mensaje |
| **Recursos** | Siempre consume | Solo si hace login |
| **Caché** | No implementado | Implementado (productosLoaded) |

---

## 📝 Logs Esperados

### Al abrir la app (sin login)

**Consola del navegador:**
```
[Nada relacionado con productos]
```

### Al hacer login

**Consola del navegador:**
```
Login exitoso: {email: "cliente@test.com", ...}
🔄 Cargando productos del agente IA...
```

**Consola del agente (ventana terminal):**
```
[DEBUG] Iniciando /productos-ia...
[DB] Conectando a SQL Server...
[DB] ✓ Conectado a SQL Server
[DB] Ejecutando SELECT... (Total: 85 productos)
[OLLAMA] Enviando petición a http://localhost:11434...
[OLLAMA] ✓ Respuesta recibida en 52.3s
✓ Retornando 5 productos agrupados
```

### Cuando terminan de cargar

**Consola del navegador:**
```
✓ Productos cargados del agente: {buzo: {...}, remera: {...}, ...}
```

---

## 🎨 Screenshots Esperados

### 1. Antes de hacer login
- Hero section o formularios
- NO hay actividad de red hacia el agente

### 2. Después del login
- Dashboard del usuario
- Network tab muestra: GET /productos-ia (pending, ~60s)

### 3. Al avanzar a ProductSelector (si aún carga)
- Loader centrado
- Spinner rotatorio celeste
- Mensaje: "Cargando productos disponibles..."
- Barra de progreso animada
- Texto: "Procesando con OLLAMA qwen2.5:1.5b..."

### 4. Cuando termina de cargar
- Grilla de productos (Buzo, Remera, Taza, etc.)
- Cards clicables
- Panel de variantes abajo

---

## ✅ Checklist de Implementación

- [x] App.vue: Estados `productosLoading` y `productosLoaded`
- [x] App.vue: `cargarProductosDelAgente()` actualiza estados
- [x] App.vue: `onMounted` comentado (no carga)
- [x] App.vue: `onLoginSuccess` llama a `cargarProductosDelAgente()`
- [x] App.vue: Props `:loading` y `:loaded` a ProductSelector
- [x] ProductSelector.vue: Props `loading` y `loaded` definidos
- [x] ProductSelector.vue: Template con `v-if="loading"` para loader
- [x] ProductSelector.vue: Template con `v-else` para grilla
- [x] ProductSelector.vue: Estilos CSS para loader
- [x] FLUJO_ANTERIOR_AGENTE.md: Documentación de rollback
- [x] FLUJO_NUEVO_AGENTE.md: Documentación del cambio

---

**Fin del Documento**

Este flujo garantiza que los recursos del agente IA se utilicen solo cuando el usuario realmente los necesita, mejorando la eficiencia del sistema.
