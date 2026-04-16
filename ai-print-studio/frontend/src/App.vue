<template>
  <div class="app">
    <!-- Header Navbar -->
    <header class="navbar">
      <div class="navbar-container">
        <div class="logo-section">
          <div class="logo"><img src="./assets/logo-prendete-rock.jpg" alt="Logo"></div>
          <span class="brand">Prendete Rock</span>
        </div>
        <nav class="nav-menu">
          <a href="#" class="nav-link active">Inicio</a>
          <a href="#" class="nav-link">Crear</a>
          <a href="#" class="nav-link">Mis diseños</a>
        </nav>
        <!-- <div class="nav-actions">
          <button class="icon-btn">🌙</button>
          <button class="icon-btn">👤</button>
        </div> -->
      </div>
    </header>

    <main class="app-main">
      <!-- PASO 0: HERO SECTION -->
      <section v-if="!imageSourceMode" class="hero-section">
        <div class="">
          <div class="hero-content">
            <h1 class="hero-title">Creá estampados únicos con IA</h1>
            <p class="hero-subtitle">Subí una imagen o escribí una idea y generá diseños en segundos</p>
            
            <div class="hero-buttons">
              <button @click="imageSourceMode = 'upload'" class="btn btn-primary">
                📁 Subir imagen
              </button>
              <button @click="imageSourceMode = 'generate'" class="btn btn-primary">
                🤖 Generar con IA
              </button>
            </div>
          </div>
          
          <!-- <div class="hero-showcase">
            <div class="showcase-image">
              <img src="./assets/logo-prendete-rock.jpg" alt="Showcase" />
            </div>
          </div> -->
        </div>

        <!-- marca de agua: se aplica vía CSS ::before para que quede centrada y no se recorte -->

        <!-- Carrusel de Ejemplos -->
        <div class="examples-section">
          <div class="example-card" v-for="i in 4" :key="i">
            <div class="example-placeholder"></div>
          </div>
          <button class="carousel-nav next">›</button>
        </div>
      </section>

      <!-- PASO 1B: SUBIR IMAGEN -->
      <section v-if="imageSourceMode === 'upload'" class="workflow-section">
        <button @click="goBackToChoice" class="btn btn-back">
          ← Volver
        </button>
        <ImageUploader @image-generated="onImageGenerated" />
      </section>

      <!-- PASO 1C: GENERAR CON IA -->
      <section v-if="imageSourceMode === 'generate'" class="workflow-section">
        <button @click="goBackToChoice" class="btn btn-back">
          ← Volver
        </button>
        <GenerateImage @image-generated="onImageGenerated" />
      </section>

      <!-- PASO 2: SELECCIONAR PRODUCTO -->
      <section v-if="generatedImage && !selectedProduct" class="workflow-section">
        <ProductSelector
          :productos="productos"
          @product-selected="onProductSelected"
        />
      </section>

      <!-- PASO 3: VISTA PREVIA -->
      <section v-if="selectedProduct && !orderData" class="workflow-section">
        <PreviewPanel
          :imagen-url="generatedImage"
          :producto="selectedProduct"
          :prompt="lastPrompt"
          @confirm-order="onConfirmOrder"
        />
      </section>

      <!-- PASO 4: CHECKOUT -->
      <section v-if="orderData" class="workflow-section">
        <CheckoutPanel
          :order="orderData"
          :imagen-url="generatedImage"
          :producto="selectedProduct"
        />
      </section>
    </main>

    <!-- Footer -->
    <footer class="app-footer">
      <div class="footer-content">
        <span>✅ Pago Seguro</span>
        <span>✅ Alta Calidad</span>
        <span>✅ Envío Rápido</span>
      </div>
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
import GenerateImage from './components/GenerateImage.vue'

const currentStep = ref(0)

const steps = ['Subí tu imagen', 'Elige producto', 'Vista previa', 'Pagar']

const imageSourceMode = ref(null) // null, 'upload', o 'generate'

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

function goBackToChoice() {
  imageSourceMode.value = null
}
</script>

<style scoped>
:root {
  /* Modo nocturno local (coherente con variables globales) */
  --color-primary: #06b6d4;
  --color-primary-dark: #0b7285;
  --color-secondary: #ffd54f;
  --color-accent: #67e8f9;
  --color-text: #e6eef8;
  --color-text-light: #9aa6b2;
  --color-border: rgba(255,255,255,0.06);
  --color-surface: #0f1724;
  --color-bg: #071226;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  /* background-color: var(--color-bg); */
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
}

/* NAVBAR */
.navbar {
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  width: 100%;
  z-index: 1100;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.navbar-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 700;
  font-size: 18px;
  color: var(--color-primary);
  letter-spacing: -0.3px;
}

.logo {
  font-size: 24px;
  height: 100%;
  display: flex;
  align-items: center;
}

.logo img {
  height: 100%;
  max-height: 64px; /* coincide con .navbar-container height */
  width: auto;
  display: block;
  object-fit: contain;
  border-radius: 8px;
}

.nav-menu {
  display: flex;
  gap: 32px;
  flex: 1;
  justify-content: center;
}

.nav-link {
  text-decoration: none;
  color: var(--color-text);
  font-weight: 500;
  transition: color 0.3s ease;
  position: relative;
}

.nav-link:hover,
.nav-link.active {
  color: var(--color-secondary);
}

