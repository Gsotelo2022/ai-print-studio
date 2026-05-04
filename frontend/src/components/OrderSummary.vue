<template>
  <div class="order-summary">
    <!-- Header -->
    <div class="section-header">
      <h2 class="section-title">
        <span class="step-badge">4</span>
        Resumen de tu pedido
      </h2>
      <button @click="$emit('go-back')" class="btn btn-back">← Volver</button>
    </div>

    <div class="summary-layout">
      <!-- Card izquierda: imagen + producto -->
      <div class="summary-card">
        <div class="image-preview">
          <img :src="imagenUrl" alt="Tu diseño" class="design-image" />
        </div>

        <div class="product-info">
          <h3 class="product-name">{{ producto.nombre }}</h3>
          <div class="product-details">
            <span v-if="producto.talle" class="detail-badge">Talle: {{ producto.talle }}</span>
            <span v-if="producto.color" class="detail-badge">Color: {{ producto.color }}</span>
            <span class="detail-badge">Cantidad: {{ producto.cantidad }}</span>
          </div>
          <div class="product-price">
            <span class="price-label">Total:</span>
            <span class="price-value">${{ formatPrice(producto.precioTotal) }}</span>
          </div>
        </div>
      </div>

      <!-- Card derecha: descripción + acciones -->
      <div class="action-card">
        <div class="description-section">
          <label class="form-label">📝 Descripción del estampado</label>
          <p class="form-hint">Indicá cómo querés que quede el estampado (posición, tamaño, etc.)</p>
          <textarea
            v-model="descripcion"
            class="description-input"
            rows="4"
            placeholder="Ej: Centrado en el pecho, tamaño mediano, sin bordes..."
          ></textarea>
        </div>

        <!-- Cupones -->
        <div v-if="userId" class="cupones-section">
          <CuponesDisponibles
            :user-id="userId"
            @cupon-aplicado="onCuponAplicado"
            @cupon-removido="onCuponRemovido"
          />
        </div>

        <!-- Precio final -->
        <div class="price-final" v-if="cuponAplicado">
          <div class="price-row">
            <span>Subtotal</span>
            <span>${{ formatPrice(producto.precioTotal) }}</span>
          </div>
          <div class="price-row descuento">
            <span>Descuento -{{ cuponAplicado.descuento }}%</span>
            <span>-${{ formatPrice(montoDescuento) }}</span>
          </div>
          <div class="price-row total">
            <span>Total</span>
            <span>${{ formatPrice(totalConDescuento) }}</span>
          </div>
        </div>

        <!-- Acciones -->
        
        <!-- Confirmación del pedido -->
        <div v-if="!pedidoConfirmado" class="confirm-section">
          <button
            @click="confirmarPedido"
            class="btn btn-back"
            :disabled="confirmando"
          >
            <span class="btn-icon">{{ confirmando ? '⏳' : '✅' }}</span>
            {{ confirmando ? 'Confirmando...' : 'Confirmar pedido' }}
          </button>
        </div>

        <div v-if="pedidoConfirmado" class="actions-section">
          <button @click="enviarWhatsApp" class="btn btn-back">
            <span class="btn-icon">📱</span>
            Enviar pedido por WhatsApp
          </button>

          <button @click="enviarWhatsAppYPagar" class="btn btn-back">
            <span class="btn-icon">💳</span>
            Enviar por WhatsApp + Pagar por MP
          </button>
        </div>

        <p class="actions-hint">
          Al enviar por WhatsApp se adjuntará la imagen y el detalle del pedido.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useApi } from '../composables/useApi.js'
import { useToast } from '../composables/useToast.js'
import CuponesDisponibles from './CuponesDisponibles.vue'

const props = defineProps({
  imagenUrl: { type: String, required: true },
  producto: { type: Object, required: true },
  userId: { type: Number, default: null }
})

const emit = defineEmits(['go-back', 'order-completed'])

const api = useApi()
const { success, error: toastError, important } = useToast()

const descripcion = ref('')
const cuponAplicado = ref(null)
const enviando = ref(false)
const confirmando = ref(false)
const pedidoConfirmado = ref(false)
const ordenCreada = ref(null)   // guarda el pedido creado al confirmar

const WHATSAPP_NUMERO = '5491134696400'

