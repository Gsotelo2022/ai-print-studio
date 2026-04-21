<template>
  <div class="background-remover-section">
    <h2 class="section-title">
      <span class="step-badge">2</span>
      Editar imagen
    </h2>

    <div class="remover-layout">
      <!-- Vista previa de la imagen -->
      <div class="image-preview">
        <div class="preview-container">
          <img 
            :src="imagenUrl.value" 
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
            <button @click="removeBackground" class="btn btn-option" :disabled="loading">
              <span v-if="!loading">✨ Remover fondo</span>
              <span v-else>⏳ Procesando...</span>
            </button>
            <p class="option-description">Elimina el fondo de la imagen para mejor resultado</p>
          </div>

          <div class="option-item">
            <button @click="rotatImage" class="btn btn-option">
              🔄 Rotar imagen
            </button>
            <p class="option-description">Gira la imagen 90 grados</p>
          </div>

          <div class="option-item">
            <button @click="flipImage" class="btn btn-option">
              ↔️ Voltear imagen
            </button>
            <p class="option-description">Espeja la imagen horizontalmente</p>
          </div>
        </div>

        <!-- Acciones finales -->
        <div class="action-buttons">
          <button @click="continueWithoutChanges" class="btn btn-secondary">
            Continuar sin cambios
          </button>
          <button @click="confirmChanges" class="btn btn-primary" :disabled="!hasChanges">
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
import { ref } from 'vue'

const emit = defineEmits(['image-processed', 'skip-editing'])

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
const imagenUrl = ref(props.imagenUrl)

function removeBackground() {
  loading.value = true
  status.value = '⏳ Removiendo fondo con IA (esto puede tomar un momento)...'
  statusType.value = 'info'

  console.log('[removeBackground] Iniciando, imagen URL:', imagenUrl.value)

  // Obtener la imagen del URL y convertir a blob/file
  fetch(imagenUrl.value)
    .then(response => {
      console.log('[removeBackground] Blob fetch status:', response.status)
      if (!response.ok) throw new Error(`No se pudo obtener la imagen: ${response.status}`)
      return response.blob()
    })
    .then(blob => {
      console.log('[removeBackground] Blob obtenido, tamaño:', blob.size, 'tipo:', blob.type)
      const formData = new FormData()
      formData.append('file', blob, 'imagen.png')
      
      console.log('[removeBackground] Enviando POST a /api/remove-background')
      return fetch('http://localhost:8000/api/remove-background', {
        method: 'POST',
        body: formData
      })
    })
    .then(response => {
      console.log('[removeBackground] Respuesta del servidor status:', response.status)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return response.json()
    })
    .then(data => {
      console.log('[removeBackground] Datos recibidos:', data)
      if (data.success) {
        loading.value = false
        status.value = '✅ ¡Fondo removido exitosamente!'
        statusType.value = 'success'
        backgroundRemoved.value = true
        imageFilter.value = 'drop-shadow(0 0 10px rgba(6, 182, 212, 0.5))'
        hasChanges.value = true
        // Actualizar la imagen con la procesada
        console.log('[removeBackground] Actualizando imagen...')
        imagenUrl.value = data.data.imagen_url
        console.log('[removeBackground] Imagen actualizada exitosamente')
      } else {
        throw new Error(data.detail?.error || 'Error desconocido del servidor')
      }
    })
    .catch(error => {
      console.error('[removeBackground] Error:', error)
      loading.value = false
      status.value = `❌ Error: ${error.message}`
      statusType.value = 'error'
    })
}

function rotatImage() {
  imageRotation.value = (imageRotation.value + 90) % 360
  hasChanges.value = true
  status.value = `� Imagen rotada ${imageRotation.value}° - ¡Perfecto!`
  statusType.value = 'success'
  
  // Limpiar el mensaje después de 3 segundos
  setTimeout(() => {
    status.value = ''
  }, 3000)
}

function flipImage() {
  imageFlipped.value = !imageFlipped.value
  hasChanges.value = true
  status.value = imageFlipped.value ? '↔️ Imagen volteada - ¡Listo!' : '↔️ Imagen restaurada'
  statusType.value = 'success'
  
  // Limpiar el mensaje después de 3 segundos
  setTimeout(() => {
    status.value = ''
  }, 3000)
}

function continueWithoutChanges() {
  emit('skip-editing')
}

function confirmChanges() {
  emit('image-processed', {
    imagen_url: imagenUrl.value,
    rotation: imageRotation.value,
    flipped: imageFlipped.value,
    backgroundRemoved: backgroundRemoved.value
  })
}
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
