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
      Confirma tu pedido
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
import { useApi } from '../composables/useApi.js'

const props = defineProps({
  order:     { type: Object, required: true },
  imagenUrl: { type: String, required: true },
  producto:  { type: Object, required: true },
})

const { loading, error, createPayment } = useApi()

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
  try {
    // Llamar al backend para crear preferencia en MercadoPago
    const data = await createPayment(props.order.order_id)

    // Redirigir al usuario a MercadoPago
    // data.payment_url es el init_point de MercadoPago
    // En testing, usar data.sandbox_url
    const payUrl = data.sandbox_url || data.payment_url
    window.location.href = payUrl

  } catch (err) {
    console.error('Error creando pago:', err)
  }
}

function sendWhatsApp() {
  const numero = '5491134696400' 
  const text = `Hola! Quiero confirmar mi pedido #${props.order.order_id}\n` +
    `${props.producto.nombre} x${props.producto.cantidad}\n` +
    `Total: $${formatPrice(props.order.precio_total)}`
    const url = `https://wa.me/${numero}?text=${encodeURIComponent(texto)}`
  window.open(url, '_blank')
}

function formatPrice(price) {
  return new Intl.NumberFormat('es-AR').format(price)
}
</script>