// Cupones
const montoDescuento = computed(() => {
  if (!cuponAplicado.value) return 0
  return (props.producto.precioTotal * cuponAplicado.value.descuento) / 100
})

const totalConDescuento = computed(() => {
  return props.producto.precioTotal - montoDescuento.value
})

function onCuponAplicado(c) { cuponAplicado.value = c }
function onCuponRemovido() { cuponAplicado.value = null }

// ── CONFIRMAR PEDIDO (crea en BD) ──────────────────────────
async function confirmarPedido() {
  if (!props.producto?.id_variante) {
    toastError('No se encontró la variante del producto. Volvé atrás y seleccioná el producto nuevamente.')
    return
  }

  confirmando.value = true

  try {
    const payload = {
      user_id: props.userId,
      items: [{
        id_variante: props.producto.id_variante,
        cantidad: props.producto.cantidad,
        archivo_diseno: props.imagenUrl,
        descripcion_estampado: descripcion.value
      }],
      codigo_cupon: cuponAplicado.value?.codigo || null
    }

    ordenCreada.value = await api.createOrder(payload)
    pedidoConfirmado.value = true
    success('¡Pedido confirmado! Ahora podés enviarlo por WhatsApp o pagar.')

  } catch (err) {
    toastError('Error al confirmar el pedido: ' + err.message)
  } finally {
    confirmando.value = false
  }
}

// ── CONSTRUIR MENSAJE WHATSAPP ─────────────────────────────
function buildWhatsAppMessage() {
  const orderId = ordenCreada.value?.order_id || ordenCreada.value?.id_pedido || 'NUEVO'
  const talle = props.producto.talle ? `Talle: ${props.producto.talle}` : ''
  const color = props.producto.color ? `Color: ${props.producto.color}` : ''
  const precio = cuponAplicado.value
    ? `$${formatPrice(totalConDescuento.value)} (descuento ${cuponAplicado.value.descuento}%)`
    : `$${formatPrice(props.producto.precioTotal)}`

  let msg = `🛒 *NUEVO PEDIDO #${orderId}*\n\n`
  msg += `📦 *Producto:* ${props.producto.nombre}\n`
  if (talle) msg += `📏 ${talle}\n`
  if (color) msg += `🎨 ${color}\n`
  msg += `🔢 Cantidad: ${props.producto.cantidad}\n`
  msg += `💰 *Total: ${precio}*\n`
  if (descripcion.value.trim()) {
    msg += `\n📝 *Detalle del estampado:*\n${descripcion.value.trim()}\n`
  }
  msg += `\n🖼️ La imagen del diseño se adjunta aparte.`

  return msg
}

// ── ENVIAR POR WHATSAPP ────────────────────────────────────
async function enviarWhatsApp() {
  if (enviando.value || !ordenCreada.value) return
  enviando.value = true

  try {
    const msg = buildWhatsAppMessage()
    await navigator.clipboard.writeText(msg).catch(() => {})
    const url = `https://wa.me/${WHATSAPP_NUMERO}?text=${encodeURIComponent(msg)}`
    window.open(url, '_blank')
    success('Mensaje copiado. Se abrirá WhatsApp. Pegá el mensaje, adjuntá la imagen y enviá.')
    emit('order-completed', ordenCreada.value)
  } catch (err) {
    toastError('Error al abrir WhatsApp: ' + err.message)
  } finally {
    enviando.value = false
  }
}

// ── ENVIAR POR WHATSAPP + PAGAR ────────────────────────────
async function enviarWhatsAppYPagar() {
  if (enviando.value || !ordenCreada.value) return
  enviando.value = true

  try {
    const msg = buildWhatsAppMessage()
    const orderId = ordenCreada.value?.order_id || ordenCreada.value?.id_pedido

    await navigator.clipboard.writeText(msg).catch(() => {})
    const waUrl = `https://wa.me/${WHATSAPP_NUMERO}?text=${encodeURIComponent(msg)}`
    window.open(waUrl, '_blank')

    const paymentData = await api.createPayment({
      order_id: orderId,
      producto: props.producto.nombre,
      precio: cuponAplicado.value ? totalConDescuento.value : props.producto.precioTotal,
      cantidad: props.producto.cantidad
    })

    const payUrl = paymentData.sandbox_url || paymentData.payment_url || paymentData.init_point
    if (payUrl) {
      setTimeout(() => { window.location.href = payUrl }, 2000)
    } else {
      important('Pedido enviado por WhatsApp pero no se pudo generar el link de pago. Contactá al vendedor.')
    }

    emit('order-completed', ordenCreada.value)
  } catch (err) {
    toastError('Error: ' + err.message)
  } finally {
    enviando.value = false
  }
}

