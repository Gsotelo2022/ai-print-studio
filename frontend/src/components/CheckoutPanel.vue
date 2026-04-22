<!--
  ============================================
  CheckoutPanel.vue - Paso 4: Confirmar y Pagar
  ============================================
  Último paso: muestra resumen del pedido y redirige a MercadoPago.

  COMUNICACIÓN:
    - Recibe: order (datos del pedido), imagenUrl, producto
    - No emite eventos (es el último paso)

  FLUJO:
    Muestra resumen → click "Pagar con MercadoPago"
    → useApi().createPayment(orderId) → POST /api/create-payment.php
    → PHP cURL → MercadoPago API → devuelve init_point (URL de pago)
    → Redirigimos al usuario a esa URL
    → El usuario paga en MercadoPago
    → MercadoPago redirige de vuelta a nuestra app
-->
<template>
  <div class="checkout-panel">
    <h2 class="section-title">
      <span class="step-badge">5</span>
      Paga o envía por WhatsApp
    </h2>

    <!-- Resumen del pedido -->
    <div class="checkout-layout">
      <div class="order-summary">
        <div class="summary-item">
          <div class="summary-image">
            <img :src="imagenUrl" alt="Tu diseño" class="summary-thumb" />
          </div>
          <div class="summary-details">
            <h3>{{ producto.nombre }}
              <span v-if="producto.talle">({{ producto.talle }})</span>
            </h3>
            <p class="summary-color">Color: {{ producto.color }}</p>
            <p class="summary-qty">Cantidad: {{ producto.cantidad }}</p>
          </div>
          <div class="summary-price">
            ${{ formatPrice(order.precio_total) }}
          </div>
        </div>
      </div>

      <!-- Métodos de pago -->
      <div class="payment-methods">
        <p class="payment-label">Pago:</p>
        <div class="payment-icons">
          <span class="payment-badge">MercadoPago</span>
          <span class="payment-badge">Visa</span>
          <span class="payment-badge">MasterCard</span>
        </div>
      </div>

      <!-- Botón de pago MercadoPago -->
      <button
        @click="pay"
        :disabled="loading"
        class="btn btn-primary btn-pay btn-mercadopago"
      >
        {{ loading ? '⏳ Conectando con MercadoPago...' : '💳 Pagar ahora con Mercado Pago' }}
      </button>

      <!-- Envío WhatsApp -->
      <button class="btn btn-whatsapp" @click="sendWhatsApp">
        ✅ Enviar por WhatsApp
      </button>

      <!-- Estado del pago (si vuelve de MercadoPago) -->
      <div v-if="paymentStatus" class="alert" :class="paymentStatusClass">
        {{ paymentMessage }}
      </div>

      <!-- Error -->
      <div v-if="error" class="alert alert-error">
        ❌ {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'

const props = defineProps({
  order:     { type: Object, required: true },
  imagenUrl: { type: String, required: true },
  producto:  { type: Object, required: true },
})

const loading = ref(false)
const error = ref(null)
const paymentStatus = ref(null)

// --- Verificar si el usuario vuelve de MercadoPago ---
// MercadoPago redirige con ?payment=success|failure|pending
onMounted(() => {
  const params = new URLSearchParams(window.location.search)
  const status = params.get('payment')
  if (status) {
    paymentStatus.value = status
  }
})

const paymentMessage = computed(() => {
  const messages = {
    success: '✅ ¡Pago aprobado! Tu pedido está en camino.',
    failure: '❌ El pago no pudo completarse. Intentá de nuevo.',
    pending: '⏳ Tu pago está pendiente de confirmación.',
  }
  return messages[paymentStatus.value] || ''
})

const paymentStatusClass = computed(() => {
  const classes = {
    success: 'alert-success',
    failure: 'alert-error',
    pending: 'alert-warning',
  }
  return classes[paymentStatus.value] || ''
})

// --- Pagar con MercadoPago ---
async function pay() {
  if (!props.order.order_id) {
    console.error('❌ Error: No hay order_id')
    return
  }

  try {
    // Llamar al backend para crear preferencia en MercadoPago
    const response = await fetch('http://localhost:8080/api/create-payment.php', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        order_id: props.order.order_id,
        producto: props.producto.nombre,
        precio: props.order.precio_total,
        cantidad: props.order.cantidad
      })
    })

    const data = await response.json()

    // Redirigir al usuario a MercadoPago
    // En testing usar sandbox_url, en producción usar init_point
    const payUrl = data.sandbox_url || data.payment_url || data.init_point
    if (!payUrl) {
      throw new Error('No se recibió URL de pago de MercadoPago')
    }
    window.location.href = payUrl

  } catch (err) {
    console.error('Error creando pago:', err)
    error.value = err.message
  }
}

function sendWhatsApp() {
  const numero = '5491134696400'
  const numeroPedido = props.order?.order_id || props.order?.id_pedido || 'PENDIENTE'
  const cantidad = props.producto?.cantidad || 1
  const producto = props.producto?.nombre || 'Producto'
  const color = props.producto?.color || 'N/A'
  const talle = props.producto?.talle || 'Único'
  const precioTotal = props.order?.precio_total || props.producto?.precioTotal || 0
  
  const text = `Hola, mi n° de pedido es #${numeroPedido}.

Detalle: ${cantidad} ${producto}${cantidad > 1 ? 's' : ''} ${color} con talle${talle === 'Único' ? '' : 's'} ${talle}.

Precio total: $${formatPrice(precioTotal)}`

  // Copiar al portapapeles
  navigator.clipboard.writeText(text).then(() => {
    alert('📋 Mensaje copiado al portapapeles!\n\nAhora:\n1. Se abrirá WhatsApp\n2. Pega el mensaje\n3. Adjunta la FOTO\n4. Envía')
    
    // Abrir WhatsApp Web
    const url = `https://wa.me/${numero}`
    window.open(url, '_blank')
  }).catch(err => {
    // Si falla copiar, abre WhatsApp con el texto en la URL
    console.log('No se puede copiar al portapapeles:', err)
    const url = `https://wa.me/${numero}?text=${encodeURIComponent(text)}`
    window.open(url, '_blank')
  })
}

function formatPrice(price) {
  return new Intl.NumberFormat('es-AR').format(price)
}
</script>