.nav-link.active::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: var(--color-secondary);
}

.nav-actions {
  display: flex;
  gap: 12px;
}

.icon-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: background-color 0.3s ease;
}

.icon-btn:hover {
  background-color: var(--color-bg);
}

/* MAIN CONTENT */
.app-main {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 0 24px;
  padding-top: 64px; /* espacio para navbar fija */
  padding-bottom: 72px; /* espacio para footer fijo */
}

/* HERO SECTION */
.hero-section {
  display: flex;
  flex-direction: column;
  gap: 60px;
  padding: 60px 0;
  background: none !important;
  position: relative;
  overflow: visible;
}

.hero-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 80px;
  align-items: center;
  min-height: 500px;
}

.hero-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero-content { z-index: 2; position: relative; }


.hero-section::before {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  /* background-image: url('./assets/logo-prendete-rock.jpg'); */
  background-repeat: no-repeat;
  background-position: center 40px;
  background-size: 100% auto;
  opacity: 0.10;
  pointer-events: none;
  z-index: 0;
}

.hero-title {
  font-size: 35px;
  font-weight: 900;
  line-height: 1.1;
  color: var(--color-primary);
  margin: 0;
  letter-spacing: -0.5px;
}

.hero-subtitle {
  font-size: 18px;
  color: var(--color-text-light);
  line-height: 1.6;
  margin: 0;
  letter-spacing: 0.25px;
}

.hero-buttons {
  display: flex;
  gap: 12px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.btn {
  padding: 12px 28px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 16px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
  border: 2px solid var(--color-primary);
  font-size: 16px;
  padding: 14px 32px;
}

.btn-primary:hover {
  background-color: var(--color-primary-dark);
  border-color: var(--color-primary-dark);
  color: white;
  transform: translateY(-3px);
  box-shadow: 0 8px 16px rgba(6, 182, 212, 0.3);
}

.btn-secondary {
  background-color: var(--color-secondary);
  color: white;
  border: 2px solid var(--color-secondary);
  font-size: 16px;
  padding: 14px 32px;
}

.btn-secondary:hover {
  background-color: #2563eb;
  border-color: #2563eb;
  transform: translateY(-3px);
  box-shadow: 0 12px 20px rgba(37, 99, 235, 0.4);
}

.btn-variant {
  background-color: var(--color-surface);
  color: var(--color-accent);
  border: 2px solid var(--color-accent);
  padding: 10px 20px;
  font-size: 14px;
}

.btn-variant:hover {
  background-color: rgba(255, 213, 79, 0.08);
  border-color: var(--color-secondary);
  color: var(--color-secondary);
  transform: translateY(-2px);
}

.btn-back {
  background-color: var(--color-bg);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  padding: 10px 16px;
  font-size: 14px;
  margin-bottom: 20px;
}

.btn-back:hover {
  background-color: var(--color-border);
}

.hero-showcase {
  display: flex;
  justify-content: center;
  align-items: center;
}

.showcase-image {
  width: 100%;
  max-width: 400px;
  height: 500px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-border);
}

.showcase-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* EJEMPLOS CAROUSEL */
.examples-section {
  display: grid;
  grid-template-columns: repeat(4, 180px);
  gap: 16px;
  margin-top: 16px;
  position: relative;
  justify-content: center;
}

.example-card {
  aspect-ratio: 1 / 1;
  width: 100%;
  max-width: 180px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid var(--color-border);
}

.example-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
  border-color: var(--color-secondary);
}

.example-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #e0e7ff 0%, #f0f4ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
}

.carousel-nav {
  position: absolute;
  right: -50px;
  top: 50%;
  transform: translateY(-50%);
  background-color: var(--color-secondary);
  color: white;
  border: none;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  font-weight: bold;
}

.carousel-nav:hover {
  background-color: #2563eb;
  transform: translateY(-50%) scale(1.15);
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4);
}

/* WORKFLOW SECTION */
.workflow-section {
  padding: 40px 0;
  animation: fadeIn 0.3s ease;
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

/* FOOTER */
.app-footer {
  background: linear-gradient(135deg, var(--color-primary) 0%, #0f2946 100%);
  color: white;
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100vw; /* asegurar viewport-wide */
  margin-left: calc(50% - 50vw);
  padding: 10px 16px; /* más fino */
  box-shadow: 0 -2px 6px rgba(0, 0, 0, 0.06);
  box-sizing: border-box;
  z-index: 1050;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: center;
  gap: 48px;
  text-align: center;
  font-weight: 500;
  letter-spacing: 0.3px;
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .hero-container {
    grid-template-columns: 1fr;
    gap: 40px;
    min-height: auto;
  }

  .hero-title {
    font-size: 36px;
  }

  .hero-subtitle {
    font-size: 16px;
  }

  .hero-buttons {
    flex-direction: column;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .examples-section {
    grid-template-columns: repeat(2, 160px);
    justify-content: center;
  }

  .nav-menu {
    display: none;
  }

  .navbar-container {
    justify-content: space-between;
  }

  .footer-content {
    flex-direction: column;
    gap: 16px;
  }

  .carousel-nav {
    display: none;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 28px;
  }

  .examples-section {
    grid-template-columns: 1fr;
    gap: 12px;
    justify-content: center;
  }
}
</style>