function formatPrice(price) {
  return new Intl.NumberFormat('es-AR').format(price)
}
</script>

<style scoped>
.order-summary {
  max-width: 1000px;
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
  color: var(--color-primary, #06b6d4);
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
  background: var(--color-primary, #06b6d4);
  color: white;
  border-radius: 50%;
  font-weight: 700;
  font-size: 0.9rem;
}

.btn-volver {
  padding: 0.5rem 1rem;
  background: transparent;
  border: 2px solid var(--color-primary, #06b6d4);
  color: var(--color-primary, #06b6d4);
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-volver:hover {
  background: var(--color-primary, #06b6d4);
  color: white;
}

.summary-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  align-items: start;
}

.summary-card,
.action-card {
  background: var(--color-surface, #0f1724);
  border: 2px solid var(--color-border, rgba(255,255,255,0.06));
  border-radius: 12px;
  padding: 24px;
}

.image-preview {
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 20px;
  background: var(--color-bg, #071226);
  display: flex;
  align-items: center;
  justify-content: center;
  max-height: 300px;
}

.design-image {
  max-width: 100%;
  max-height: 300px;
  object-fit: contain;
}

.product-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.product-name {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--color-text, #e6eef8);
}

.product-details {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.detail-badge {
  padding: 4px 12px;
  background: rgba(6, 182, 212, 0.1);
  border: 1px solid rgba(6, 182, 212, 0.3);
  border-radius: 6px;
  font-size: 0.85rem;
  color: var(--color-primary, #06b6d4);
  font-weight: 500;
}

.product-price {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: var(--color-bg, #071226);
  border-radius: 8px;
  margin-top: 8px;
}

.price-label {
  font-weight: 600;
  color: var(--color-text, #e6eef8);
}

.price-value {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-primary, #06b6d4);
}

/* Descripción */
.description-section {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 4px;
  color: var(--color-text, #e6eef8);
}

.form-hint {
  font-size: 0.85rem;
  color: var(--color-text-secondary, #9aa6b2);
  margin-bottom: 10px;
}

.description-input {
  width: 100%;
  padding: 12px;
  border: 2px solid var(--color-border, rgba(255,255,255,0.06));
  border-radius: 8px;
  background: var(--color-bg, #071226);
  color: var(--color-text, #e6eef8);
  font-size: 0.95rem;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.2s;
}

.description-input:focus {
  outline: none;
  border-color: var(--color-primary, #06b6d4);
}

.description-input::placeholder {
  color: var(--color-text-secondary, #9aa6b2);
}

/* Cupones */
.cupones-section {
  margin-bottom: 16px;
}

/* Precio final */
.price-final {
  background: var(--color-bg, #071226);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 20px;
}

.price-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  color: var(--color-text, #e6eef8);
  font-size: 0.95rem;
}

.price-row.descuento {
  color: #27ae60;
}

.price-row.total {
  font-weight: 700;
  font-size: 1.2rem;
  color: var(--color-primary, #06b6d4);
  border-top: 2px solid var(--color-border, rgba(255,255,255,0.06));
  margin-top: 8px;
  padding-top: 12px;
}

/* Acciones */
.actions-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.btn-action {
  width: 100%;
  padding: 14px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.btn-whatsapp {
  background: #25d366;
  color: white;
}

.btn-whatsapp:hover {
  background: #1da851;
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(37, 211, 102, 0.3);
}

.btn-whatsapp-mp {
  background: linear-gradient(135deg, #25d366 0%, #009ee3 100%);
  color: white;
}

.btn-whatsapp-mp:hover {
  background: linear-gradient(135deg, #1da851 0%, #007bb6 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 158, 227, 0.3);
}

.btn-icon {
  font-size: 1.2rem;
}

.actions-hint {
  font-size: 0.8rem;
  color: var(--color-text-secondary, #9aa6b2);
  text-align: center;
  margin-top: 12px;
}

@media (max-width: 768px) {
  .summary-layout {
    grid-template-columns: 1fr;
  }
}
</style>
