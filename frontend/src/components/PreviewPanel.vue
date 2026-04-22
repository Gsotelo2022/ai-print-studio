<template>
  <div class="preview-panel">
    <!-- Header con título y botón volver -->
    <div class="section-header">
      <h2 class="section-title">
        <span class="step-badge">4</span>
        Vista previa del estampado
      </h2>
      <button @click="goBack" class="btn-volver">
        ← Volver
      </button>
    </div>

    <div class="preview-layout">
      
      <!-- PREVIEW DEL PRODUCTO -->
      <div class="preview-mockup">
        <div class="mockup-container">

          <div class="mockup-product">

            <!-- Imagen base del producto -->
            <img
              :src="getProductImage(producto.key)"
              class="mockup-base"
            />

            <!-- Sticker -->
            <img
              :src="imagenUrl"
              :alt="'Diseño: ' + prompt"
              class="mockup-design"
              :style="stickerStyle"
              @mousedown="startDrag"
            />

          </div>

          <p class="mockup-label">
            {{ producto.nombre }} Personalizada
          </p>

          <!-- Zoom Controls -->
          <div class="zoom-controls">
            <button 
              @click="zoomOut" 
              :disabled="imageZoom <= 0.5"
              class="btn-zoom"
            >
              −
            </button>
            <span class="zoom-display">{{ (imageZoom * 100).toFixed(0) }}%</span>
            <button 
              @click="zoomIn" 
              :disabled="imageZoom >= 3.0"
              class="btn-zoom"
            >
              +
            </button>
            <button 
              @click="resetZoom"
              class="btn-zoom-reset"
            >
              Restablecer
            </button>
          </div>
        </div>
      </div>

      <!-- DETALLES -->
      <div class="preview-details">

        <div v-if="producto.talle" class="detail-row">
          <span class="detail-label">Talle:</span>
          <div class="variant-pills">
            <span
              v-for="t in talles"
              :key="t"
              class="pill"
              :class="{ active: t === producto.talle }"
            >
              {{ t }}
            </span>
          </div>
        </div>

        <div class="detail-row">
          <span class="detail-label">Color:</span>
          <div class="variant-pills">
            <span class="pill active">
              {{ producto.color }}
            </span>
          </div>
        </div>

        <div class="detail-row">
          <span class="detail-label">Cantidad:</span>
          <span class="detail-value">
            {{ producto.cantidad }}
          </span>
        </div>

        <!-- PRECIO -->
        <div class="price-box">
          <div class="price-row">
            <span>{{ producto.nombre }}</span>
            <span>${{ formatPrice(producto.precio) }} c/u</span>
          </div>

          <div class="price-row price-total">
            <span>Total</span>
            <span>${{ formatPrice(producto.precioTotal) }}</span>
          </div>
        </div>

        <!-- ESTADO DEL PEDIDO -->
        <div v-if="!orderCreated" class="order-status">
          <p class="status-label">⏳ Pedido no confirmado aún</p>
          <p class="status-help">Confirma tu pedido para continuar con el pago</p>
        </div>
        <div v-else class="order-status success">
          <p class="status-label">✅ Pedido confirmado</p>
          <p class="status-help">ID: <strong>#{{ orderId }}</strong></p>
        </div>

        <!-- 🔥 BOTÓN CONFIRMAR PEDIDO -->
        <button
          v-if="!orderCreated"
          @click="confirmarPedido"
          :disabled="creatingOrder"
          class="btn btn-primary btn-confirm-order"
        >
          {{ creatingOrder ? '⏳ Guardando pedido...' : '✅ Confirmar Pedido' }}
        </button>

        <!-- BOTONES DE PAGO (solo si el pedido está confirmado) -->
        <template v-if="orderCreated">
          <!-- 🔥 BOTÓN MERCADO PAGO -->
          <button
            @click="pagar"
            :disabled="loadingPago"
            class="btn btn-primary btn-pay"
          >
            {{ loadingPago ? '⏳ Redirigiendo a Mercado Pago...' : '💳 Pagar con Mercado Pago' }}
          </button>

          <!-- WHATSAPP -->
          <button class="btn btn-whatsapp" @click="sendWhatsApp">
            📲 Enviar por WhatsApp
          </button>
        </template>

        <div class="shipping-info">
          <span>Envío: 📦 🏠</span>
        </div>

        <div v-if="errorPago" class="alert alert-error">
          ❌ {{ errorPago }}
        </div>
        <div v-if="errorOrder" class="alert alert-error">
          ❌ {{ errorOrder }}
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { reactive, computed, ref, onMounted } from 'vue'

