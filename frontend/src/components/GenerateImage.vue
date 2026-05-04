<template>
  <div class="generator panel-box">
    <div class="generator-header">
      <button @click="goBack" class="btn btn-back">← Volver</button>
      <h2>Generar mi imagen</h2>
    </div>

    <!-- Asistente de prompt con IA -->
    <div class="asistente-box">
      <label class="asistente-label">✨ Describí lo que querés (en español)</label>
      <div class="asistente-row">
        <input
          v-model="descripcionUsuario"
          placeholder="Ej: una calavera con flores de colores estilo mexicano"
          class="asistente-input"
          :disabled="loadingPrompt"
          @keydown.enter.prevent="asistirPrompt"
        />
        <button
          @click="asistirPrompt"
          :disabled="loadingPrompt || !descripcionUsuario.trim()"
          class="btn btn-back"
        >
          {{ loadingPrompt ? '⏳' : '🪄 Mejorar' }}
        </button>
      </div>
      <p v-if="errorPrompt" class="error-asistente">⚠️ {{ errorPrompt }}</p>
    </div>

    <label class="asistente-label">📝 Prompt final (podés editarlo)</label>
    <textarea
      v-model="prompt"
      placeholder="El prompt aparecerá aquí después de usar el asistente, o escribí uno directamente..."
    ></textarea>

    <button @click="generate" :disabled="loading || !prompt.trim()" class="btn btn-back">
      {{ loading ? 'Generando...' : 'Generar imagen' }}
    </button>
    
    <div v-if="error" class="error-message">
      ⚠️ {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useApi } from '../composables/useApi'

const emit = defineEmits(['image-generated', 'go-back'])

const prompt = ref('')
const image = ref(null)
const loading = ref(false)
const error = ref('')
const { generateImage } = useApi()

const userId = parseInt(localStorage.getItem('userId') || '0')

// --- Asistente de prompts ---
const descripcionUsuario = ref('')
const loadingPrompt = ref(false)
const errorPrompt = ref('')
const AGENTE_PROMPTS_URL = 'http://localhost:5004'

async function asistirPrompt() {
  if (!descripcionUsuario.value.trim()) return

  loadingPrompt.value = true
  errorPrompt.value = ''

  try {
    const response = await fetch(`${AGENTE_PROMPTS_URL}/generar-prompt`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ descripcion: descripcionUsuario.value.trim() })
    })
    const data = await response.json()

    if (data.success) {
      prompt.value = data.prompt
    } else {
      errorPrompt.value = data.error || 'No se pudo generar el prompt'
    }
  } catch (err) {
    errorPrompt.value = 'El agente de prompts no está disponible. Podés escribir el prompt directo.'
  } finally {
    loadingPrompt.value = false
  }
}

async function generate() {
  if (!prompt.value) return

  loading.value = true
  error.value = ''

  try {
    const result = await generateImage(prompt.value)
    
    let url = null

    if (result?.imagen_url) {
      url = result.imagen_url
    } else if (result?.imagen) {
      url = result.imagen
    } else {
      error.value = result?.error || 'Error al generar imagen'
      return
    }

    image.value = url

    // ✅ 🔥 ESTO ES LO QUE FALTABA
    emit('image-generated', {
      imagen_url: url,
      prompt: prompt.value
    })

  } catch (err) {
    console.error(err)
    error.value = err.message || 'Error generando imagen'
  } finally {
    loading.value = false
  }
}

function usarImagen() {
  emit('image-generated', {
    imagen_url: image.value,
    prompt: prompt.value
  })
}

function goBack() {
  emit('go-back')
}

function removeBackground() {
  // Emitir la imagen y el usuario podrá editarla en BackgroundRemover
  emit('image-generated', {
    imagen_url: image.value,
    prompt: prompt.value
  })
}
</script>

<style scoped>
:root {
  --color-primary: #06b6d4;
  --color-primary-dark: #0b7285;
  --color-surface: #0f1724;
  --color-accent: #ffd54f;
  --color-secondary: #ffd54f;
  --color-text: #e6eef8;
}

.generator {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

textarea {
  min-height: 100px;
  padding: 10px;
  border-radius: 8px;
  background-color: var(--color-surface);
  color: var(--color-text);
  border: 2px solid rgba(255, 255, 255, 0.06);
}

.error-message {
  padding: 10px;
  background-color: #fee;
  border: 2px solid #fcc;
  border-radius: 8px;
  color: #c33;
  font-size: 13px;
  margin: 10px 0;
}

button {
  padding: 10px 16px;
  cursor: pointer;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.2s ease;
  width: fit-content;
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
  border: 2px solid var(--color-primary);
}

.btn-primary:hover {
  background-color: var(--color-primary-dark);
  border-color: var(--color-primary-dark);
}

.btn-variant {
  background-color: var(--color-surface);
  color: white;
  border: 2px solid white;
}

.btn-variant:hover {
  background-color: rgba(255, 255, 255, 0.08);
  border-color: white;
}

.preview img {
  max-width: 250px;
  border-radius: 10px;
}

.actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
  flex-wrap: wrap;
}
.asistente-box {
  background: rgba(6, 182, 212, 0.06);
  border: 1px solid rgba(6, 182, 212, 0.2);
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.asistente-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-primary);
  letter-spacing: 0.3px;
}

.asistente-row {
  display: flex;
  gap: 8px;
}

.asistente-input {
  flex: 1;
  padding: 8px 12px;
  border-radius: 8px;
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 13px;
}

.asistente-input:disabled {
  opacity: 0.5;
}

.btn-asistir {
  padding: 8px 14px;
  background: rgba(6, 182, 212, 0.15);
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
  border-radius: 8px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.btn-asistir:hover:not(:disabled) {
  background: var(--color-primary);
  color: white;
}

.btn-asistir:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.error-asistente {
  font-size: 12px;
  color: #f87171;
  margin: 0;
}

</style>