<template>
  <div class="product-selector">
    <!-- Header -->
    <div class="section-header">
      <h2 class="section-title">
        <span class="step-badge">3</span>
        Seleccion&#225; tu producto
      </h2>
      <button @click="$emit('go-back')" class="btn btn-back">&#8592; Volver</button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <h3>Cargando productos...</h3>
      <p class="loading-hint">Consultando cat&#225;logo disponible</p>
    </div>

    <!-- Sin productos -->
    <div v-else-if="productList.length === 0" class="empty-state">
      <p>No hay productos disponibles en este momento.</p>
      <button @click="$emit('go-back')" class="btn btn-back">Volver</button>
    </div>

    <!-- Lista de productos -->
    <div v-else>
      <div class="products-list">
        <div
          v-for="prod in productList"
          :key="prod.id_producto"
          class="product-card"
          :class="{ selected: selectedProductId === prod.id_producto }"
          @click="selectProduct(prod)"
        >
          <div class="product-icon">{{ getIcon(prod.nombre) }}</div>
          <div class="product-info">
            <h3 class="product-name">{{ prod.nombre }}</h3>
            <p class="product-desc" v-if="prod.descripcion">{{ prod.descripcion }}</p>
            <span class="product-price">Desde ${{ formatPrice(prod.precio_desde) }}</span>
          </div>
        </div>
      </div>

      <!-- Panel de variantes -->
      <div v-if="selectedProduct" class="variants-panel">
        <h3>Personaliz&#225; tu {{ selectedProduct.nombre }}</h3>

        <!-- Talle -->
        <div v-if="availableTalles.length > 0" class="form-group">
          <label class="form-label">Talle:</label>
          <div class="variant-options">
            <button
              v-for="t in availableTalles"
              :key="t"
              @click="talle = t"
              class="btn btn-back"
              :class="{ active: talle === t }"
            >{{ t }}</button>
          </div>
        </div>

        <!-- Color -->
        <div v-if="availableColores.length > 0" class="form-group">
          <label class="form-label">Color:</label>
          <div class="variant-options">
            <button
              v-for="c in availableColores"
              :key="c"
              @click="color = c"
              class="btn btn-back"
              :class="{ active: color === c }"
            >{{ c }}</button>
          </div>
        </div>

        <!-- Cantidad -->
        <div class="form-group">
          <label class="form-label">Cantidad:</label>
          <div class="quantity-control">
            <button @click="cantidad > 1 && cantidad--" class="btn btn-back">&#8722;</button>
            <span class="qty-display">{{ cantidad }}</span>
            <button @click="cantidad < 10 && cantidad++" class="btn btn-back">+</button>
          </div>
        </div>

        <!-- Precio -->
        <div class="price-summary">
          <span class="price-label">Total:</span>
          <span class="price-value">${{ formatPrice(precioTotal) }}</span>
        </div>

        <!-- Continuar -->
        <button @click="confirmSelection" :disabled="!canContinue" class="btn btn-back">
          Continuar &#8594;
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  productos: { type: [Array, Object], required: true },
  loading: { type: Boolean, default: false },
  loaded: { type: Boolean, default: false }
})

const emit = defineEmits(['product-selected', 'go-back'])

const selectedProductId = ref(null)
const talle = ref(null)
const color = ref(null)
const cantidad = ref(1)

// Normalizar productos: puede venir como array o como objeto
const productList = computed(() => {
  if (Array.isArray(props.productos)) return props.productos
  if (typeof props.productos === 'object' && props.productos !== null) {
    return Object.entries(props.productos).map(([key, val]) => ({
      ...val,
      _key: key,
      id_producto: val.id_producto || key
    }))
  }
  return []
})

const selectedProduct = computed(() => {
  if (!selectedProductId.value) return null
  return productList.value.find(p => p.id_producto === selectedProductId.value) || null
})

