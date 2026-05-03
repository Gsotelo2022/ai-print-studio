<!--
  ============================================
  MisDisenosGaleria.vue - Galería de diseños del usuario
  ============================================
  
  Muestra todos los diseños que el usuario ha creado o subido,
  permitiendo reutilizarlos en nuevos pedidos.
  
  Props:
    - userId (Number): ID del usuario autenticado
  
  Eventos:
    - @design-selected: Se emite cuando el usuario selecciona un diseño para usar
    - @go-back: Volver al paso anterior
-->

<template>
  <div class="disenos-galeria">
    <!-- Header -->
    <div class="section-header">
      <h2 class="section-title">
        <span class="step-badge">📸</span>
        Mis Diseños
      </h2>
      <button @click="$emit('go-back')" class="btn-volver">
        ← Volver
      </button>
    </div>

    <!-- Loading -->
    <div v-if="cargando" class="loading-container">
      <div class="loading-spinner"></div>
      <h3>Cargando tus diseños...</h3>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-container">
      <p>❌ Error al cargar diseños: {{ error }}</p>
      <button @click="cargarDisenos" class="btn-retry">Reintentar</button>
    </div>

    <!-- Contenido principal -->
    <div v-else class="galeria-content">
      <!-- Estadísticas -->
      <div class="stats-bar">
        <div class="stat-item">
          <span class="stat-icon">🎨</span>
          <span class="stat-label">Total:</span>
          <span class="stat-value">{{ estadisticas.total }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-icon">🤖</span>
          <span class="stat-label">Generados por IA:</span>
          <span class="stat-value">{{ estadisticas.total_generados_ia }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-icon">📤</span>
          <span class="stat-label">Subidos:</span>
          <span class="stat-value">{{ estadisticas.total_subidos }}</span>
        </div>
      </div>

      <!-- Filtros -->
      <div class="filters-bar">
        <button 
          :class="['filter-btn', { active: filtroActivo === 'todos' }]"
          @click="filtroActivo = 'todos'"
        >
          Todos
        </button>
        <button 
          :class="['filter-btn', { active: filtroActivo === 'ia' }]"
          @click="filtroActivo = 'ia'"
        >
          Generados por IA
        </button>
        <button 
          :class="['filter-btn', { active: filtroActivo === 'subidos' }]"
          @click="filtroActivo = 'subidos'"
        >
          Subidos manualmente
        </button>
      </div>

      <!-- Mensaje vacío -->
      <div v-if="disenosFiltrados.length === 0" class="empty-state">
        <span class="empty-icon">📸</span>
        <h3>No tienes diseños aún</h3>
        <p>Genera tu primera imagen con IA o sube tu propio diseño</p>
        <button @click="$emit('go-back')" class="btn-primary">
          Crear nuevo diseño
        </button>
      </div>

      <!-- Grid de diseños -->
      <div v-else class="disenos-grid">
        <div 
          v-for="diseno in disenosFiltrados" 
          :key="diseno.id_archivo"
          class="diseno-card"
          @click="abrirModal(diseno)"
        >
          <!-- Thumbnail -->
          <div class="diseno-thumbnail">
            <img 
              v-if="diseno.ruta_thumbnail"
              :src="`${BASE_URL}/${diseno.ruta_thumbnail}`" 
              :alt="diseno.nombre_original"
              @error="handleImageError"
            />
            <div v-else class="thumbnail-placeholder">
              <span>🖼️</span>
              <span>Sin preview</span>
            </div>
            
            <!-- Badge de IA -->
            <div v-if="diseno.es_generado_ia" class="ia-badge">
              🤖 IA
            </div>
            
            <!-- Overlay hover -->
            <div class="diseno-overlay">
              <button class="btn-use">
                ✓ Usar este diseño
              </button>
            </div>
          </div>

          <!-- Info -->
          <div class="diseno-info">
            <div class="diseno-nombre">{{ diseno.nombre_original }}</div>
            <div class="diseno-meta">
              <span>{{ diseno.dimensiones }}</span>
              <span>•</span>
              <span>{{ diseno.tamano_kb }} KB</span>
            </div>
            <div class="diseno-fecha">
              {{ formatearFecha(diseno.fecha_subida) }}
            </div>
            <div v-if="diseno.estadisticas.veces_usado > 0" class="diseno-stats">
              📦 Usado {{ diseno.estadisticas.veces_usado }} vez(veces)
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de detalle -->
    <transition name="fade">
      <div v-if="disenoSeleccionado" class="modal-overlay" @click="cerrarModal">
        <div class="modal-content" @click.stop>
          <!-- Header modal -->
          <div class="modal-header">
            <h3>{{ disenoSeleccionado.nombre_original }}</h3>
            <button class="btn-close" @click="cerrarModal">✕</button>
          </div>

          <!-- Body modal -->
          <div class="modal-body">
            <!-- Imagen grande -->
            <div class="modal-image-container">
              <img 
                v-if="disenoSeleccionado.ruta_archivo"
                :src="`${BASE_URL}/${disenoSeleccionado.ruta_archivo}`"
                :alt="disenoSeleccionado.nombre_original"
                @error="handleImageError"
              />
              <div v-else class="image-placeholder">
                🖼️ Imagen no disponible
              </div>
            </div>

            <!-- Detalles -->
            <div class="modal-details">
              <div class="detail-row">
                <span class="detail-label">Dimensiones:</span>
                <span class="detail-value">{{ disenoSeleccionado.dimensiones }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Tamaño:</span>
                <span class="detail-value">{{ disenoSeleccionado.tamano_kb }} KB</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Tipo:</span>
                <span class="detail-value">{{ disenoSeleccionado.tipo_mime }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Origen:</span>
                <span class="detail-value">
                  {{ disenoSeleccionado.es_generado_ia ? '🤖 Generado por IA' : '📤 Subido manualmente' }}
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Fecha:</span>
                <span class="detail-value">{{ formatearFechaCompleta(disenoSeleccionado.fecha_subida) }}</span>
              </div>
              
              <!-- Prompt si es IA -->
              <div v-if="disenoSeleccionado.es_generado_ia && disenoSeleccionado.prompt_usado" class="detail-row prompt-row">
                <span class="detail-label">Prompt usado:</span>
                <p class="prompt-text">{{ disenoSeleccionado.prompt_usado }}</p>
              </div>

              <!-- Estadísticas de uso -->
              <div class="usage-stats">
                <h4>Estadísticas de uso:</h4>
                <div class="stat-row">
                  <span>📦 Usado en pedidos:</span>
                  <strong>{{ disenoSeleccionado.estadisticas.veces_usado }}</strong>
                </div>
                <div v-if="disenoSeleccionado.estadisticas.ultimo_uso" class="stat-row">
                  <span>🕒 Último uso:</span>
                  <strong>{{ formatearFechaCompleta(disenoSeleccionado.estadisticas.ultimo_uso) }}</strong>
                </div>
              </div>
            </div>
          </div>

          <!-- Footer modal -->
          <div class="modal-footer">
            <button class="btn-secondary" @click="cerrarModal">
              Cancelar
            </button>
            <button class="btn-primary" @click="usarDiseno">
              ✓ Usar este diseño
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi.js'

const { get } = useApi()
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Props
const props = defineProps({
  userId: { type: Number, required: true }
})

// Eventos
const emit = defineEmits(['design-selected', 'go-back'])

// Estado
const cargando = ref(false)
const error = ref(null)
const disenos = ref([])
const estadisticas = ref({
  total: 0,
  total_generados_ia: 0,
  total_subidos: 0
})
const filtroActivo = ref('todos')
const disenoSeleccionado = ref(null)

// Computed
const disenosFiltrados = computed(() => {
  if (filtroActivo.value === 'todos') {
    return disenos.value
  } else if (filtroActivo.value === 'ia') {
    return disenos.value.filter(d => d.es_generado_ia)
  } else {
    return disenos.value.filter(d => !d.es_generado_ia)
  }
})

// Funciones
async function cargarDisenos() {
  // Validar que userId sea válido
  if (!props.userId || isNaN(props.userId)) {
    console.error('❌ userId inválido:', props.userId)
    error.value = 'No se pudo identificar al usuario. Por favor, inicia sesión nuevamente.'
    return
  }
  
  cargando.value = true
  error.value = null
  
  try {
    console.log(`🔄 Cargando diseños del usuario ${props.userId}...`)
    
    const result = await get(`/mis-disenos/${props.userId}`)
    
    disenos.value = result.disenos || []
    estadisticas.value = {
      total: result.total || 0,
      total_generados_ia: result.total_generados_ia || 0,
      total_subidos: result.total_subidos || 0
    }
    
    console.log(`✅ ${disenos.value.length} diseños cargados`)
  } catch (err) {
    console.error('❌ Error cargando diseños:', err)
    error.value = err.message
  } finally {
    cargando.value = false
  }
}

function abrirModal(diseno) {
  disenoSeleccionado.value = diseno
}

function cerrarModal() {
  disenoSeleccionado.value = null
}

function usarDiseno() {
  if (!disenoSeleccionado.value) return
  
  console.log('✅ Diseño seleccionado:', disenoSeleccionado.value)
  
  // Emitir evento con la URL del diseño
  emit('design-selected', {
    imagen_url: `${BASE_URL}/${disenoSeleccionado.value.ruta_archivo}`,
    prompt: disenoSeleccionado.value.prompt_usado || 'Diseño reutilizado',
    id_archivo: disenoSeleccionado.value.id_archivo
  })
  
  cerrarModal()
}

function handleImageError(event) {
  event.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23f0f0f0" width="200" height="200"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23999"%3E🖼️%3C/text%3E%3C/svg%3E'
}

function formatearFecha(fecha) {
  if (!fecha) return 'N/A'
  const date = new Date(fecha)
  const ahora = new Date()
  const diff = ahora - date
  const dias = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (dias === 0) return 'Hoy'
  if (dias === 1) return 'Ayer'
  if (dias < 7) return `Hace ${dias} días`
  if (dias < 30) return `Hace ${Math.floor(dias / 7)} semanas`
  return date.toLocaleDateString('es-ES', { year: 'numeric', month: 'short', day: 'numeric' })
}

function formatearFechaCompleta(fecha) {
  if (!fecha) return 'N/A'
  const date = new Date(fecha)
  return date.toLocaleDateString('es-ES', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Lifecycle
onMounted(() => {
  cargarDisenos()
})
</script>

<style scoped>
.disenos-galeria {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

/* Header */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 28px;
  margin: 0;
  color: #333;
}

.step-badge {
  font-size: 32px;
}

.btn-volver {
  padding: 10px 20px;
  background: #f5f5f5;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-volver:hover {
  background: #e0e0e0;
}

/* Loading y Error */
.loading-container,
.error-container {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.btn-retry {
  padding: 10px 20px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  margin-top: 20px;
}

/* Estadísticas */
.stats-bar {
  display: flex;
  gap: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-icon {
  font-size: 24px;
}

.stat-label {
  opacity: 0.9;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
}

/* Filtros */
.filters-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
}

.filter-btn {
  padding: 10px 20px;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: #667eea;
}

.filter-btn.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

/* Estado vacío */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 80px;
  display: block;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin: 0 0 10px;
  color: #333;
}

.empty-state p {
  color: #666;
  margin-bottom: 30px;
}

.btn-primary {
  padding: 12px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: #5568d3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* Grid de diseños */
.disenos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.diseno-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.diseno-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.diseno-thumbnail {
  position: relative;
  width: 100%;
  height: 250px;
  background: #f5f5f5;
  overflow: hidden;
}

.diseno-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbnail-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  font-size: 48px;
}

.thumbnail-placeholder span:last-child {
  font-size: 14px;
  margin-top: 10px;
}

.ia-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(102, 126, 234, 0.9);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.diseno-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.diseno-card:hover .diseno-overlay {
  opacity: 1;
}

.btn-use {
  padding: 12px 24px;
  background: white;
  color: #667eea;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-use:hover {
  transform: scale(1.05);
}

.diseno-info {
  padding: 15px;
}

.diseno-nombre {
  font-weight: 600;
  color: #333;
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.diseno-meta,
.diseno-fecha,
.diseno-stats {
  font-size: 12px;
  color: #666;
  margin-bottom: 3px;
}

.diseno-stats {
  color: #667eea;
  font-weight: 500;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 16px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
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

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

.modal-image-container {
  background: #f5f5f5;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.modal-image-container img {
  max-width: 100%;
  max-height: 600px;
  object-fit: contain;
}

.image-placeholder {
  font-size: 48px;
  color: #999;
}

.modal-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 12px;
  color: #666;
  text-transform: uppercase;
  font-weight: 600;
}

.detail-value {
  font-size: 14px;
  color: #333;
}

.prompt-row {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 8px;
}

.prompt-text {
  margin: 0;
  line-height: 1.6;
  color: #333;
}

.usage-stats {
  margin-top: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 8px;
}

.usage-stats h4 {
  margin: 0 0 12px;
  font-size: 14px;
  color: #333;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
  color: #666;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #eee;
}

.btn-secondary {
  padding: 10px 20px;
  background: #f5f5f5;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

/* Transiciones */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 900px) {
  .modal-body {
    grid-template-columns: 1fr;
  }
  
  .stats-bar {
    flex-direction: column;
    gap: 5px;
  }
}

@media (max-width: 640px) {
  .disenos-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
  
  .diseno-thumbnail {
    height: 150px;
  }
}
</style>
