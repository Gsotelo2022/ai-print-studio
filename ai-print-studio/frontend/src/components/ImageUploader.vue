<template>
  <div class="uploader">
    <h2>1️⃣ Subí tu imagen</h2>

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
    const res = await fetch('http://localhost/ai-print-studio/backend/api/remove-background.php', {
      method: 'POST',
      body: formData
    })

    const data = await res.json()

    preview.value = data.imagen_url

    emit('image-generated', {
      imagen_url: data.imagen_url,
      prompt: 'imagen con fondo removido'
    })

  } catch (error) {
    console.error('Error:', error)
    alert('Error al procesar la imagen')
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
.uploader {
  display: flex;
  flex-direction: column;
  gap: 15px;
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
}
</style>