// Extraer talles y colores unicos de las variantes
const availableTalles = computed(() => {
  if (!selectedProduct.value?.variantes) return []
  const talles = new Set()
  selectedProduct.value.variantes.forEach(v => {
    const t = v.atributos?.talle?.valor || v.talle
    if (t) talles.add(t)
  })
  return Array.from(talles)
})

const availableColores = computed(() => {
  if (!selectedProduct.value?.variantes) return []
  const colores = new Set()
  selectedProduct.value.variantes.forEach(v => {
    const c = v.atributos?.color?.valor || v.color
    if (c) colores.add(c)
  })
  return Array.from(colores)
})

const precioTotal = computed(() => {
  const variante = findVariante()
  if (variante) return variante.precio * cantidad.value
  if (selectedProduct.value) return selectedProduct.value.precio_desde * cantidad.value
  return 0
})

const canContinue = computed(() => {
  if (!selectedProduct.value) return false
  if (availableTalles.value.length > 0 && !talle.value) return false
  if (availableColores.value.length > 0 && !color.value) return false
  return cantidad.value > 0
})

function selectProduct(prod) {
  selectedProductId.value = prod.id_producto
  talle.value = null
  color.value = null
  cantidad.value = 1
}

function findVariante() {
  if (!selectedProduct.value?.variantes) return null
  return selectedProduct.value.variantes.find(v => {
    const vTalle = v.atributos?.talle?.valor || v.talle || null
    const vColor = v.atributos?.color?.valor || v.color || null
    const talleOk = availableTalles.value.length === 0 || vTalle === talle.value
    const colorOk = availableColores.value.length === 0 || vColor === color.value
    return talleOk && colorOk
  })
}

function confirmSelection() {
  if (!canContinue.value) return
  const variante = findVariante()

  if (!variante) {
    alert('No se encontro una variante con esa combinacion. Proba otra.')
    return
  }

  emit('product-selected', {
    id_producto: selectedProduct.value.id_producto,
    id_variante: variante.id_variante,
    nombre: selectedProduct.value.nombre,
    talle: talle.value,
    color: color.value,
    cantidad: cantidad.value,
    precio: variante.precio,
    precioTotal: variante.precio * cantidad.value
  })
}

function getIcon(nombre) {
  const n = (nombre || '').toLowerCase()
  if (n.includes('remera') || n.includes('camiseta')) return String.fromCodePoint(0x1F455)
  if (n.includes('taza')) return String.fromCodePoint(0x2615)
  if (n.includes('buzo') || n.includes('sudadera')) return String.fromCodePoint(0x1F9E5)
  if (n.includes('gorra')) return String.fromCodePoint(0x1F9E2)
  if (n.includes('bolsa') || n.includes('tote')) return String.fromCodePoint(0x1F45C)
  if (n.includes('mochila')) return String.fromCodePoint(0x1F392)
  return String.fromCodePoint(0x1F4E6)
}

function formatPrice(p) {
  return new Intl.NumberFormat('es-AR').format(p || 0)
}
</script>

<style scoped>
.product-selector { padding: 20px 0; }

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.4rem;
  color: var(--color-text, #e6eef8);
}

