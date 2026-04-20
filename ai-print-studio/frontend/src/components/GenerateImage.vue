<template>
  <div class="generator panel-box">
    <div class="generator-header">
      <button @click="goBack" class="btn btn-back">← Volver</button>
      <h2>Generar mi imagen</h2>
    </div>

    <textarea
      v-model="prompt"
    ></textarea>

    <button @click="generate" :disabled="loading" class="btn btn-primary">
      {{ loading ? 'Generando...' : 'Generar' }}
    </button>
    
    <div v-if="image" class="preview">
      <img :src="image" />
      
      <div class="actions">
        <button @click="usarImagen" class="btn btn-variant">
          Usar imagen
        </button>

        <button @click="removeBackground" class="btn btn-variant">
          ✂️ Quitar fondo
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['image-generated', 'go-back'])

const prompt = ref('')
const image = ref(null)
const loading = ref(false)

async function generate() {

  if (!prompt.value) return

  loading.value = true

  try {

    const res = await fetch('http://localhost:3000/generar-imagen', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        prompt: prompt.value
      })
    })

    const data = await res.json()

    image.value = data.imagen

  } catch (error) {
    console.error(error)
    alert('Error generando imagen')
  }

  loading.value = false
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

</style>