// --- Props ---
const props = defineProps({
  imagenUrl: { type: String, required: true },
  producto:  { type: Object, required: true },
  prompt:    { type: String, required: true },
  userId:    { type: Number, required: true }, // ID del usuario autenticado
})

// --- Eventos ---
const emit = defineEmits(['confirm-order', 'go-back'])

// Zoom
const imageZoom = ref(1)

// Estados
const orderCreated = ref(false)
const orderId = ref(null)
const creatingOrder = ref(false)
const errorOrder = ref(null)
const loadingPago = ref(false)
const errorPago = ref(null)

// Talles disponibles
const talles = ['S', 'M', 'L', 'XL', 'XXL']

// -----------------------------
// 🎯 POSICIÓN DEL STICKER
// -----------------------------
const position = reactive({ x: 100, y: 100 })
const drag = reactive({ active: false, startX: 0, startY: 0 })

const stickerStyle = computed(() => ({
  position: 'absolute',
  top: position.y + 'px',
  left: position.x + 'px',
  width: '120px',
  cursor: 'move',
  transform: `scale(${imageZoom.value})`
}))

function startDrag(e) {
  drag.active = true
  drag.startX = e.clientX
  drag.startY = e.clientY

  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', stopDrag)
}

function onMove(e) {
  if (!drag.active) return

  const dx = e.clientX - drag.startX
  const dy = e.clientY - drag.startY

  position.x += dx
  position.y += dy

  drag.startX = e.clientX
  drag.startY = e.clientY
}

function stopDrag() {
  drag.active = false
  window.removeEventListener('mousemove', onMove)
  window.removeEventListener('mouseup', stopDrag)
}

// Zoom functions
function zoomIn() {
  if (imageZoom.value < 3.0) {
    imageZoom.value = Math.min(imageZoom.value + 0.2, 3.0)
  }
}

function zoomOut() {
  if (imageZoom.value > 0.5) {
    imageZoom.value = Math.max(imageZoom.value - 0.2, 0.5)
  }
}

function resetZoom() {
  imageZoom.value = 1.0
}

// -----------------------------
// 🖼 MOCKUPS
// -----------------------------
function getProductImage(key) {
  const images = {
    camiseta: '/mockups/camiseta.png',
    taza: '/mockups/taza.png',
    sudadera: '/mockups/sudadera.png',
  }
  return images[key] || '/mockups/default.png'
}

// ---------------------------------
// 📝 CONFIRMAR PEDIDO EN LA BD
// ---------------------------------
async function confirmarPedido() {
  try {
    creatingOrder.value = true
    errorOrder.value = null

    const response = await fetch('http://localhost:8000/api/create-order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: props.userId,  // NUEVO: ID del usuario autenticado
        producto: props.producto.key,
        talle: props.producto.talle || null,
        color: props.producto.color,
        cantidad: props.producto.cantidad,
        prompt: props.prompt,
        imagen_url: props.imagenUrl,
        posicion_x: position.x,
        posicion_y: position.y,
        zoom: imageZoom.value
      })
    })

    const data = await response.json()
    
    // Verificar si la respuesta fue exitosa
    if (!response.ok || !data.success) {
      throw new Error(data.error || data.data?.error || 'Error al crear el pedido')
    }

    // Extraer datos del pedido (estructura: {success: true, data: {...}})
    const orderInfo = data.data
    if (!orderInfo || !orderInfo.order_id) {
      throw new Error('No se recibió ID del pedido')
    }

    // Éxito: el pedido fue creado
    orderId.value = orderInfo.order_id
    orderCreated.value = true
    creatingOrder.value = false
    
    console.log('✅ Pedido creado:', {
      order_id: orderInfo.order_id,
      precio_total: orderInfo.precio_total
    })

    // 🔥 EMITIR EVENTO con los datos del pedido para que App.vue sepa
    emit('confirm-order', {
      order_id: orderInfo.order_id,
      precio_total: orderInfo.precio_total,
      cantidad: orderInfo.cantidad,
      producto: orderInfo.producto
    })

  } catch (err) {
    console.error('❌ Error creando pedido:', err)
    errorOrder.value = err.message || 'No se pudo crear el pedido. Intenta de nuevo.'
    creatingOrder.value = false
  }
}

