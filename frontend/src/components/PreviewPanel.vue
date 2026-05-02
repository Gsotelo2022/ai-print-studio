<template>
  <div class="preview-panel">
    <!-- Header -->
    <div class="section-header">
      <h2 class="section-title">
        <span class="step-badge">4</span>
        Vista previa del estampado
      </h2>
      <button @click="goBack" class="btn-volver">← Volver</button>
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
  const startX = e.clientX
  const startY = e.clientY

  function move(ev) {
    position.x += ev.clientX - startX
    position.y += ev.clientY - startY
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
.preview-layout {
  display: flex;
  gap: 30px;
}

.mockup-product {
  position: relative;
  width: 300px;
}

.mockup-base {
  width: 100%;
}

.mockup-design {
  position: absolute;
}

.price-box {
  background: #eee;
  padding: 10px;
  margin-top: 10px;
}

.price-row {
  display: flex;
  justify-content: space-between;
}

.total {
  font-weight: bold;
}
</style>