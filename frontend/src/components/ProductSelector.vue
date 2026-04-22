<!--
  ============================================
  ProductSelector.vue - Paso 2: Elegir producto
  ============================================
  Este componente maneja:
    1. Grilla de productos disponibles (camiseta, taza, etc.)
    2. Selección de variantes (talle, color, cantidad)
    3. Cálculo de precio dinámico

  COMUNICACIÓN:
    - Recibe: productos (catálogo desde App.vue) via props
    - Emite: @product-selected → le dice a App.vue qué eligió el usuario

  CONCEPTOS VUE:
    - props: datos que el padre (App.vue) pasa al hijo
    - v-for: renderiza una lista de elementos
    - v-model: vincula un input con una variable (two-way binding)
    - computed: calcula valores derivados automáticamente
-->
<template>
  <div class="product-selector">
    <!-- Header con título y botón volver -->
    <div class="section-header">
      <h2 class="section-title">
        <span class="step-badge">3</span>
        Selecciona el producto
      </h2>
      <button @click="goBack" class="btn-volver">
        ← Volver
      </button>
    </div>

    <!-- Estado de carga: mostrar mientras el agente procesa productos -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <h3 class="loading-title">🔄 Cargando productos disponibles...</h3>
      <p class="loading-subtitle">
        El agente IA está consultando el catálogo desde la base de datos.<br>
        Esto puede tardar entre 30 y 90 segundos.
      </p>
      <div class="loading-progress">
        <div class="progress-bar">
          <div class="progress-fill"></div>
        </div>
        <p class="progress-text">Procesando con OLLAMA qwen2.5:1.5b...</p>
      </div>
    </div>

    <!-- Grilla de productos: mostrar solo cuando no está cargando -->
    <div v-else class="products-grid">
      <!--
        v-for recorre el catálogo de productos.
        Object.entries() convierte { camiseta: {...}, taza: {...} }
        en [['camiseta', {...}], ['taza', {...}]]
      -->
      <div
        v-for="[key, prod] in Object.entries(productos)"
        :key="key"
        class="product-card"
        :class="{ selected: selectedKey === key }"
        @click="selectProduct(key)"
      >
        <div class="product-icon">{{ productIcons[key] || '📦' }}</div>
        <div class="product-name">{{ prod.nombre }}</div>
        <div class="product-price">${{ formatPrice(prod.precio) }}</div>
      </div>
    </div>

    <!-- Panel de variantes (aparece al seleccionar un producto) -->
    <div v-if="selectedKey" class="variants-panel">
      <h3>Personaliza tu {{ currentProduct.nombre }}</h3>

      <!-- Talle (solo si el producto lo requiere) -->
      <div v-if="currentProduct.tienesTalle" class="form-group">
        <label class="form-label">Talle:</label>
        <div class="variant-options">
          <button
            v-for="t in talles"
            :key="t"
            @click="talle = t"
            class="btn btn-variant"
            :class="{ 'btn-active': talle === t }"
          >
            {{ t }}
          </button>
        </div>
      </div>

      <!-- Color -->
      <div class="form-group">
        <label class="form-label">Color:</label>
        <div class="variant-options">
          <button
            v-for="c in colores"
            :key="c"
            @click="color = c"
            class="btn btn-variant"
            :class="{ 'btn-active': color === c }"
          >
            {{ c }}
          </button>
        </div>
      </div>

      <!-- Cantidad -->
      <div class="form-group">
        <label class="form-label">Cantidad:</label>
        <div class="quantity-control">
          <button @click="cantidad > 1 && cantidad--" class="btn btn-sm">-</button>
          <span class="quantity-display">{{ cantidad }}</span>
          <button @click="cantidad < 10 && cantidad++" class="btn btn-sm">+</button>
        </div>
      </div>

      <!-- Precio total -->
      <div class="price-summary">
        <span class="price-label">Total:</span>
        <span class="price-value">${{ formatPrice(precioTotal) }}</span>
      </div>

      <!-- Botón continuar -->
      <button
        @click="confirmSelection"
        :disabled="!canContinue"
        class="btn btn-primary"
      >
        Continuar →
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// --- Props: datos que recibe del padre (App.vue) ---
// defineProps declara qué datos espera este componente
const props = defineProps({
  productos: {
    type: Object,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  loaded: {
    type: Boolean,
    default: false,
  },
})

// --- Eventos ---
const emit = defineEmits(['product-selected', 'go-back'])

// --- Estado local ---
const selectedKey = ref(null)   // Key del producto seleccionado ('camiseta', 'taza', etc.)
const talle = ref('M')
const color = ref('Blanco')
const cantidad = ref(1)

// Iconos para cada producto
const productIcons = {
  camiseta: '👕',
  taza:     '☕',
  sudadera: '🧥',
  cojin:    '🛋️',
  mochila:  '🎒',
  gorra:    '🧢',
  buzo:     '🧥',
  musculosa: '👕',
  almohada: '🛋️',
}

// --- Computed ---
// El producto actualmente seleccionado (objeto completo)
const currentProduct = computed(() => {
  return selectedKey.value ? props.productos[selectedKey.value] : null
})

// Talles disponibles para el producto actual (dinámicos del agente)
const talles = computed(() => {
  return currentProduct.value?.talles || []
})

// Colores disponibles para el producto actual (dinámicos del agente)
const colores = computed(() => {
  return currentProduct.value?.colores || []
})

// Precio total = precio unitario × cantidad
const precioTotal = computed(() => {
  if (!currentProduct.value) return 0
  return currentProduct.value.precio * cantidad.value
})

// ¿Se puede continuar? (debe haber producto, y talle si aplica)
const canContinue = computed(() => {
  if (!currentProduct.value) return false
  if (currentProduct.value.tienesTalle && !talle.value) return false
  return true
})

// --- Métodos ---
function selectProduct(key) {
  selectedKey.value = key
  // Resetear variantes al cambiar producto
  talle.value = talles.value.length > 0 ? talles.value[0] : null
  color.value = colores.value.length > 0 ? colores.value[0] : null
  cantidad.value = 1
}

function confirmSelection() {
  // Emitir al padre toda la info del producto seleccionado
  emit('product-selected', {
    key: selectedKey.value,
    nombre: currentProduct.value.nombre,
    precio: currentProduct.value.precio,
    talle: currentProduct.value.tienesTalle ? talle.value : null,
    color: color.value,
    cantidad: cantidad.value,
    precioTotal: precioTotal.value,
  })
}

function goBack() {
  emit('go-back')
}

function formatPrice(price) {
  return new Intl.NumberFormat('es-AR').format(price)
}
</script>
<style scoped>
:root {
  --color-primary: #06b6d4;
  --color-primary-dark: #0b7285;
  --color-surface: #0f1724;
  --color-accent: #ffd54f;
  --color-text: #e6eef8;
  --color-border: rgba(255, 255, 255, 0.06);
}

.product-selector {
  padding: 20px 0;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

.btn-volver {
  padding: 8px 16px;
  background-color: transparent;
  border: 2px solid #ffd54f;
  color: #ffd54f;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-volver:hover {
  background-color: rgba(255, 213, 79, 0.1);
  transform: translateY(-2px);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.4rem;
  margin-bottom: 24px;
  color: var(--color-text);
}

.step-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: var(--color-primary);
  color: white;
  border-radius: 50%;
  font-weight: 700;
  font-size: 0.9rem;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.product-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.product-card:hover {
  border-color: var(--color-primary);
  background-color: rgba(6, 182, 212, 0.08);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(6, 182, 212, 0.15);
}

.product-card.selected {
  border-color: var(--color-primary);
  background-color: rgba(6, 182, 212, 0.12);
  box-shadow: 0 4px 12px rgba(6, 182, 212, 0.2);
}

.product-icon {
  font-size: 2.5rem;
}

.product-name {
  font-weight: 600;
  color: var(--color-text);
  text-align: center;
  font-size: 0.95rem;
}

.product-price {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-primary);
}

.variants-panel {
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: 10px;
  padding: 20px;
  margin-top: 20px;
}

.variants-panel h3 {
  color: var(--color-text);
  margin-bottom: 16px;
  font-size: 1.1rem;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  color: var(--color-text);
  font-weight: 600;
  margin-bottom: 8px;
  font-size: 0.95rem;
}

.variant-options {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.variant-options button {
  background-color: var(--color-surface);
  color: white;
  border: 2px solid white;
  padding: 8px 14px;
  cursor: pointer;
  border-radius: 6px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.variant-options button:hover {
  border-color: white;
  background-color: rgba(255, 255, 255, 0.08);
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quantity-display {
  min-width: 40px;
  text-align: center;
  color: var(--color-text);
  font-weight: 600;
}

.price-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(6, 182, 212, 0.08);
  padding: 12px 16px;
  border-radius: 8px;
  margin: 16px 0;
  border: 1px solid var(--color-primary);
}

.price-label {
  color: var(--color-text);
  font-weight: 600;
}

.price-value {
  color: var(--color-primary);
  font-weight: 700;
  font-size: 1.2rem;
}

/* === ESTILOS DEL LOADER === */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  min-height: 400px;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(6, 182, 212, 0.2);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 24px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-title {
  color: var(--color-text);
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 12px;
}

.loading-subtitle {
  color: rgba(230, 238, 248, 0.7);
  font-size: 1rem;
  line-height: 1.6;
  max-width: 500px;
  margin-bottom: 32px;
}

.loading-progress {
  width: 100%;
  max-width: 400px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(6, 182, 212, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary), var(--color-accent));
  animation: progress 2s ease-in-out infinite;
  border-radius: 4px;
}

@keyframes progress {
  0% { width: 0%; }
  50% { width: 70%; }
  100% { width: 0%; }
}

.progress-text {
  color: rgba(230, 238, 248, 0.6);
  font-size: 0.9rem;
  font-style: italic;
}
</style>