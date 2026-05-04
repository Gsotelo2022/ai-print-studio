<!--
  ============================================
  PromptGenerator.vue - Paso 1: Crear diseño
  ============================================
  Este componente maneja:
    1. Input del prompt (texto que describe la imagen)
    2. Opciones de estilo (realista, ilustración, anime)
    3. Opciones de tamaño
    4. Botón "Generar Imagen"
    5. Llamada al backend → Stability AI

  COMUNICACIÓN:
    - Recibe: nada (es el primer paso)
    - Emite: @image-generated → le dice a App.vue que la imagen está lista

  FLUJO INTERNO:
    Usuario escribe prompt → click "Generar"
    → useApi().generateImage() → fetch POST /api/generate-image.php
    → PHP llama a Stability AI → devuelve imagen_url
    → Emitimos evento con la URL → App.vue avanza al paso 2
-->
<template>
  <div class="prompt-generator">
    <h2 class="section-title">
      <span class="step-badge">1</span>
      Crea tu diseño
    </h2>

    <!-- Input del prompt -->
    <div class="form-group">
      <div class="input-tabs">
        <button class="tab active">Generar con Texto</button>
        <button class="tab" disabled title="Próximamente">Subir Imagen</button>
      </div>
      <textarea
        v-model="prompt"
        placeholder="Dragón robótico en una ciudad futurista..."
        rows="3"
        class="prompt-input"
        maxlength="500"
      ></textarea>
      <small class="char-count">{{ prompt.length }}/500</small>
    </div>

    <!-- Botón generar -->
    <button
      @click="generate"
      :disabled="!canGenerate || loading"
      class="btn btn-back btn-generate"
    >
      {{ loading ? '⏳ Generando...' : '🎨 Generar Imagen' }}
    </button>

    <!-- Opciones de estilo -->
    <div class="form-group">
      <label class="form-label">Estilo:</label>
      <div class="radio-group">
        <label v-for="s in styles" :key="s.value" class="radio-option">
          <input type="radio" v-model="style" :value="s.value" />
          <span class="radio-label">{{ s.icon }} {{ s.label }}</span>
        </label>
      </div>
    </div>

    <!-- Opciones avanzadas -->
    <details class="advanced-options">
      <summary>Opciones avanzadas</summary>
      <div class="form-group">
        <label class="form-label">Tamaño:</label>
        <div class="size-options">
          <button
            v-for="size in sizes"
            :key="size.w"
            @click="width = size.w; height = size.h"
            class="btn btn-back"
            :class="{ 'btn-active': width === size.w && height === size.h }"
          >
            {{ size.w }} × {{ size.h }}
          </button>
        </div>
      </div>
    </details>

    <!-- Mensaje de error -->
    <div v-if="error" class="alert alert-error">
      ❌ {{ error }}
    </div>

    <!-- Preview de la imagen generada -->
    <div v-if="previewUrl" class="image-preview">
      <h3>Imagen generada:</h3>
      <img :src="previewUrl" alt="Imagen generada por IA" class="generated-image" />
      <div class="preview-actions">
        <button @click="generate" class="btn btn-back" :disabled="loading">
          🔄 Regenerar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useApi } from '../composables/useApi.js'

// --- Eventos que este componente puede emitir ---
// defineEmits le dice a Vue qué eventos dispara este componente
const emit = defineEmits(['image-generated'])

// --- API composable ---
const { loading, error, generateImage } = useApi()

// --- Estado local del componente ---
const prompt = ref('')
const style = ref('realista')
const width = ref(1024)
const height = ref(1024)
const previewUrl = ref(null)

// Opciones de estilo
const styles = [
  { value: 'realista',    label: 'Realista',     icon: '📷' },
  { value: 'ilustracion', label: 'Ilustración',  icon: '🎨' },
  { value: 'anime',       label: 'Anime',        icon: '✨' },
]

// Opciones de tamaño
const sizes = [
  { w: 512,  h: 512,  label: 'Chico' },
  { w: 1024, h: 1024, label: 'Mediano' },
  { w: 2048, h: 2048, label: 'Grande' },
]

// --- Computed ---
// computed() es un valor que se recalcula automáticamente
// cuando cambian sus dependencias
const canGenerate = computed(() => {
  return prompt.value.trim().length >= 3
})

// --- Función principal ---
async function generate() {
  try {
    // Llama al backend → Stability AI → devuelve imagen_url
    const data = await generateImage(prompt.value, {
      style: style.value,
      width: width.value,
      height: height.value,
    })

    // Guardar preview local
    previewUrl.value = data.imagen_url

    // Emitir evento hacia App.vue con los datos
    // App.vue escucha este evento con @image-generated="onImageGenerated"
    emit('image-generated', {
      imagen_url: data.imagen_url,
      prompt: prompt.value,
    })

  } catch (err) {
    // El error ya se maneja en useApi (se muestra arriba)
    console.error('Error generando imagen:', err)
  }
}
</script>
