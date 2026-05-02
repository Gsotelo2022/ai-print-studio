<template>
  <div class="app">
    <!-- Header Navbar (oculto para admin) -->
    <header v-if="userType !== 'admin'" class="navbar">
      <div class="navbar-container">
        <div class="logo-section" @click="openHome">
          <div class="logo"><img src="./assets/logo-prendete-rock.jpg" alt="Logo"></div>
          <span class="brand">Prendete Rock</span>
        </div>
        <nav class="nav-menu">
          <!-- Sin usuario logueado: mostrar Home, Registrarme, Ingresar -->
          <template v-if="!userLogged">
            <a href="#" @click.prevent="openHome" class="nav-link">Home</a>
            <a href="#" @click.prevent="openRegister" class="nav-link">Registrarme</a>
            <a href="#" @click.prevent="openLogin" class="nav-link">Ingresar</a>
          </template>
          
          <!-- Cliente logueado -->
          <template v-if="userLogged && userType === 'cliente'">
            <a href="#" @click.prevent="openHome" class="nav-link">Home</a>
            <a href="#" @click.prevent="goToDashboard" class="nav-link">Crear</a>
            <a href="#" @click.prevent="goToMyDesigns" class="nav-link">Mis Diseños</a>
            <a href="#" @click.prevent="goToMyOrders" class="nav-link">Mis Pedidos</a>
            <a href="#" @click.prevent="handleLogout" class="nav-link">Cerrar Sesión</a>
          </template>
        </nav>
      </div>
    </header>

    <main class="app-main">
      <!-- PANEL DE ADMINISTRADOR -->
      <section v-if="userLogged && userType === 'admin'" class="admin-section">
        <AdminDashboard @logout="handleLogout" />
      </section>

      <!-- PASO 0: REGISTRO -->
      <section v-if="showRegistrationForm && userType !== 'admin'" class="workflow-section">
        <CreateUser
          @user-created="onUserCreated"
          @go-to-login="handleGoToLogin"
        />
      </section>

      <!-- LOGIN -->
      <section v-if="showLoginForm && userType !== 'admin'" class="workflow-section">
      <Login
        @login-success="onLoginSuccess"
        @go-to-register="openRegister"
        @forgot-password="handleForgotPassword"
      />
      </section>

      <!-- DASHBOARD USUARIO LOGUEADO: Opciones iniciales (Subir imagen o Generar con IA) -->
      <section v-if="userLogged && !imageSourceMode && !generatedImage && !showMyDesigns && !showMyOrders && userType === 'cliente'" class="workflow-section dashboard-section">
        <div class="dashboard-header">
          <h2 class="dashboard-title">Creá estampados únicos con IA</h2>
          <p class="dashboard-subtitle">Subí una imagen o escribe una idea y genera diseños en segundos</p>
        </div>
        <div class="dashboard-options">
          <button @click="imageSourceMode = 'upload'" class="option-card">
            <div class="option-icon">📁</div>
            <h3>Subir imagen</h3>
            <p>Cargá tu propia imagen para personalizarla</p>
          </button>
          <button @click="imageSourceMode = 'generate'" class="option-card">
            <div class="option-icon">🤖</div>
            <h3>Generar con IA</h3>
            <p>Describe tu idea y deja que la IA genere diseños</p>
          </button>
        </div>
      </section>

      <!-- PASO 0: HERO SECTION (solo sin usuario logueado) -->
      <section v-if="!userLogged && !imageSourceMode && !showRegistrationForm && !showLoginForm" class="hero-section">
        <div class="">
          <div class="hero-content">
            <h1 class="hero-title">Diseños Únicos a tu estilo</h1>
            <p class="hero-subtitle">Crea tus propias estampas personalizables subiendo tus ideas e imágenes, y deja que nuestra IA te ayude a generar diseños únicos.</p>
            
            <div class="hero-buttons">
              <button @click="openRegister" class="btn btn-primary btn-large">
                🚀 Comenzar ahora
              </button>
              <button @click="openLogin" class="btn btn-secondary btn-large">
                🔐 Ya tengo cuenta
              </button>
            </div>

            <!-- Características -->
            <div class="hero-features">
              <div class="feature-item">
                <span class="feature-icon">🤖</span>
                <span class="feature-text">IA Generativa</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">🎨</span>
                <span class="feature-text">Diseños Únicos</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">⚡</span>
                <span class="feature-text">Entrega Rápida</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- PASO 1B: SUBIR IMAGEN -->
      <section v-if="userLogged && imageSourceMode === 'upload' && userType === 'cliente'" class="workflow-section">
        <ImageUploader @image-generated="onImageGenerated" @go-back="goToDashboard" />
      </section>

      <!-- PASO 1C: GENERAR CON IA -->
      <section v-if="userLogged && imageSourceMode === 'generate' && userType === 'cliente'" class="workflow-section">
        <GenerateImage @image-generated="onImageGenerated" @go-back="goToDashboard" />
      </section>

      <!-- PASO 2: EDITAR/REMOVER FONDO DE IMAGEN -->
      <section v-if="userLogged && showBackgroundRemover && generatedImage && userType === 'cliente'" class="workflow-section">
        <BackgroundRemover
          :imagenUrl="generatedImage"
          @image-processed="onImageProcessed"
          @skip-editing="onSkipEditing"
          @go-back="onBackgroundRemoverGoBack"
        />
      </section>

      <!-- PASO 3: SELECCIONAR PRODUCTO -->
      <section v-if="userLogged && generatedImage && !selectedProduct && !showBackgroundRemover && userType === 'cliente'" class="workflow-section">
        <ProductSelector
          :productos="productos"
          :loading="productosLoading"
          :loaded="productosLoaded"
          @product-selected="onProductSelected"
          @go-back="onProductSelectorGoBack"
        />
      </section>

      <!-- GALERÍA DE DISEÑOS -->
      <section v-if="userLogged && showMyDesigns && userType === 'cliente' && currentUser" class="workflow-section">
        <MisDisenosGaleria
          :user-id="currentUser.id_usuario || currentUser.user_id || currentUser.id"
          @design-selected="onDesignSelected"
          @go-back="closeMyDesigns"
        />
      </section>

      <!-- PASO 3: VISTA PREVIA -->
      <section v-if="userLogged && selectedProduct && !orderData && userType === 'cliente'" class="workflow-section">
        <PreviewPanel
          :imagen-url="generatedImage"
          :producto="selectedProduct"
          :prompt="lastPrompt"
          :user-id="currentUser?.id_usuario || currentUser?.user_id || currentUser?.id"
          @confirm-order="onConfirmOrder"
          @go-back="onPreviewPanelGoBack"
        />
      </section>

      <!-- PASO 4: CHECKOUT -->
      <section v-if="userLogged && orderData && userType === 'cliente'" class="workflow-section">
        <CheckoutPanel
          :order="orderData"
          :imagen-url="generatedImage"
          :producto="selectedProduct"
        />
      </section>
    </main>

    <!-- Footer (oculto para admin) -->
    <footer v-if="userType !== 'admin'" class="app-footer">
      <div class="footer-content">
        <span>✅ Pago Seguro</span>
        <span>✅ Alta Calidad</span>
        <span>✅ Envío Rápido</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'

