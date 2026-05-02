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
import { useApi } from '../composables/useApi.js'

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
    const { createPayment } = useApi()
    const data = await createPayment({
      order_id: props.order.order_id,
      producto: props.producto.nombre,
      precio: props.order.precio_total,
      cantidad: props.order.cantidad,
    })

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
  --color-warning: #f39c12;
}

.checkout-panel {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: 12px;
  box-shadow: 0 6px 18px rgba(2, 6, 23, 0.6);
}

.section-title {
  font-size: 1.8rem;
  color: var(--color-primary);
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-badge {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: white;
  border-radius: 50%;
  font-weight: 700;
}

.checkout-layout {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.order-summary {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1.5rem;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.summary-image {
  flex-shrink: 0;
}

.summary-thumb {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
  border: 2px solid var(--color-border);
}

.summary-details {
  flex: 1;
}

.summary-details h3 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
  color: var(--color-text);
}

.summary-color,
.summary-qty {
  font-size: 0.95rem;
  color: var(--color-text-secondary);
  margin: 0.25rem 0;
}

.summary-price {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-primary);
}

.payment-methods {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1rem;
}

.payment-label {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  margin-bottom: 0.5rem;
}

.payment-icons {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.payment-badge {
  padding: 0.5rem 1rem;
  background: rgba(6, 182, 212, 0.1);
  border: 1px solid var(--color-primary);
  border-radius: 6px;
  font-size: 0.85rem;
  color: var(--color-primary);
  font-weight: 600;
}

.btn {
  width: 100%;
  padding: 1rem;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(6, 182, 212, 0.3);
}

.btn-pay {
  padding: 1.25rem;
  font-size: 1.2rem;
}

.btn-mercadopago {
  background: linear-gradient(135deg, #009ee3, #007bb6);
}

.btn-mercadopago:hover:not(:disabled) {
  background: linear-gradient(135deg, #007bb6, #005f8f);
}

.btn-whatsapp {
  background: #25d366;
  color: white;
}

.btn-whatsapp:hover {
  background: #1da851;
  transform: translateY(-2px);
}

.alert {
  padding: 1rem;
  border-radius: 8px;
  font-size: 0.95rem;
  text-align: center;
}

.alert-success {
  background: rgba(39, 174, 96, 0.1);
  border: 1px solid var(--color-success);
  color: var(--color-success);
}

.alert-error {
  background: rgba(255, 107, 107, 0.1);
  border: 1px solid var(--color-error);
  color: var(--color-error);
}

.alert-warning {
  background: rgba(243, 156, 18, 0.1);
  border: 1px solid var(--color-warning);
  color: var(--color-warning);
}

@media (max-width: 768px) {
  .checkout-panel {
    padding: 1.5rem;
  }

  .summary-item {
    flex-direction: column;
    text-align: center;
  }

  .summary-price {
    font-size: 1.3rem;
  }
}
</style>