// ---------------------------------
// 💳 MERCADO PAGO
// ---------------------------------
async function pagar() {
  if (!orderId.value) {
    errorPago.value = '❌ Error: No hay pedido confirmado'
    return
  }

  try {
    loadingPago.value = true
    errorPago.value = null

    const response = await fetch('http://localhost:8080/api/create-payment.php', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        order_id: orderId.value,
        producto: props.producto.nombre,
        precio: props.producto.precioTotal,
        cantidad: props.producto.cantidad
      })
    })

    const data = await response.json()
    
    if (data.success === false || data.error) {
      throw new Error(data.error?.response || data.error || 'Error en MercadoPago')
    }

    // Obtener la URL de pago
    const payUrl = data.sandbox_url || data.payment_url || data.init_point
    if (!payUrl) {
      throw new Error('No se recibió URL de Mercado Pago')
    }

    // Redirigir a Mercado Pago
    window.location.href = payUrl

  } catch (err) {
    console.error('❌ Error Mercado Pago:', err)
    errorPago.value = `❌ ${err.message || 'Error al procesar pago'}`
    loadingPago.value = false
  }
}

// ---------------------------------
// 📲 WHATSAPP
// ---------------------------------
function sendWhatsApp() {
  const cantidad = props.producto.cantidad || 1
  const producto = props.producto.nombre || 'Producto'
  const color = props.producto.color || 'N/A'
  const talle = props.producto.talle || 'Único'
  const numeroPedido = orderId.value || 'PENDIENTE'
  
  const text = `Hola, mi n° de pedido es #${numeroPedido}.

Detalle: ${cantidad} ${producto}${cantidad > 1 ? 's' : ''} ${color} con talle${talle === 'Único' ? '' : 's'} ${talle}.

Precio total: $${formatPrice(props.producto.precioTotal || 0)}`

  // Copiar al portapapeles
  navigator.clipboard.writeText(text).then(() => {
    alert('📋 Mensaje copiado al portapapeles!\n\nAhora:\n1. Se abrirá WhatsApp\n2. Pega el mensaje\n3. Adjunta la FOTO\n4. Envía')
    
    // Abrir WhatsApp Web
    const numero = '5491134696400'
    const url = `https://wa.me/${numero}`
    window.open(url, '_blank')
  }).catch(err => {
    // Si falla copiar, abre WhatsApp con el texto en la URL
    console.log('No se puede copiar al portapapeles:', err)
    const numero = '5491134696400'
    const url = `https://wa.me/${numero}?text=${encodeURIComponent(text)}`
    window.open(url, '_blank')
  })
}

function goBack() {
  emit('go-back')
}

// ---------------------------------
// 💲 FORMATO PRECIO
// ---------------------------------
function formatPrice(price) {
  return new Intl.NumberFormat('es-AR').format(price)
}

</script>

<style scoped>
.preview-layout {
  display: flex;
  gap: 40px;
  align-items: flex-start;
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
  color: #e6eef8;
  margin: 0;
}

