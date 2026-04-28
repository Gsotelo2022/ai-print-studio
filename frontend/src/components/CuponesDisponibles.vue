<!--
  ============================================
  CuponesDisponibles.vue - Sistema de cupones
  ============================================
  Componente reutilizable que muestra cupones disponibles
  para el usuario actual y permite aplicarlos al pedido.
  
  Props:
    - userId (Number): ID del usuario autenticado
  
  Eventos:
    - @cupon-aplicado: Se emite cuando el usuario aplica un cupón
    - @cupon-removido: Se emite cuando el usuario quita el cupón aplicado
-->

<template>
  <div class="cupones-container">
    <!-- Badge de cupones disponibles -->
    <div v-if="!cargando && cuponesDisponibles.length > 0" class="cupones-badge" @click="toggleModal">
      <span class="badge-icon">🎟️</span>
      <span class="badge-text">
        Tienes {{ cuponesDisponibles.length }} cupón(es) disponible(s)
      </span>
      <span class="badge-arrow">{{ modalVisible ? '▲' : '▼' }}</span>
    </div>

    <!-- Mensaje cuando no hay cupones -->
    <div v-else-if="!cargando && cuponesDisponibles.length === 0" class="no-cupones">
      <span class="no-cupones-icon">😔</span>
      <span class="no-cupones-text">No tienes cupones disponibles en este momento</span>
    </div>

    <!-- Loading -->
    <div v-if="cargando" class="cupones-loading">
      <div class="spinner"></div>
      <span>Cargando cupones...</span>
    </div>

    <!-- Modal de cupones -->
    <transition name="fade">
      <div v-if="modalVisible" class="cupones-modal-overlay" @click="closeModal">
        <div class="cupones-modal" @click.stop>
          <div class="modal-header">
            <h3>🎟️ Tus cupones disponibles</h3>
            <button class="btn-close" @click="closeModal">✕</button>
          </div>

          <div class="modal-body">
            <!-- Lista de cupones -->
            <div v-for="cupon in cuponesDisponibles" :key="cupon.id_cupon" class="cupon-card">
              <div class="cupon-header">
                <div class="cupon-codigo">{{ cupon.codigo }}</div>
                <div class="cupon-descuento">-{{ cupon.descuento }}%</div>
              </div>
              
              <div class="cupon-descripcion">{{ cupon.descripcion }}</div>
              
              <div class="cupon-info">
                <div class="info-item">
                  <span class="info-label">Expira:</span>
                  <span class="info-value">{{ formatearFecha(cupon.expiracion) }}</span>
                </div>
                <div v-if="cupon.es_limitado" class="info-item">
                  <span class="info-label">Usos restantes:</span>
                  <span class="info-value">{{ cupon.usos_restantes }}</span>
                </div>
              </div>

              <div v-if="cupon.razon" class="cupon-razon">
                {{ cupon.razon }}
              </div>

              <button 
                class="btn-aplicar"
                :disabled="cuponAplicadoId === cupon.id_cupon"
                @click="aplicarCupon(cupon)"
              >
                {{ cuponAplicadoId === cupon.id_cupon ? '✓ Aplicado' : 'Aplicar cupón' }}
              </button>
            </div>
          </div>

          <div class="modal-footer">
            <button 
              v-if="cuponAplicadoId" 
              class="btn-remover"
              @click="removerCupon"
            >
              🗑️ Quitar cupón
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// Props
const props = defineProps({
  userId: { type: Number, required: true }
})

// Eventos
const emit = defineEmits(['cupon-aplicado', 'cupon-removido'])

// Estado
const cuponesDisponibles = ref([])
const cargando = ref(false)
const modalVisible = ref(false)
const cuponAplicadoId = ref(null)
const error = ref(null)

// Funciones
function toggleModal() {
  modalVisible.value = !modalVisible.value
}

function closeModal() {
  modalVisible.value = false
}

