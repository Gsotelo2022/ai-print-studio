<template>
  <section class="create-user-section">
    <div class="form-container">
      <div class="form-header">
        <!-- <div class="form-icon">👤</div> -->
        <h2 class="form-title">Registrarme</h2>
        <!-- <p class="form-subtitle">Completa tus datos para registrarte</p> -->
      </div>

      <form @submit.prevent="handleSubmit" class="registration-form">
        <!-- Row 1: Nombre + Email -->
        <div class="form-row">
          <!-- Nombre completo -->
          <div class="form-group">
            <label for="fullname" class="form-label">Nombre completo</label>
            <div class="input-wrapper">
              <span class="input-icon">👤</span>
              <input
                id="fullname"
                v-model="formData.fullname"
                type="text"
                placeholder="Ej: Juan Pérez"
                class="form-input"
                required
              />
            </div>
          </div>

          <!-- Email -->
          <div class="form-group">
            <label for="email" class="form-label">Email</label>
            <div class="input-wrapper">
              <span class="input-icon">✉️</span>
              <input
                id="email"
                v-model="formData.email"
                type="email"
                placeholder="Ej: juan@email.com"
                class="form-input"
                required
              />
            </div>
          </div>
        </div>

        <!-- Row 2: Teléfono + Contraseña -->
        <div class="form-row">
          <!-- Teléfono (opcional) -->
          <div class="form-group">
            <label for="phone" class="form-label">Teléfono <span class="optional">(opcional)</span></label>
            <div class="input-wrapper">
              <span class="input-icon">📞</span>
              <input
                id="phone"
                v-model="formData.phone"
                type="tel"
                placeholder="Ej: 11 1234-5678"
                class="form-input"
              />
            </div>
          </div>

          <!-- Contraseña -->
          <div class="form-group">
            <label for="password" class="form-label">Contraseña</label>
            <div class="input-wrapper">
              <span class="input-icon">🔒</span>
              <input
                id="password"
                v-model="formData.password"
                type="password"
                placeholder="••••••••"
                class="form-input"
                required
              />
            </div>
          </div>
        </div>

        <!-- Row 3: Confirmar Contraseña -->
        <div class="form-row">
          <!-- Confirmar Contraseña -->
          <div class="form-group">
            <label for="confirmPassword" class="form-label">Confirmar contraseña</label>
            <div class="input-wrapper">
              <span class="input-icon">🔒</span>
              <input
                id="confirmPassword"
                v-model="formData.confirmPassword"
                type="password"
                placeholder="••••••••"
                class="form-input"
                required
              />
            </div>
          </div>
        </div>

        <!-- Submit Button Row -->
        <div class="form-row button-row">
          <button type="submit" class="btn btn-submit">
            <span class="btn-icon">👤</span>
            Registrarme
          </button>
        </div>
      </form>

      <!-- Login Link -->
      <div class="login-link">
        <span>¿Ya tenés cuenta?</span>
        <a href="#" @click.prevent="$emit('go-to-login')" class="link">Inicia sesión</a>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['go-to-login', 'user-created'])

import { useApi } from '../composables/useApi'
const { registerUser } = useApi()

const formData = ref({
  fullname: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: ''
})

const loading = ref(false)

async function handleSubmit() {
  // Validar que las contraseñas coincidan
  if (formData.value.password !== formData.value.confirmPassword) {
    alert('Las contraseñas no coinciden')
    return
  }

  // Validar que la contraseña tenga al menos 6 caracteres
  if (formData.value.password.length < 6) {
    alert('La contraseña debe tener al menos 6 caracteres')
    return
  }

  // Llamar al endpoint de registro
  loading.value = true
  try {
    const payload = {
      fullname: formData.value.fullname,
      email: formData.value.email,
      phone: formData.value.phone,
      password: formData.value.password,
    }

    const data = await registerUser(payload)
    // Emitir evento con la respuesta del backend
    emit('user-created', data)

    // Resetear formulario
    formData.value = {
      fullname: '',
      email: '',
      phone: '',
      password: '',
      confirmPassword: ''
    }
  } catch (err) {
    alert('Error registrando usuario: ' + (err.message || err))
  } finally {
    loading.value = false
  }
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
  --font-display: 'Orbitron', cursive;
}

