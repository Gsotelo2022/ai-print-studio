<template>
  <div v-if="visible" class="modal-overlay" @click.self="cerrar">
    <div class="modal-container">
      <div class="modal-header">
        <h2>Editar Cliente</h2>
        <button @click="cerrar" class="btn-cerrar">×</button>
      </div>
      <div class="modal-body" v-if="clienteEditado">
        <div class="form-grupo">
          <label for="nombre">Nombre</label>
          <input type="text" id="nombre" v-model="clienteEditado.nombre">
        </div>
        <div class="form-grupo">
          <label for="email">Email</label>
          <input type="email" id="email" v-model="clienteEditado.email">
        </div>
        <div class="form-grupo">
          <label for="telefono">Teléfono</label>
          <input type="tel" id="telefono" v-model="clienteEditado.telefono">
        </div>
        <div class="form-grupo">
          <label for="tipo">Tipo de usuario</label>
          <select id="tipo" v-model="clienteEditado.tipo">
            <option value="cliente">Cliente</option>
            <option value="administrador">Administrador</option>
          </select>
        </div>
        <div class="form-grupo">
          <label for="bloqueado">Cuenta bloqueada</label>
          <select id="bloqueado" v-model="clienteEditado.cuenta_bloqueada">
            <option :value="true">Sí</option>
            <option :value="false">No</option>
          </select>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn-cancelar" @click="cerrar">Cancelar</button>
        <button class="btn-guardar" @click="guardar">Guardar Cambios</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue';

const props = defineProps({
  cliente: Object,
  visible: Boolean
});

const emit = defineEmits(['cerrar', 'guardar']);

const clienteEditado = ref(null);

watch(() => props.cliente, (nuevoValor) => {
  if (nuevoValor) {
    clienteEditado.value = { ...nuevoValor };
  } else {
    clienteEditado.value = null;
  }
}, { immediate: true });

const cerrar = () => {
  emit('cerrar');
};

const guardar = () => {
  emit('guardar', clienteEditado.value);
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-container {
  background: var(--color-surface);
  border-radius: var(--radius);
  width: 500px;
  max-width: 90%;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.btn-cerrar {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--color-text-secondary);
}

.modal-body {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-grupo {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-grupo label {
  font-weight: 500;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

.form-grupo input,
.form-grupo select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-background);
  color: var(--color-text);
  font-size: 1rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--color-border);
}

.btn-cancelar, .btn-guardar {
  padding: 10px 20px;
  border-radius: var(--radius-sm);
  border: none;
  cursor: pointer;
  font-weight: 500;
}

.btn-cancelar {
  background: var(--color-surface-soft);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.btn-guardar {
  background: var(--color-primary);
  color: white;
}
</style>