function aplicarCupon(cupon) {
  cuponAplicadoId.value = cupon.id_cupon
  emit('cupon-aplicado', cupon)
  console.log(`✅ Cupón ${cupon.codigo} aplicado (-${cupon.descuento}%)`)
  closeModal()
}

function removerCupon() {
  cuponAplicadoId.value = null
  emit('cupon-removido')
  console.log('🗑️ Cupón removido')
  closeModal()
}

function formatearFecha(fecha) {
  if (!fecha) return 'N/A'
  const date = new Date(fecha)
  return date.toLocaleDateString('es-ES', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}

async function cargarCupones() {
  cargando.value = true
  error.value = null
  
  try {
    console.log(`🔄 Cargando cupones para usuario ${props.userId}...`)
    
    const response = await fetch(`http://localhost:8000/api/cupones/disponibles/${props.userId}`)
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    
    const result = await response.json()
    
    if (result.success && result.data) {
      cuponesDisponibles.value = result.data.cupones || []
      console.log(`✅ ${cuponesDisponibles.value.length} cupones cargados`)
    } else {
      console.warn('⚠️ Respuesta sin cupones:', result)
      cuponesDisponibles.value = []
    }
  } catch (err) {
    console.error('❌ Error cargando cupones:', err)
    error.value = err.message
    cuponesDisponibles.value = []
  } finally {
    cargando.value = false
  }
}

// Cargar cupones al montar componente
onMounted(() => {
  cargarCupones()
})

// Exponer método para recargar cupones (opcional)
defineExpose({
  recargarCupones: cargarCupones
})
</script>

<style scoped>
.cupones-container {
  margin: 20px 0;
}

/* Badge de cupones */
.cupones-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.cupones-badge:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.badge-icon {
  font-size: 24px;
}

.badge-text {
  flex: 1;
  font-weight: 600;
  font-size: 14px;
}

.badge-arrow {
  font-size: 12px;
  opacity: 0.8;
}

/* Mensaje sin cupones */
.no-cupones {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: #f5f5f5;
  color: #666;
  border-radius: 12px;
  font-size: 14px;
}

.no-cupones-icon {
  font-size: 20px;
}

/* Loading */
.cupones-loading {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  color: #666;
  font-size: 14px;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #ddd;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Modal overlay */
.cupones-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

/* Modal */
.cupones-modal {
  background: white;
  border-radius: 16px;
  max-width: 500px;
  width: 100%;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

/* Modal header */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.btn-close:hover {
  background: #f5f5f5;
  color: #333;
}

/* Modal body */
.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* Cupon card */
.cupon-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.cupon-card:last-child {
  margin-bottom: 0;
}

.cupon-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.cupon-codigo {
  font-size: 18px;
  font-weight: bold;
  letter-spacing: 1px;
  font-family: 'Courier New', monospace;
}

.cupon-descuento {
  font-size: 24px;
  font-weight: bold;
}

.cupon-descripcion {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 12px;
}

.cupon-info {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  font-size: 12px;
  opacity: 0.8;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-label {
  opacity: 0.7;
}

.info-value {
  font-weight: 600;
}

.cupon-razon {
  background: rgba(255, 255, 255, 0.2);
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 12px;
}

.btn-aplicar {
  width: 100%;
  padding: 12px;
  background: white;
  color: #667eea;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-aplicar:hover:not(:disabled) {
  background: #f5f5f5;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.btn-aplicar:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Modal footer */
.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #eee;
}

.btn-remover {
  width: 100%;
  padding: 12px;
  background: #ff4444;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-remover:hover {
  background: #cc0000;
  transform: translateY(-1px);
}

/* Transiciones */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 640px) {
  .cupones-modal {
    max-height: 90vh;
  }
  
  .cupon-codigo {
    font-size: 16px;
  }
  
  .cupon-descuento {
    font-size: 20px;
  }
}
</style>