.create-user-section {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  min-height: calc(100vh - 136px);
  padding: 20px 24px;
}

.form-container {
  background: rgba(6, 182, 212, 0.08);
  border: 2px solid var(--color-primary);
  border-radius: 10px;
  padding: 25px;
  width: 60%;
  max-width: 900px;
  transition: all 0.2s ease;
}

.form-container:hover {
  background: rgba(6, 182, 212, 0.12);
  box-shadow: 0 4px 12px rgba(6, 182, 212, 0.2);
}

.form-header {
  text-align: center;
  margin-bottom: 24px;
  border-bottom: 2px solid var(--color-primary);
  padding-bottom: 14px;
  transition: all 0.2s ease;
}

.form-header:hover {
  border-bottom-color: var(--color-accent);
}

.form-icon {
  font-size: 28px;
  margin-bottom: 6px;
  display: inline-block;
}

.form-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-primary);
  margin-bottom: 4px;
  font-family: var(--font-display);
  letter-spacing: 2px;
  text-transform: uppercase;
}

.form-subtitle {
  font-size: 11px;
  color: var(--color-text);
  margin: 0;
  font-family: var(--font-display);
  letter-spacing: 1px;
}

.registration-form {
  display: flex;
  flex-direction: column;
  gap: 9px;
  margin-bottom: 18px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 9px;
}

.button-row {
  grid-template-columns: 1fr 1fr;
  align-items: center;
}

.button-row .btn-submit {
  /* Centrar el botón: ocupar ambas columnas y centrarse */
  grid-column: 1 / -1;
  justify-self: center;
  /* Mantener la reducción de ancho previa (56% del contenedor) */
  width: 56%;
  margin-bottom: 20px;
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
  margin-bottom: 4px;
}

.optional {
  font-size: 11px;
  color: var(--color-accent);
  font-weight: 400;
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
  border: 2px solid var(--color-primary);
  border-radius: 8px;
  font-size: 12px;
  font-family: inherit;
  background-color: rgba(10, 14, 26, 0.95);
  color: var(--color-text);
  transition: all 0.2s ease;
}

.form-input::placeholder {
  color: var(--color-text);
  opacity: 0.5;
}

.form-input:hover {
  box-shadow: 0 2px 8px rgba(6, 182, 212, 0.2);
}

.form-input:focus {
  outline: none;
  border-color: var(--color-accent);
  background-color: rgba(10, 14, 26, 1);
  box-shadow: 0 4px 12px rgba(6, 182, 212, 0.2);
}

.btn-submit {
  width: 100%;
  /* reducir el alto: padding vertical menor (10% menos) */
  padding: 7px 14px;
  /* Usar las mismas propiedades visuales que el botón "volver" */
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

.btn-icon {
  font-size: 18px;
}

.btn-submit:hover {
  background-color: var(--color-border);
}

.btn-submit:active {
  transform: translateY(0);
}

.login-link {
  text-align: center;
  font-size: 11px;
  color: var(--color-text);
  font-family: var(--font-display);
  letter-spacing: 0.5px;
}

.login-link span {
  margin-right: 4px;
}

.link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 600;
  font-family: var(--font-display);
  transition: color 0.2s ease;
}

.link:hover {
  color: var(--color-accent);
  text-decoration: underline;
}

@media (max-width: 480px) {
  .form-container {
    padding: 24px 16px;
    max-width: 100%;
  }

  .form-title {
    font-size: 20px;
  }

  .form-input {
    padding: 8px 8px 8px 32px;
    font-size: 14px;
  }

  .btn-submit {
    font-size: 13px;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 10px;
  }
}
</style>
