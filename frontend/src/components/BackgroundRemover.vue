<template>
  <div class="background-remover-section">
    <!-- Header con título y botón volver -->
    <div class="section-header">
      <h2 class="section-title">
        <span class="step-badge">2</span>
        Editar imagen
      </h2>
      <button @click="goBack" class="btn btn-back">
        ← Volver
      </button>
    </div>

    <div class="remover-layout">
      <!-- Vista previa de la imagen -->
      <div class="image-preview">
        <div class="preview-container">
          <img 
            :src="imagenDisplayUrl" 
            :alt="'Imagen a editar'" 
            class="preview-image"
            :style="{
              transform: `rotate(${imageRotation}deg) scaleX(${imageFlipped ? -1 : 1})`,
              filter: imageFilter
            }"
          />
        </div>
        <p class="preview-label">Tu imagen</p>
      </div>

      <!-- Opciones -->
      <div class="remover-options">
        <div class="option-group">
          <h3>Opciones de edición</h3>

          <div class="option-item">
            <button @click="removeBackground" class="btn btn-back" :disabled="loading">
              <span v-if="!loading">✨ REMOVER FONDO</span>
              <span v-else>⏳ PROCESANDO (puede tomar 1-3 minutos)...</span>
            </button>
            <p class="option-description" v-if="!loading">Elimina el fondo de la imagen usando IA</p>
            <p class="option-description" v-else style="color: #ffd54f;">
              ⏳ Procesando con IA... La primera vez puede tardar más mientras descarga el modelo.
              <br>Por favor espera sin cerrar esta ventana.
            </p>
          </div>

          <div class="option-item">
            <button @click="rotateImage" class="btn btn-back">
              🔄 ROTAR IMAGEN
            </button>
            <p class="option-description">Gira la imagen 90 grados</p>
          </div>

          <div class="option-item">
            <button @click="flipImage" class="btn btn-back">
              ↔️ VOLTEAR IMAGEN
            </button>
            <p class="option-description">Espeja la imagen horizontalmente</p>
          </div>
        </div>

        <!-- Acciones finales -->
        <div class="action-buttons">
          <button @click="continueWithoutChanges" class="btn btn-back">
            Continuar sin cambios
          </button>
          <button @click="confirmChanges" class="btn btn-back" :disabled="!hasChanges">
            ✅ Continuar con cambios
          </button>
        </div>
      </div>
    </div>

    <!-- Estado del procesamiento -->
    <div v-if="status" class="status-message" :class="statusType">
      {{ status }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
//import { useApi } from '@/composables/useApi'
import { useApi } from '../composables/useApi.js'

const { removeBackground: removeBgApi } = useApi()

const emit = defineEmits(['image-processed', 'skip-editing', 'go-back'])

const props = defineProps({
  imagenUrl: {
    type: String,
    required: true
  }
})

const loading = ref(false)
const hasChanges = ref(false)
const status = ref('')
const statusType = ref('info')

const imageRotation = ref(0)
const imageFlipped = ref(false)
const backgroundRemoved = ref(false)
const imageFilter = ref('')

const imagenUrlActual = ref(props.imagenUrl)

// Abort controller (se mantiene por UX)
let controller = null

const imagenDisplayUrl = computed(() => imagenUrlActual.value)

watch(() => props.imagenUrl, (newUrl) => {
  imagenUrlActual.value = newUrl
  resetState()
})

function resetState() {
  imageRotation.value = 0
  imageFlipped.value = false
  backgroundRemoved.value = false
  imageFilter.value = ''
  hasChanges.value = false
  status.value = ''
}

// =============================
// 🧠 REMOVE BACKGROUND (FIX)
// =============================
async function removeBackground() {
  if (loading.value) return

  loading.value = true
  hasChanges.value = false
  status.value = '⏳ Removiendo fondo con IA...'
  statusType.value = 'info'

  try {
    let blob

    if (imagenUrlActual.value.startsWith('data:')) {
      blob = await fetch(imagenUrlActual.value).then(res => res.blob())
    } else {
      const response = await fetch(imagenUrlActual.value)
      if (!response.ok) throw new Error('No se pudo obtener la imagen')
      blob = await response.blob()
    }

    // ✅ USANDO useApi
    const data = await removeBgApi(blob)

    // compatibilidad backend
    const newImage = data?.imagen_url || data?.data?.imagen_url

    if (!newImage) {
      throw new Error('No se recibió imagen procesada')
    }

    imagenUrlActual.value = newImage

    backgroundRemoved.value = true
    imageFilter.value = 'drop-shadow(0 0 10px rgba(6, 182, 212, 0.5))'
    hasChanges.value = true

    status.value = '✅ ¡Fondo removido exitosamente!'
    statusType.value = 'success'

    setTimeout(() => {
      status.value = ''
    }, 3000)

  } catch (err) {
    if (err.name === 'AbortError') return

    let msg = err.message

    if (msg.includes('fetch')) {
      msg = 'Error de conexión con el backend'
    }

    status.value = `❌ ${msg}`
    statusType.value = 'error'

    setTimeout(() => {
      status.value = ''
    }, 8000)

  } finally {
    loading.value = false
  }
}

// =============================
// 🔄 TRANSFORMACIONES
// =============================
function rotateImage() {
  imageRotation.value = (imageRotation.value + 90) % 360
  hasChanges.value = true

  status.value = `🔄 Imagen rotada ${imageRotation.value}°`
  statusType.value = 'success'

  setTimeout(() => status.value = '', 2000)
}

function flipImage() {
  imageFlipped.value = !imageFlipped.value
  hasChanges.value = true

  status.value = imageFlipped.value
    ? '↔️ Imagen volteada'
    : '↔️ Imagen restaurada'

  statusType.value = 'success'

  setTimeout(() => status.value = '', 2000)
}

// =============================
// 🚀 ACCIONES
// =============================
function continueWithoutChanges() {
  emit('skip-editing')
}

function confirmChanges() {
  emit('image-processed', {
    imagen_url: imagenUrlActual.value,
    rotation: imageRotation.value,
    flipped: imageFlipped.value,
    backgroundRemoved: backgroundRemoved.value
  })
}

function goBack() {
  if (controller) controller.abort()
  emit('go-back')
}

onUnmounted(() => {
  if (controller) controller.abort()
})
</script>

<style scoped>
:root {
  --color-primary: #06b6d4;
  --color-primary-dark: #0b7285;
  --color-secondary: #ffd54f;
  --color-accent: #67e8f9;
  --color-text: #e6eef8;
  --color-text-light: #9aa6b2;
  --color-border: rgba(255, 255, 255, 0.06);
  --color-surface: #0f1724;
  --color-bg: #071226;
  --font-display: 'Orbitron', cursive;
}

.background-remover-section {
  display: flex;
  flex-direction: column;
  gap: 40px;
  padding: 40px 0;
  animation: fadeIn 0.3s ease;
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
  font-size: 28px;
  font-weight: 700;
  color: var(--color-primary);
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: var(--font-display);
  letter-spacing: 1px;
  margin: 0 0 20px 0;
}

.step-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--color-primary);
  color: white;
  font-weight: 700;
  font-size: 18px;
}