import ImageUploader from './components/ImageUploader.vue'
import CreateUser from './components/CreateUser.vue'
import Login from './components/Login.vue'
import BackgroundRemover from './components/BackgroundRemover.vue'
import ProductSelector from './components/ProductSelector.vue'
import PreviewPanel from './components/PreviewPanel.vue'
import CheckoutPanel from './components/CheckoutPanel.vue'
import GenerateImage from './components/GenerateImage.vue'
import AdminDashboard from './components/AdminDashboard.vue'
import MisDisenosGaleria from './components/MisDisenosGaleria.vue'

import { useApi } from './composables/useApi.js'

// ✅ INSTANCIA ÚNICA
const api = useApi()

// ============================
// STATE
// ============================

const userLogged = ref(false)
const userType = ref('cliente')
const showRegistrationForm = ref(false)
const showLoginForm = ref(false)
const showMyDesigns = ref(false)
const showMyOrders = ref(false)
const currentUser = ref(null)

const imageSourceMode = ref(null)
const generatedImage = ref(null)
const lastPrompt = ref('')
const showBackgroundRemover = ref(false)

const uploadedImageMode = ref(false) 

const selectedProduct = ref(null)
const orderData = ref(null)

// ============================
// PRODUCTOS
// ============================

//const productos = reactive({})
const productos = ref([])
const productosLoading = ref(false)
const productosLoaded = ref(false)

