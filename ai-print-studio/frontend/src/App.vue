<template>
  <div class="app">
    <!-- Header -->
    <header class="app-header">
      <h1 class="app-title">Prendete Rock</h1>
      <p class="app-subtitle">Diseña y compra estampados personalizados</p>
    </header>

    <main class="app-main">
      <!-- Indicador de pasos -->
      <div class="steps-indicator">
        <div
          v-for="(step, index) in steps"
          :key="index"
          class="step"
          :class="{ active: currentStep >= index, completed: currentStep > index }"
        >
          <span class="step-number">{{ index + 1 }}</span>
          <span class="step-label">{{ step }}</span>
        </div>
      </div>

      <div class="panels-container">
        
        <!-- PASO 1: SUBIR IMAGEN -->
        <section class="panel" :class="{ 'panel-active': currentStep === 0 }">
          <ImageUploader
            @image-generated="onImageGenerated"
          />
        </section>

        <!-- PASO 2 -->
        <section v-if="generatedImage" class="panel" :class="{ 'panel-active': currentStep === 1 }">
          <ProductSelector
            :productos="productos"
            @product-selected="onProductSelected"
          />
        </section>

        <!-- PASO 3 -->
        <section v-if="selectedProduct" class="panel" :class="{ 'panel-active': currentStep === 2 }">
          <PreviewPanel
            :imagen-url="generatedImage"
            :producto="selectedProduct"
            :prompt="lastPrompt"
            @confirm-order="onConfirmOrder"
          />
        </section>

        <!-- PASO 4 -->
        <section v-if="orderData" class="panel" :class="{ 'panel-active': currentStep === 3 }">
          <CheckoutPanel
            :order="orderData"
            :imagen-url="generatedImage"
            :producto="selectedProduct"
          />
        </section>

      </div>
    </main>

    <!-- Footer -->
    <footer class="app-footer">
      <span>✅ Pago Seguro</span>
      <span>✅ Alta Calidad</span>
      <span>✅ Envío Rápido</span>
    </footer>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

// 🔥 IMPORTANTE: cambiamos el componente
import ImageUploader from './components/ImageUploader.vue'

import ProductSelector from './components/ProductSelector.vue'
import PreviewPanel from './components/PreviewPanel.vue'
import CheckoutPanel from './components/CheckoutPanel.vue'

const currentStep = ref(0)

const steps = ['Subí tu imagen', 'Elige producto', 'Vista previa', 'Pagar']

const generatedImage = ref(null)
const lastPrompt = ref('')

const selectedProduct = ref(null)
const orderData = ref(null)

const productos = reactive({
  camiseta: { nombre: 'Camiseta', precio: 12000, tienesTalle: true },
  taza:     { nombre: 'Taza',     precio: 8000,  tienesTalle: false },
  sudadera: { nombre: 'Sudadera', precio: 18000, tienesTalle: true },
  /*cojin:    { nombre: 'Cojín',    precio: 10000, tienesTalle: false },
  mochila:  { nombre: 'Mochila',  precio: 15000, tienesTalle: false },
  gorra:    { nombre: 'Gorra',    precio: 9000,  tienesTalle: false },*/
})

// EVENTOS

function onImageGenerated({ imagen_url, prompt }) {
  generatedImage.value = imagen_url
  lastPrompt.value = prompt
  currentStep.value = 1
}

function onProductSelected(product) {
  selectedProduct.value = product
  currentStep.value = 2
}

function onConfirmOrder(order) {
  orderData.value = order
  currentStep.value = 3
}
</script>