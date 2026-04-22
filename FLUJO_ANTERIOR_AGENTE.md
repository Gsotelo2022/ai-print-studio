# 📋 Flujo Anterior del Agente IA (Backup para Rollback)

> **Fecha de backup:** 22 de abril de 2026  
> **Motivo:** Cambio en el flujo de carga de productos (de "al inicio" a "después del login")

---

## Flujo Original (Antes del cambio)

### Cuando se ejecutaba RUN.bat:

```
1. RUN.bat inicia todos los servidores
   ├─ FastAPI (puerto 8000)
   ├─ OLLAMA (puerto 11434)
   ├─ Agente IA (puerto 5001) ← Ya disponible
   ├─ Frontend Vue (puerto 5173)
   └─ PHP Backend (puerto 8080)

2. Usuario abre navegador en http://localhost:5173

3. App.vue se monta (onMounted)
   └─→ Llama inmediatamente a cargarProductosDelAgente()
       └─→ fetch('http://localhost:5001/productos-ia')
           └─→ Agente consulta BD
               └─→ OLLAMA procesa
                   └─→ Retorna JSON
                       └─→ productos reactive se llena

4. Productos ya disponibles cuando usuario hace login
```

### Código Original en App.vue

**Línea ~205-242:**
```javascript
async function cargarProductosDelAgente() {
  try {
    const response = await fetch('http://localhost:5001/productos-ia')
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    
    const data = await response.json()
    productosDelAgente.value = data
    
    data.forEach(item => {
      const key = item.producto.toLowerCase()
      productos[key] = {
        nombre: item.producto,
        talles: item.talles || [],
        colores: item.colores || [],
        precio: 12000,
        tienesTalle: (item.talles && item.talles.length > 0)
      }
    })
    
    console.log('✓ Productos cargados del agente:', productos)
  } catch (error) {
    console.log('⚠ Error cargando productos del agente, usando valores por defecto:', error.message)
    
    // Fallback hardcoded
    Object.assign(productos, {
      camiseta: { nombre: 'Camiseta', talles: ['S', 'M', 'L', 'XL', 'XXL'], colores: ['Blanco', 'Negro', 'Gris', 'Azul'], precio: 12000, tienesTalle: true },
      taza:     { nombre: 'Taza',     talles: [], colores: ['Blanco', 'Negro'], precio: 8000,  tienesTalle: false },
      sudadera: { nombre: 'Sudadera', talles: ['S', 'M', 'L', 'XL', 'XXL'], colores: ['Blanco', 'Negro'], precio: 18000, tienesTalle: true },
      cojin:    { nombre: 'Cojín',    talles: [], colores: ['Blanco', 'Negro'], precio: 10000, tienesTalle: false },
      mochila:  { nombre: 'Mochila',  talles: [], colores: ['Negro', 'Gris', 'Azul'], precio: 15000, tienesTalle: false },
      gorra:    { nombre: 'Gorra',    talles: [], colores: ['Blanco', 'Negro'], precio: 9000,  tienesTalle: false },
    })
  }
}

// ← AQUÍ SE LLAMABA AL MONTAR
onMounted(() => {
  cargarProductosDelAgente()
})
```

**onLoginSuccess (Línea ~328-340):**
```javascript
function onLoginSuccess(loginData) {
  console.log('Login exitoso:', loginData)
  currentUser.value = loginData
  userLogged.value = true
  showLoginForm.value = false
  imageSourceMode.value = null
  generatedImage.value = null
  selectedProduct.value = null
  orderData.value = null
  // ← No llamaba a cargar productos aquí
}
```

---

## Ventajas del Flujo Original

✅ **Productos listos inmediatamente** cuando usuario hace login  
✅ **Menos tiempo percibido de espera** (carga paralela mientras usuario navega)  
✅ **UX más fluida** sin loaders adicionales  

---

## Desventajas del Flujo Original

❌ **Llamada innecesaria** si el usuario nunca hace login  
❌ **Carga de recursos** aunque usuario solo esté explorando  
❌ **Timeout de 60s** podría expirar antes de que usuario llegue a productos  

---

## Cómo Revertir los Cambios

### 1. Restaurar App.vue

**Descomentar la llamada en onMounted:**
```javascript
onMounted(() => {
  cargarProductosDelAgente() // ← Descomentar esta línea
})
```

**Eliminar la llamada en onLoginSuccess:**
```javascript
function onLoginSuccess(loginData) {
  console.log('Login exitoso:', loginData)
  currentUser.value = loginData
  userLogged.value = true
  showLoginForm.value = false
  imageSourceMode.value = null
  generatedImage.value = null
  selectedProduct.value = null
  orderData.value = null
  // ← Eliminar llamada a cargarProductosDelAgente() si existe
}
```

**Eliminar estados de loading:**
```javascript
// Eliminar estas variables si existen:
const productosLoading = ref(false)
const productosLoaded = ref(false)
```

### 2. Restaurar ProductSelector.vue

**Eliminar prop de loading:**
```vue
<template>
  <div class="product-selector">
    <!-- Eliminar sección de loading -->
    <!-- <div v-if="loading" class="loading-container">...</div> -->
    
    <!-- Mostrar productos directamente -->
    <div class="products-grid">
      <div v-for="[key, prod] in Object.entries(productos)" ...>
        ...
      </div>
    </div>
  </div>
</template>

<script setup>
// Eliminar:
// defineProps({ productos: Object, loading: Boolean })

// Dejar solo:
defineProps({ productos: Object })
</script>
```

### 3. Verificar funcionamiento

```powershell
# Ejecutar
.\RUN.bat

# Abrir navegador
# http://localhost:5173

# Verificar en consola del navegador (F12):
# Debe aparecer: "✓ Productos cargados del agente: {...}"
# Inmediatamente al cargar la página, antes de hacer login
```

---

## Archivos Modificados en el Cambio

- ✏️ `frontend/src/App.vue` (líneas ~205-250, ~328-345)
- ✏️ `frontend/src/components/ProductSelector.vue` (template y props)
- 📝 `FLUJO_ANTERIOR_AGENTE.md` (este archivo - documentación)

---

## Logs Esperados (Flujo Original)

**Consola del Navegador al abrir http://localhost:5173:**
```
[App.vue] onMounted: Cargando productos del agente...
[fetch] GET http://localhost:5001/productos-ia
[Agente IA] Consultando BD...
[OLLAMA] Procesando 85 productos...
✓ Productos cargados del agente: { buzo: {...}, remera: {...}, ... }
```

**Tiempo típico:** 45-90 segundos (depende de OLLAMA)

---

## Comparación de Flujos

| Aspecto | Flujo Original (onMounted) | Flujo Nuevo (onLogin) |
|---------|---------------------------|----------------------|
| **Momento de carga** | Al iniciar app | Después del login |
| **Usuario sin login** | Carga igual | No carga |
| **Tiempo de respuesta** | Paralelo (usuario no espera) | Secuencial (usuario puede esperar) |
| **Recursos utilizados** | Siempre | Solo si hace login |
| **UX** | Fluida, sin loaders | Loader "Cargando productos..." |
| **Timeout** | Puede expirar antes de login | Ocurre cuando usuario necesita datos |

---

## Recomendación

- **Usar Flujo Original** si: mayoría de usuarios hacen login, hardware potente (i5+)
- **Usar Flujo Nuevo** si: muchos visitantes no logueados, hardware limitado (i3)

---

**Fin del Backup**
