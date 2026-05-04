<template>
  <div class="uploader">
    <div class="uploader-header">
      <button @click="goBack" class="btn btn-back">← Volver</button>
      <h2>1️⃣ Tu imagen</h2>
    </div>

    <!-- Input file -->
    <input 
      type="file" 
      ref="fileInput"
      accept="image/*" 
      @change="onFileChange"
      style="display: none;"
    />

    <button class="btn btn-back" @click="openFile">
      📁 Elegir imagen
    </button>
    
    <!-- Preview -->
    <div v-if="preview" class="preview-container">
      <img :src="preview" class="preview-image" />
    </div>

    <!-- Acciones -->
    <div v-if="preview" class="actions">
      <button @click="emitImage" class="btn btn-back">
        ✅ Usar imagen
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['image-generated', 'go-back'])

const file = ref(null)
const preview = ref(null)
const loading = ref(false)
const base64Image = ref(null) // Guardar la versión base64

// Cuando el usuario selecciona archivo
function onFileChange(e) {
  const selected = e.target.files[0]
  if (!selected) return

  file.value = selected
  preview.value = URL.createObjectURL(selected)
  
  // Convertir a base64 para enviar al backend
  const reader = new FileReader()
  reader.onload = (event) => {
    base64Image.value = event.target.result
    console.log('✅ Imagen convertida a base64')
  }
  reader.readAsDataURL(selected)
}

// Emitir imagen (irá al BackgroundRemover después en App.vue)
function emitImage() {
  emit('image-generated', {
    imagen_url: base64Image.value || preview.value, // Usar base64 si está disponible
    prompt: 'imagen subida por usuario'
  })
}

// Volver al dashboard
function goBack() {
  emit('go-back')
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

.uploader-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.uploader-header h2 {
  margin: 0;
  flex: 1;
  font-size: 24px;
  color: var(--color-primary);
}

.btn-back {
  padding: 10px 16px;
  background-color: transparent;
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: #e6eef8;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  font-size: 14px;
  white-space: nowrap;
}

.btn-back:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  transform: translateY(-2px);
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