// ============================
// AUTH
// ============================
function onImageGenerated(data) {
  generatedImage.value = data.imagen_url || data.url || data

  // Si viene de upload, marcamos flag
  uploadedImageMode.value = true

  // Mostrar background remover
  showBackgroundRemover.value = true

  console.log('🖼️ Imagen generada/subida:', generatedImage.value)
}

function goToDashboard() {
  imageSourceMode.value = null
  generatedImage.value = null
  showBackgroundRemover.value = false
  selectedProduct.value = null
  orderData.value = null

  // 🔥 ESTO TE FALTABA
  showMyDesigns.value = false
  showMyOrders.value = false

  console.log('🏠 Volviendo al dashboard')
}

function onLoginSuccess(data) {
  localStorage.setItem('token', data.token)
  localStorage.setItem('userId', data.user_id)
  localStorage.setItem('userName', data.nombre)
  localStorage.setItem('userType', data.tipo)

  currentUser.value = {
    id_usuario: data.user_id,
    nombre: data.nombre,
    email: data.email,
    tipo: data.tipo
  }

  userLogged.value = true
  userType.value = data.tipo

  showLoginForm.value = false

  cargarProductosDelAgente()
  openHome()
}

function handleLogout() {
  localStorage.clear()

  userLogged.value = false
  userType.value = 'cliente'
  currentUser.value = null

  openHome()
}

// ============================
// NAV
// ============================

function openHome() {
  imageSourceMode.value = null
  generatedImage.value = null
  showBackgroundRemover.value = false
  selectedProduct.value = null
  orderData.value = null
  showRegistrationForm.value = false
  showLoginForm.value = false
  showMyDesigns.value = false
  showMyOrders.value = false
}

function openLogin() {
  showLoginForm.value = true
  showRegistrationForm.value = false
}

function openRegister() {
  showRegistrationForm.value = true
  showLoginForm.value = false
}

// ============================
// FLOW
// ============================

function onImageProcessed(data) {
  generatedImage.value = data.imagen_url
  showBackgroundRemover.value = false
  uploadedImageMode.value = false
  
  console.log('✅ Imagen procesada, mostrar ProductSelector')
}

// ===== FUNCIÓN NUEVA 1 =====
function onSkipEditing() {
  showBackgroundRemover.value = false
  uploadedImageMode.value = false
  
  if (!productosLoaded.value) {
    cargarProductosDelAgente()
  }
  
  console.log('⏭️ Saltando edición, mostrar ProductSelector')
}

// ===== FUNCIÓN NUEVA 2 =====
function onBackgroundRemoverGoBack() {
  showBackgroundRemover.value = false
  uploadedImageMode.value = false
  generatedImage.value = null
  imageSourceMode.value = null
  
  console.log('↩️ Volviendo desde BackgroundRemover')
}

function onProductSelected(product) {
  selectedProduct.value = product
}

// ===== FUNCIÓN NUEVA 3 =====
function onProductSelectorGoBack() {
  selectedProduct.value = null
  generatedImage.value = null
  uploadedImageMode.value = false
  imageSourceMode.value = null
  showBackgroundRemover.value = false
  
  console.log('↩️ Volviendo desde ProductSelector')
}

function onConfirmOrder(order) {
  orderData.value = order
}

const cargarProductosDelAgente = async () => {
  productosLoading.value = true
  
  try {
    const data = await api.get('/productos')
    if (Array.isArray(data)) {
      productos.value = data
      productosLoaded.value = true
      console.log('✅ Productos cargados:', data.length)
    } else {
      console.warn('⚠️ Sin productos disponibles')
    }
  } catch (error) {
    console.error('❌ Error cargando productos:', error)
  } finally {
    productosLoading.value = false
  }
}

onMounted(() => {
  const token = localStorage.getItem('token')
  const userId = localStorage.getItem('userId')
  const userName = localStorage.getItem('userName')
  const storedUserType = localStorage.getItem('userType')

  if (token && userId) {
    currentUser.value = {
      id_usuario: parseInt(userId),
      nombre: userName,
      tipo: storedUserType
    }

    userLogged.value = true
    userType.value = storedUserType || 'cliente'

    cargarProductosDelAgente()
  }
})