.step-badge {
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  background: var(--color-primary, #06b6d4);
  color: white; border-radius: 50%; font-weight: 700;
}

.btn-volver {
  padding: 8px 16px;
  background: transparent;
  border: 2px solid var(--color-primary, #06b6d4);
  color: var(--color-primary, #06b6d4);
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}
.btn-volver:hover { background: var(--color-primary, #06b6d4); color: white; }

.products-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.product-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: var(--color-surface, #0f1724);
  border: 2px solid var(--color-border, rgba(255,255,255,0.06));
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}
.product-card:hover {
  border-color: var(--color-primary, #06b6d4);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(6, 182, 212, 0.15);
}
.product-card.selected {
  border-color: var(--color-primary, #06b6d4);
  background: rgba(6, 182, 212, 0.1);
}

.product-icon { font-size: 2rem; }
.product-info { flex: 1; }
.product-name {
  font-size: 1rem; font-weight: 700;
  color: var(--color-text, #e6eef8); margin: 0 0 4px;
}
.product-desc {
  font-size: 0.8rem;
  color: var(--color-text-secondary, #9aa6b2); margin: 0 0 4px;
}
.product-price {
  font-size: 0.9rem; font-weight: 600;
  color: var(--color-primary, #06b6d4);
}

.variants-panel {
  background: var(--color-surface, #0f1724);
  border: 2px solid var(--color-border, rgba(255,255,255,0.06));
  border-radius: 10px;
  padding: 24px;
}
.variants-panel h3 {
  color: var(--color-text, #e6eef8); margin: 0 0 20px;
}

.form-group { margin-bottom: 16px; }
.form-label {
  display: block; font-weight: 600;
  color: var(--color-text, #e6eef8); margin-bottom: 8px;
}

.variant-options { display: flex; gap: 8px; flex-wrap: wrap; }
.variant-btn {
  padding: 8px 16px;
  background: var(--color-bg, #071226);
  border: 2px solid var(--color-border, rgba(255,255,255,0.06));
  color: var(--color-text, #e6eef8);
  border-radius: 6px;
  cursor: pointer; font-weight: 600; transition: all 0.2s;
}
.variant-btn:hover { border-color: var(--color-primary, #06b6d4); }
.variant-btn.active {
  background: var(--color-primary, #06b6d4);
  border-color: var(--color-primary, #06b6d4);
  color: white;
}

.quantity-control { display: flex; align-items: center; gap: 12px; }
.qty-btn {
  width: 36px; height: 36px;
  background: var(--color-bg, #071226);
  border: 2px solid var(--color-border, rgba(255,255,255,0.06));
  color: var(--color-text, #e6eef8);
  border-radius: 8px; cursor: pointer;
  font-size: 1.2rem; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.qty-btn:hover { border-color: var(--color-primary, #06b6d4); }
.qty-display {
  font-size: 1.2rem; font-weight: 700;
  color: var(--color-text, #e6eef8);
  min-width: 30px; text-align: center;
}

.price-summary {
  display: flex; justify-content: space-between; align-items: center;
  background: rgba(6, 182, 212, 0.08);
  padding: 14px 18px; border-radius: 8px;
  margin: 20px 0;
  border: 1px solid var(--color-primary, #06b6d4);
}
.price-label { font-weight: 600; color: var(--color-text, #e6eef8); }
.price-value { font-size: 1.4rem; font-weight: 800; color: var(--color-primary, #06b6d4); }

.btn-continue {
  width: 100%; padding: 14px;
  background: var(--color-primary, #06b6d4);
  color: white; border: none; border-radius: 8px;
  font-size: 1rem; font-weight: 700; cursor: pointer;
  transition: all 0.3s;
}
.btn-continue:hover:not(:disabled) {
  background: var(--color-primary-dark, #0b7285);
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(6, 182, 212, 0.3);
}
.btn-continue:disabled { opacity: 0.4; cursor: not-allowed; }

.loading-container {
  display: flex; flex-direction: column;
  align-items: center; padding: 60px 20px; text-align: center;
}
.loading-spinner {
  width: 48px; height: 48px;
  border: 4px solid var(--color-border, rgba(255,255,255,0.06));
  border-top-color: var(--color-primary, #06b6d4);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-hint { color: var(--color-text-secondary, #9aa6b2); margin-top: 8px; }

.empty-state {
  text-align: center; padding: 40px;
  color: var(--color-text-secondary, #9aa6b2);
}
.btn-primary {
  padding: 10px 24px;
  background: var(--color-primary, #06b6d4);
  color: white; border: none; border-radius: 8px;
  cursor: pointer; font-weight: 600; margin-top: 12px;
}

@media (max-width: 768px) {
  .products-list { grid-template-columns: 1fr; }
}
</style>