.step-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #06b6d4;
  color: white;
  border-radius: 50%;
  font-weight: 700;
  font-size: 0.9rem;
}

.mockup-container {
  text-align: center;
}

.mockup-product {
  position: relative;
  width: 300px;
  margin: auto;
}

.mockup-base {
  width: 100%;
  display: block;
}

.mockup-design {
  position: absolute;
}

.mockup-label {
  margin-top: 10px;
  font-weight: bold;
}

.zoom-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: center;
  margin-top: 16px;
  padding: 12px;
  background: rgba(6, 182, 212, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(6, 182, 212, 0.3);
}

.btn-zoom {
  padding: 8px 12px;
  background-color: #06b6d4;
  border: 2px solid #06b6d4;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 12px;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-zoom:hover:not(:disabled) {
  background-color: #0891b2;
  border-color: #0891b2;
  transform: translateY(-2px);
}

.btn-zoom:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-zoom-reset {
  padding: 8px 12px;
  background-color: transparent;
  border: 2px solid #ffd54f;
  color: #ffd54f;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 12px;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-zoom-reset:hover {
  background-color: rgba(255, 213, 79, 0.1);
  transform: translateY(-2px);
}

.zoom-display {
  min-width: 60px;
  text-align: center;
  font-weight: 700;
  color: #ffd54f;
  font-family: 'Courier New', monospace;
  font-size: 14px;
}

.preview-details {
  flex: 1;
}

.detail-row {
  margin-bottom: 10px;
}

.variant-pills {
  display: flex;
  gap: 5px;
}

.pill {
  padding: 5px 10px;
  border-radius: 20px;
  background: #eee;
}

.pill.active {
  background: #333;
  color: white;
}

.price-box {
  margin-top: 20px;
  padding: 16px;
  background: rgba(6, 182, 212, 0.1);
  border-radius: 8px;
}

.price-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.price-total {
  font-weight: bold;
  border-top: 1px solid rgba(6, 182, 212, 0.3);
  padding-top: 8px;
  margin-top: 8px;
}

/* ESTADO DEL PEDIDO */
.order-status {
  margin-top: 20px;
  padding: 12px;
  background: rgba(255, 107, 107, 0.1);
  border-left: 4px solid #ff6b6b;
  border-radius: 6px;
  margin-bottom: 16px;
}

.order-status.success {
  background: rgba(51, 217, 178, 0.1);
  border-left-color: #33d9b2;
}

.status-label {
  font-weight: 600;
  color: #e6eef8;
  margin: 0 0 4px 0;
  font-size: 14px;
}

.status-help {
  color: #9aa6b2;
  font-size: 12px;
  margin: 0;
}

/* BOTONES */
.btn {
  width: 100%;
  margin-top: 12px;
  padding: 12px;
  cursor: pointer;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #06b6d4;
  color: white;
  border: 2px solid #06b6d4;
}

.btn-primary:hover:not(:disabled) {
  background: #0891b2;
  border-color: #0891b2;
  transform: translateY(-2px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-confirm-order {
  background: #33d9b2;
  border-color: #33d9b2;
  color: white;
}

.btn-confirm-order:hover:not(:disabled) {
  background: #22b699;
  border-color: #22b699;
}

.btn-pay {
  background: #06b6d4;
}

.btn-pay:hover:not(:disabled) {
  background: #0891b2;
}

.btn-whatsapp {
  background: #25d366;
  color: white;
  border: 2px solid #25d366;
}

.btn-whatsapp:hover:not(:disabled) {
  background: #1ea952;
  border-color: #1ea952;
  transform: translateY(-2px);
}

.shipping-info {
  margin-top: 12px;
  font-size: 12px;
  color: #9aa6b2;
}

.alert {
  margin-top: 12px;
  padding: 12px;
  border-radius: 6px;
  font-size: 12px;
}

.alert-error {
  background: rgba(255, 107, 107, 0.1);
  border-left: 4px solid #ff6b6b;
  color: #ff6b6b;
  margin-top: 10px;
  color: red;
}
</style>