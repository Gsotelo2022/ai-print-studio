<template>
  <section class="login-section">
    <div class="form-container">
      <div class="form-header">
        <h2 class="form-title">Iniciar sesión</h2>
        <p class="form-subtitle">Ingresá para continuar</p>
      </div>

      <form @submit.prevent="handleSubmit" class="login-form">
        <div v-if="error" class="error-message">
          ⚠️ {{ error }}
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="email" class="form-label">Email</label>
            <div class="input-wrapper">
              <span class="input-icon">✉️</span>
              <input
                id="email"
                v-model="form.email"
                type="email"
                placeholder="tu@email.com"
                class="form-input"
                required
              />
            </div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="password" class="form-label">Contraseña</label>
            <div class="input-wrapper">
              <span class="input-icon">🔒</span>
              <input
                id="password"
                v-model="form.password"
                type="password"
                placeholder="••••••••"
                class="form-input"
                required
              />
            </div>
          </div>
        </div>

        <div class="form-row small-row">
          <label class="remember">
            <input type="checkbox" v-model="form.remember" />
            Recordarme
          </label>
          <a href="#" class="link-forgot" @click.prevent="onForgot">¿Olvidaste tu contraseña?</a>
        </div>

        <div class="form-row button-row">
          <button type="submit" class="btn btn-back">
            <span class="btn-icon">↪️</span>
            Ingresar
          </button>
        </div>
      </form>

      <div class="login-link small">
        <span>¿No tenés cuenta?</span>
        <a href="#" @click.prevent="$emit('go-to-register')" class="link">Creá una ahora</a>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useApi } from '../composables/useApi'

const emit = defineEmits(['login-success', 'go-to-register', 'forgot-password'])

const { loginUser } = useApi()

const form = ref({
  email: '',
  password: '',
  remember: false
})

const loading = ref(false)
const error = ref(null)

async function handleSubmit() {
  loading.value = true
  error.value = null
  
  try {
    const payload = {
      email: form.value.email,
      password: form.value.password,
    }

    const user = await loginUser(payload)

    console.log("RESPUESTA LOGIN:", user)

    if (user?.token) {
      // ✅ GUARDAR JWT Y DATOS DE USUARIO EN LOCALSTORAGE
      localStorage.setItem('token', user.token)
      localStorage.setItem('userId', user.id || user.id_usuario || '')
      localStorage.setItem('userName', user.nombre || user.name || user.email)
      localStorage.setItem('userType', user.tipo || user.userType || 'cliente')
      
      // Emitir éxito con datos del usuario
      emit('login-success', user)
    } else {
      error.value = 'Error: No se recibió token de autenticación'
    }

  } catch (err) {
    console.error(err)
    error.value = err.message || 'Error al iniciar sesión'
  } finally {
    loading.value = false
  }
}
function onForgot() {
  emit('forgot-password')
}
</script>

<style scoped>
:root {
  --color-primary: #06b6d4;
  --color-primary-dark: #0b7285;
  --color-surface: #0f1724;
  --color-accent: #ffd54f;
  --color-text: #e6eef8;
  --color-border: rgba(255, 255, 255, 0.06);
  --color-bg: #071226;
  --font-display: 'Orbitron', cursive;
}

.login-section {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 136px);
  padding: 20px 24px;
}

.form-container {
  background: rgba(6, 182, 212, 0.04);
  border: 2px solid var(--color-primary);
  border-radius: 10px;
  padding: 25px;
  width: 420px;
  max-width: 95%;
  transition: all 0.2s ease;
}

.form-header {
  text-align: center;
  margin-bottom: 18px;
}

.form-title {
  font-size: 20px;
  font-weight: 800;
  color: var(--color-primary);
  margin-bottom: 4px;
  font-family: var(--font-display);
}

.form-subtitle {
  font-size: 12px;
  color: var(--color-text);
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 9px;
  margin-bottom: 12px;
}

.error-message {
  padding: 10px;
  background-color: #fee;
  border: 2px solid #fcc;
  border-radius: 8px;
  color: #c33;
  font-size: 13px;
  margin-bottom: 8px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 9px;
}

.small-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text);
  display: flex;
  align-items: center;
  gap: 4px;
  font-family: var(--font-display);
  letter-spacing: 1px;
  text-transform: uppercase;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 12px;
  font-size: 16px;
  pointer-events: none;
  color: var(--color-primary);
}

.form-input {
  width: 100%;
  padding: 7px 9px 7px 31px;
  border: 2px solid var(--color-border);
  border-radius: 8px;
  font-size: 13px;
  background-color: rgba(10, 14, 26, 0.95);
  color: var(--color-text);
  transition: all 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 4px 12px rgba(6, 182, 212, 0.12);
}

.remember {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--color-text);
}

.link-forgot {
  color: var(--color-primary);
  text-decoration: none;
  font-size: 13px;
}

.link-forgot:hover { text-decoration: underline; }

.button-row {
  grid-column: 1 / -1;
}

.btn-submit {
  width: 100%;
  /* reducir el alto: padding vertical menor (igual que CreateUser) */
  padding: 7px 14px;
  /* Usar las mismas propiedades visuales que el botón de registro */
  background-color: var(--color-bg);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 700;
  font-family: var(--font-display);
  letter-spacing: 2px;
  text-transform: uppercase;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 8px;
  transition: all 0.2s ease;
}

.btn-submit:hover {
  background-color: var(--color-border);
}

.btn-submit:active {
  transform: translateY(0);
}

.login-link.small {
  text-align: center;
  margin-top: 10px;
  font-size: 13px;
}

.link { color: var(--color-primary); text-decoration: none; font-weight: 600; }
.link:hover { text-decoration: underline; }

@media (max-width: 480px) {
  .form-container { width: 100%; padding: 18px; }
}

</style>
