<template>
  <div class="preview-panel">
    <!-- Header -->
    <div class="section-header">
      <h2 class="section-title">
        <span class="step-badge">4</span>
        Vista previa del estampado
      </h2>
      <button @click="goBack" class="btn btn-back">← Volver</button>
    </div>

    <div class="preview-layout">
      
      <!-- MOCKUP -->
      <div class="preview-mockup">
        <div class="mockup-container">
          <div class="mockup-product">
            <img :src="getProductImage(producto.key)" class="mockup-base" />

            <img
              :src="imagenUrl"
              class="mockup-design"
              :style="stickerStyle"
              @mousedown="startDrag"
            />
          </div>

          <p class="mockup-label">
            {{ producto.nombre }} Personalizada
          </p>

          <!-- ZOOM -->
          <div class="zoom-controls">
            <button @click="zoomOut" :disabled="imageZoom <= 0.5">−</button>
            <span>{{ (imageZoom * 100).toFixed(0) }}%</span>
            <button @click="zoomIn" :disabled="imageZoom >= 3">+</button>
            <button @click="resetZoom">Reset</button>
          </div>
        </div>
      </div>

      <!-- DETALLES -->
      <div class="preview-details">

        <div class="detail-row">
          <span>Color:</span>
          <span>{{ producto.color }}</span>
        </div>

        <div class="detail-row">
          <span>Cantidad:</span>
          <span>{{ producto.cantidad }}</span>
        </div>

        <!-- PRECIO -->
        <div class="price-box">
          <div class="price-row">
            <span>{{ producto.nombre }}</span>
            <span>${{ formatPrice(producto.precio) }}</span>
          </div>

          <div v-if="cuponAplicado" class="price-row">
            <span>Subtotal</span>
            <span>${{ formatPrice(producto.precioTotal) }}</span>
          </div>

          <div v-if="cuponAplicado" class="price-row descuento">
            <span>Descuento -{{ cuponAplicado.descuento }}%</span>
            <span>-${{ formatPrice(montoDescuento) }}</span>
          </div>

          <div class="price-row total">
            <span>Total</span>
            <span>${{ formatPrice(totalConDescuento) }}</span>
          </div>
        </div>

        <!-- CUPONES -->
        <CuponesDisponibles
          v-if="!orderCreated && userId"
          :user-id="userId"
          @cupon-aplicado="onCuponAplicado"
          @cupon-removido="onCuponRemovido"
        />

        <!-- ESTADO -->
        <div v-if="!orderCreated">⏳ Pedido no confirmado</div>
        <div v-else>✅ Pedido #{{ orderId }}</div>

        <!-- CONFIRMAR -->
        <button v-if="!orderCreated" @click="confirmarPedido">
          Confirmar Pedido
        </button>

        <!-- PAGAR -->
        <button v-if="orderCreated" @click="pagar">
          Pagar
        </button>

        <!-- ERROR -->
        <div v-if="errorOrder">❌ {{ errorOrder }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import CuponesDisponibles from './CuponesDisponibles.vue'
import { useApi } from '../composables/useApi.js'

// Props
const props = defineProps({
  imagenUrl: String,
  producto: Object,
  prompt: String,
  userId: Number
})

const emit = defineEmits(['confirm-order', 'go-back'])

// Estado
const orderCreated = ref(false)
const orderId = ref(null)
const errorOrder = ref(null)

const cuponAplicado = ref(null)
const imageZoom = ref(1)

// Posición sticker
const position = reactive({ x: 100, y: 100 })

const stickerStyle = computed(() => ({
  position: 'absolute',
  top: position.y + 'px',
  left: position.x + 'px',
  transform: `scale(${imageZoom.value})`,
  width: '120px'
}))

// 🎟 CUPONES
const montoDescuento = computed(() => {
  if (!cuponAplicado.value) return 0
  return (props.producto.precioTotal * cuponAplicado.value.descuento) / 100
})

const totalConDescuento = computed(() => {
  return props.producto.precioTotal - montoDescuento.value
})

function onCuponAplicado(c) {
  cuponAplicado.value = c
}

function onCuponRemovido() {
  cuponAplicado.value = null
}

// 🧠 CONFIRMAR PEDIDO (CORREGIDO)
async function confirmarPedido() {
  try {
    errorOrder.value = null

    const { createOrder } = useApi()

    const payload = {
      user_id: props.userId,
      items: [
        {
          id_variante: props.producto.id_variante,
          cantidad: props.producto.cantidad,
          archivo_diseno: props.imagenUrl,
          posicion_x: position.x,
          posicion_y: position.y,
          zoom: imageZoom.value
        }
      ],
      codigo_cupon: cuponAplicado.value?.codigo || null
    }

    const order = await createOrder(payload)

    orderId.value = order.order_id
    orderCreated.value = true

    emit('confirm-order', order)

  } catch (err) {
    errorOrder.value = err.message
  }
}

// 💳 PAGO
async function pagar() {
  const { createPayment } = useApi()
  const data = await createPayment({ order_id: orderId.value })
  window.location.href = data.init_point
}

// UTIL
function formatPrice(p) {
  return new Intl.NumberFormat('es-AR').format(p)
}

function getProductImage() {
  return '/mockups/camiseta.png'
}

function zoomIn() { imageZoom.value += 0.2 }
function zoomOut() { imageZoom.value -= 0.2 }
function resetZoom() { imageZoom.value = 1 }

function startDrag(e) {
  let lastX = e.clientX
  let lastY = e.clientY

  function move(ev) {
    position.x += ev.clientX - lastX
    position.y += ev.clientY - lastY
    lastX = ev.clientX
    lastY = ev.clientY
  }

  function stop() {
    window.removeEventListener('mousemove', move)
    window.removeEventListener('mouseup', stop)
  }

  window.addEventListener('mousemove', move)
  window.addEventListener('mouseup', stop)
}

function goBack() {
  emit('go-back')
}
</script>

<style scoped>
:root {
  --color-primary: #06b6d4;
  --color-primary-dark: #0b7285;
  --color-surface: #0f1724;
  --color-text: #e6eef8;
  --color-text-secondary: #9aa6b2;
  --color-border: rgba(255, 255, 255, 0.06);
  --color-bg: #071226;
  --color-success: #27ae60;
  --color-error: #ff6b6b;
}

.preview-panel {
  max-width: 900px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-title {
  font-size: 1.5rem;
  color: var(--color-primary);
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-badge {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: white;
  border-radius: 50%;
  font-weight: 700;
  font-size: 0.9rem;
}

.btn-volver {
  padding: 0.5rem 1rem;
  background: transparent;
  border: 2px solid var(--color-primary);
  color: var(--color-primary);
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-volver:hover {
  background: var(--color-primary);
  color: white;
}

.preview-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  align-items: start;
}

.preview-mockup {
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: 12px;
  padding: 24px;
  text-align: center;
}

.mockup-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.mockup-product {
  position: relative;
  width: 300px;
  height: 350px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 8px;
  background: var(--color-bg);
}

.mockup-base {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.mockup-design {
  cursor: move;
  user-select: none;
}

.mockup-label {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  margin-top: 8px;
}

.zoom-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.zoom-controls button {
  padding: 6px 12px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.zoom-controls button:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.zoom-controls button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.zoom-controls span {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  min-width: 40px;
  text-align: center;
}

.preview-details {
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: 12px;
  padding: 24px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text);
}

.detail-row span:first-child {
  color: var(--color-text-secondary);
}

.price-box {
  background: var(--color-bg);
  padding: 16px;
  border-radius: 8px;
  margin-top: 8px;
}

.price-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  color: var(--color-text);
  font-size: 0.95rem;
}

.price-row.total {
  font-weight: 700;
  font-size: 1.2rem;
  color: var(--color-primary);
  border-top: 2px solid var(--color-border);
  margin-top: 8px;
  padding-top: 12px;
}

.price-row.descuento {
  color: var(--color-success);
}

.preview-details button {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  margin-top: 8px;
  background: var(--color-primary);
  color: white;
}

.preview-details button:hover {
  background: var(--color-primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(6, 182, 212, 0.3);
}

.preview-details div {
  font-size: 0.95rem;
  color: var(--color-text-secondary);
}

@media (max-width: 768px) {
  .preview-layout {
    grid-template-columns: 1fr;
  }

  .mockup-product {
    width: 100%;
    height: 280px;
  }
}
</style>