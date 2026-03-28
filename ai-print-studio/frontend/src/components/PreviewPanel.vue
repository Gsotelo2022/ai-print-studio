<template>
  <div class="preview-panel">
    <h2 class="section-title">
      <span class="step-badge">3</span>
      Vista previa del estampado
    </h2>

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

        <!-- 🔥 BOTÓN MERCADO PAGO -->
        <button
          @click="pagar"
          :disabled="loadingPago"
          class="btn btn-primary btn-pay"
        >
          {{ loadingPago ? '⏳ Redirigiendo...' : '💳 Pagar con Mercado Pago' }}
        </button>

        <!-- WHATSAPP -->
        <button class="btn btn-whatsapp" @click="sendWhatsApp">
          📲 Enviar por WhatsApp
        </button>

        <div class="shipping-info">
          <span>Envío: 📦 🏠</span>
        </div>

        <div v-if="errorPago" class="alert alert-error">
          ❌ {{ errorPago }}
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { reactive, computed, ref } from 'vue'

// --- Props ---
const props = defineProps({
  imagenUrl: { type: String, required: true },
  producto:  { type: Object, required: true },
  prompt:    { type: String, required: true },
})

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
  cursor: 'move'
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

// -----------------------------
// 💳 MERCADO PAGO
// -----------------------------
const loadingPago = ref(false)
const errorPago = ref(null)

async function pagar() {
  try {
    loadingPago.value = true
    errorPago.value = null

    const res = await fetch('http://localhost/ai-print-studio/backend/api/create-payment.php', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        producto: props.producto.nombre,
        precio: props.producto.precio,
        cantidad: props.producto.cantidad
      })
    })

    const data = await res.json()
    console.log('RESPUESTA BACKEND:', data)

    if (!data.init_point) {
      throw new Error('No se recibió link de pago')
    }

    // 🔥 REDIRECCIÓN
    window.location.href = data.init_point

  } catch (err) {
    console.error(err)
    errorPago.value = 'Error al iniciar pago'
  } finally {
    loadingPago.value = false
  }
}

// -----------------------------
// 📲 WHATSAPP
// -----------------------------
function sendWhatsApp() {
  const text = `🧾 Nuevo pedido AI Print Studio

👕 Producto: ${props.producto.nombre}
🎨 Diseño: ${props.prompt}
📏 Talle: ${props.producto.talle || 'N/A'}
🎨 Color: ${props.producto.color}
🔢 Cantidad: ${props.producto.cantidad}
💲 Precio: $${formatPrice(props.producto.precioTotal)}

🖼️ Vista previa:
${props.imagenUrl}

¿Podemos avanzar con este pedido?`

  const url = `https://wa.me/?text=${encodeURIComponent(text)}`
  window.open(url, '_blank')
}

// -----------------------------
// 💲 FORMATO PRECIO
// -----------------------------
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
}

.price-row {
  display: flex;
  justify-content: space-between;
}

.price-total {
  font-weight: bold;
}

.btn {
  margin-top: 10px;
  padding: 10px;
  cursor: pointer;
}

.btn-primary {
  background: #2c3e50;
  color: white;
}

.btn-whatsapp {
  background: #25d366;
  color: white;
}

.alert-error {
  margin-top: 10px;
  color: red;
}
</style>