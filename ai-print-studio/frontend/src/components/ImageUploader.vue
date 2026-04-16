<template>
  <div class="uploader">
    <h2>1️⃣ Tu imagen</h2>

    <!-- Input file -->
    <input 
      type="file" 
      ref="fileInput"
      accept="image/*" 
      @change="onFileChange"
      style="display: none;"
    />

    <button class="btn btn-primary" @click="openFile">
      📁 Elegir imagen
    </button>
    
    <!-- Preview -->
    <div v-if="preview" class="preview-container">
      <img :src="preview" class="preview-image" />
    </div>

    <!-- Acciones -->
    <div v-if="preview" class="actions ">
      <button @click="emitImage" class="btn btn-variant">
        Usar imagen
      </button>

      <button @click="removeBackground" :disabled="loading" class="btn btn-variant">
        {{ loading ? 'Procesando...' : 'Quitar fondo con IA' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['image-generated'])

const file = ref(null)
const preview = ref(null)
const loading = ref(false)

// Cuando el usuario selecciona archivo
function onFileChange(e) {
  const selected = e.target.files[0]
  if (!selected) return

  file.value = selected
  preview.value = URL.createObjectURL(selected)
}

// Emitir imagen SIN IA
function emitImage() {
  emit('image-generated', {
    imagen_url: preview.value,
    prompt: 'imagen subida por usuario'
  })
}

// Llamar al backend para quitar fondo
async function removeBackground() {
  if (!file.value) return

  loading.value = true

  const formData = new FormData()
  formData.append('image', file.value)

  try {
    const res = await fetch('http://ai-print-studio.local/backend/api/remove-background.php', {
      method: 'POST',
      body: formData
    })

    const data = await res.json()

    if (data.error) {
      console.error('Error del servidor:', data)
      alert(`Error: ${data.error}\n${data.detalle || ''}`)
      return
    }

    preview.value = data.imagen_url

    emit('image-generated', {
      imagen_url: data.imagen_url,
      prompt: 'imagen con fondo removido'
    })

  } catch (error) {
    console.error('Error:', error)
    alert('Error al conectar con el servidor')
  } finally {
    loading.value = false
  }
}

const fileInput = ref(null)

function openFile() {
  fileInput.value.click()
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

.uploader {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
  border: 2px solid var(--color-primary);
  padding: 12px 24px;
  cursor: pointer;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.2s ease;
  width: fit-content;
}

.btn-primary:hover {
  background-color: var(--color-primary-dark);
  border-color: var(--color-primary-dark);
}

.btn-variant {
  background-color: var(--color-surface);
  color: white;
  border: 2px solid white;
  padding: 10px 16px;
  cursor: pointer;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.2s ease;
  width: fit-content;
}

.btn-variant:hover {
  background-color: rgba(255, 255, 255, 0.08);
  border-color: white;
}

.preview-container {
  margin-top: 10px;
}

.preview-image {
  max-width: 250px;
  border-radius: 10px;
}

.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
</style>