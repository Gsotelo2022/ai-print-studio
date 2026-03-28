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
    <h2 class="section-title">
      <span class="step-badge">2</span>
      Selecciona el producto
    </h2>

    <!-- Grilla de productos -->
    <div class="products-grid">
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
})

// --- Eventos ---
const emit = defineEmits(['product-selected'])

// --- Estado local ---
const selectedKey = ref(null)   // Key del producto seleccionado ('camiseta', 'taza', etc.)
const talle = ref('M')
const color = ref('Blanco')
const cantidad = ref(1)

// Opciones
const talles = ['S', 'M', 'L', 'XL', 'XXL']
const colores = ['Blanco', 'Negro', 'Gris', 'Azul']

// Iconos para cada producto
const productIcons = {
  camiseta: '👕',
  taza:     '☕',
  sudadera: '🧥',
  cojin:    '🛋️',
  mochila:  '🎒',
  gorra:    '🧢',
}

// --- Computed ---
// El producto actualmente seleccionado (objeto completo)
const currentProduct = computed(() => {
  return selectedKey.value ? props.productos[selectedKey.value] : null
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
  talle.value = 'M'
  color.value = 'Blanco'
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

function formatPrice(price) {
  return new Intl.NumberFormat('es-AR').format(price)
}
</script>
