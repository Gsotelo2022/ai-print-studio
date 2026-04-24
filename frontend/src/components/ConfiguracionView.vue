<template>
  <div class="configuracion-view">
    <div class="view-header">
      <h1 class="view-title">⚙️ Configuración</h1>
      <p class="view-description">Ajusta la configuración general del sistema</p>
    </div>

    <div class="config-sections">
      <!-- Configuración general -->
      <div class="config-card">
        <h2 class="config-title">🏪 Información del negocio</h2>
        <div class="config-form">
          <div class="form-group">
            <label>Nombre del negocio</label>
            <input type="text" value="Prendete Rock" class="form-input" />
          </div>
          <div class="form-group">
            <label>Email de contacto</label>
            <input type="email" value="contacto@prendeterock.com" class="form-input" />
          </div>
          <div class="form-group">
            <label>Teléfono</label>
            <input type="tel" value="+54 11 1234-5678" class="form-input" />
          </div>
          <button class="btn-guardar">Guardar cambios</button>
        </div>
      </div>

      <!-- Configuración de pagos -->
      <div class="config-card">
        <h2 class="config-title">💳 Métodos de pago</h2>
        <div class="config-form">
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" checked />
              <span>Mercado Pago</span>
            </label>
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" />
              <span>Transferencia bancaria</span>
            </label>
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" />
              <span>Efectivo contra entrega</span>
            </label>
          </div>
          <button class="btn-guardar">Guardar cambios</button>
        </div>
      </div>

      <!-- Configuración de notificaciones -->
      <div class="config-card">
        <h2 class="config-title">🔔 Notificaciones</h2>
        <div class="config-form">
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" checked />
              <span>Notificar nuevos pedidos</span>
            </label>
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" checked />
              <span>Notificar pagos recibidos</span>
            </label>
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" />
              <span>Notificar nuevos clientes</span>
            </label>
          </div>
          <button class="btn-guardar">Guardar cambios</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Configuraciones del sistema
</script>

<style scoped>
.configuracion-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.view-header {
  margin-bottom: 8px;
}

.view-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.view-description {
  font-size: 0.95rem;
  color: var(--color-text-secondary);
  margin: 0;
}

.config-sections {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.config-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 24px;
}

.config-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 20px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.config-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 500px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--color-text);
}

.form-input {
  padding: 10px 12px;
  background: var(--color-bg);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 8px 0;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.checkbox-label span {
  font-size: 0.9rem;
  color: var(--color-text);
}

.btn-guardar {
  padding: 10px 20px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
  font-weight: 500;
  align-self: flex-start;
}

.btn-guardar:hover {
  background: var(--color-primary-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}
</style>