// persist user
watch(currentUser, (val) => {
  if (val) {
    localStorage.setItem('currentUser', JSON.stringify(val))
  }
})

</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');

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
  --font-display: 'Orbitron', cursive;
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
  /* Fondo con imagen proporcionada */
  background-image: url('./assets/background.png');
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
  background-attachment: fixed;
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
  font-family: var(--font-display);
  color: var(--color-primary);
  letter-spacing: 1px;
  cursor: pointer;
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
  justify-content: flex-end;
  align-items: center;
}

.nav-link {
  text-decoration: none;
  color: var(--color-text);
  font-weight: 500;
  font-family: var(--font-display);
  font-size: 16px;
  letter-spacing: 1px;
  transition: color 0.3s ease;
  position: relative;
}

.nav-link:hover {
  color: var(--color-secondary);
}

.nav-link:hover::after {
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
  width: 50%;
}

.hero-content { z-index: 2; position: relative; }


.hero-section::before {
  /* content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  background-image: url('./assets/logo-prendete-rock.jpg'); 
  background-repeat: no-repeat;
  background-position: center 40px;
  background-size: 100% auto;
  opacity: 0.10;
  pointer-events: none;
  z-index: 0; */
}

.hero-title {
  font-size: 35px;
  font-weight: 900;
  line-height: 1.1;
  color: var(--color-primary);
  margin: 0;
  letter-spacing: 2px;
  font-family: var(--font-display);
}

.hero-subtitle {
  font-size: 18px;
  color: var(--color-text-light);
  line-height: 1.6;
  margin: 0;
  letter-spacing: 0.5px;
  font-family: var(--font-display);
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

.btn-large {
  padding: 18px 40px;
  font-size: 18px;
  font-weight: 700;
}

.hero-features {
  display: flex;
  gap: 24px;
  margin-top: 16px;
  flex-wrap: wrap;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(6, 182, 212, 0.1);
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid rgba(6, 182, 212, 0.2);
}

.feature-icon {
  font-size: 20px;
}

.feature-text {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-primary);
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
  grid-template-columns: repeat(3, 180px);
  gap: 16px;
  /* Subir el carrusel 50px respecto a la posición previa (60px -> 10px) */
  margin-top: 10px;
  position: relative;
  justify-content: flex-start;
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

/* DASHBOARD SECTION */
.dashboard-section {
  display: flex;
  flex-direction: column;
  gap: 40px;
  padding: 60px 0;
  align-items: center;
}

.dashboard-header {
  text-align: center;
  max-width: 700px;
}

.dashboard-title {
  font-size: 35px;
  font-weight: 900;
  color: var(--color-primary);
  margin-bottom: 16px;
  letter-spacing: 2px;
  font-family: var(--font-display);
}

.dashboard-subtitle {
  font-size: 18px;
  color: var(--color-text-light);
  line-height: 1.6;
  letter-spacing: 0.5px;
}

.dashboard-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 32px;
  width: 100%;
  max-width: 600px;
}

.option-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 32px 24px;
  background: rgba(6, 182, 212, 0.08);
  border: 2px solid var(--color-primary);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: var(--font-display);
  text-decoration: none;
}

.option-card:hover {
  background: rgba(6, 182, 212, 0.15);
  border-color: var(--color-accent);
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(6, 182, 212, 0.2);
}

.option-icon {
  font-size: 48px;
}

.option-card h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-primary);
  margin: 0;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.option-card p {
  font-size: 12px;
  color: var(--color-text-light);
  margin: 0;
  text-align: center;
  line-height: 1.4;
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
    justify-content: flex-start;
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

  .dashboard-options {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .dashboard-title {
    font-size: 28px;
  }

  .dashboard-subtitle {
    font-size: 16px;
  }

  .option-card {
    padding: 24px;
  }

  .option-icon {
    font-size: 40px;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 28px;
  }

  .examples-section {
    grid-template-columns: 1fr;
    gap: 12px;
    justify-content: flex-start;
  }
}

/* ESTILOS PANEL ADMINISTRADOR */
.admin-section {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  background: var(--color-bg);
  overflow: hidden;
}

/* Cuando admin está activo, ocultar el main-content */
.app:has(.admin-section) {
  overflow: hidden;
}

.app:has(.admin-section) .app-main {
  padding: 0;
  margin: 0;
  max-width: none;
}
</style>