.remover-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  align-items: start;
}

.image-preview {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.preview-container {
  width: 100%;
  aspect-ratio: 1 / 1;
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid var(--color-primary);
  background-color: var(--color-surface);
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: transparent;
  transition: transform 0.4s ease-in-out;
  will-change: transform;
}

.preview-label {
  text-align: center;
  font-size: 14px;
  color: var(--color-text-light);
  margin: 0;
}

.remover-options {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.option-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.option-group h3 {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-accent);
  margin: 0;
  font-family: var(--font-display);
  letter-spacing: 2px;
  text-transform: uppercase;
  text-shadow: 0 0 10px rgba(103, 232, 249, 0.3);
}

.option-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.btn-option {
  padding: 16px 20px;
  background-color: var(--color-primary);
  border: 2px solid var(--color-primary);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 700;
  font-family: var(--font-display);
  transition: all 0.3s ease;
  font-size: 15px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.btn-option:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
  border-color: var(--color-accent);
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(6, 182, 212, 0.4);
}

.btn-option:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.option-description {
  font-size: 13px;
  color: var(--color-accent);
  margin: 0;
  line-height: 1.4;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-direction: column;
  margin-top: 20px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: var(--font-display);
  letter-spacing: 1px;
  text-transform: uppercase;
  font-size: 14px;
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
  border: 2px solid var(--color-primary);
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
  border-color: var(--color-primary-dark);
  transform: translateY(-3px);
  box-shadow: 0 8px 16px rgba(6, 182, 212, 0.3);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: var(--color-surface);
  color: var(--color-text);
  border: 2px solid var(--color-border);
}

.btn-secondary:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  transform: translateY(-2px);
}

.status-message {
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  font-weight: 700;
  font-family: var(--font-display);
  margin-top: 20px;
  font-size: 16px;
  letter-spacing: 1px;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.status-message.info {
  background-color: rgba(6, 182, 212, 0.15);
  border: 2px solid var(--color-primary);
  color: var(--color-accent);
  box-shadow: 0 0 20px rgba(6, 182, 212, 0.2);
}

.status-message.success {
  background-color: rgba(34, 197, 94, 0.15);
  border: 2px solid #22c55e;
  color: #4ade80;
  box-shadow: 0 0 20px rgba(34, 197, 94, 0.2);
}

.status-message.error {
  background-color: rgba(239, 68, 68, 0.15);
  border: 2px solid #ef4444;
  color: #fca5a5;
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.2);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .remover-layout {
    grid-template-columns: 1fr;
    gap: 32px;
  }

  .section-title {
    font-size: 24px;
  }

  .action-buttons {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>
