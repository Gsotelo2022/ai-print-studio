<template>
  <div class="mis-pedidos-container">
    <div class="header">
      <h2 class="title">Mis Pedidos</h2>
      <button @click="$emit('go-back')" class="btn btn-back">Volver</button>
    </div>

    <div v-if="cargando" class="loading-state">
      <p>Cargando tus pedidos...</p>
    </div>

    <div v-if="error" class="error-state">
      <p>Hubo un error al cargar tus pedidos. Por favor, intenta de nuevo.</p>
      <button @click="cargarPedidos">Reintentar</button>
    </div>

    <div v-if="!cargando && pedidos.length === 0 && !error" class="empty-state">
      <p>Aún no has realizado ningún pedido.</p>
      <button @click="$emit('go-back')" class="btn btn-back">Crear mi primer diseño</button>
    </div>

    <div v-if="!cargando && pedidos.length > 0" class="pedidos-list">
      <div v-for="pedido in pedidos" :key="pedido.id_pedido" class="pedido-card">
        <div class="pedido-header">
          <span class="pedido-fecha">{{ formatDate(pedido.fecha_pedido) }}</span>
          <span :class="['pedido-estado', getEstadoClass(pedido.estado)]">{{ pedido.estado }}</span>
        </div>
        <div class="pedido-body">
          <div class="pedido-items">
            <div v-for="item in pedido.items" :key="item.id_item" class="pedido-item">
              <div v-if="item.ruta_thumbnail" class="thumbnail-wrapper">
                <img :src="item.ruta_thumbnail" alt="thumbnail" class="item-thumbnail" @error="onImageError"/>
              </div>
              <div v-else class="thumbnail-placeholder">
                <span>📷</span>
              </div>
              <div class="item-info">
                <p class="item-producto">{{ item.nombre_producto }} ({{ item.variante_info }})</p>
                <p class="item-cantidad">Cantidad: {{ item.cantidad }}</p>
              </div>
            </div>
          </div>
          <div class="pedido-total">
            <p>Total: <strong>{{ formatCurrency(pedido.total) }}</strong></p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useApi } from '../composables/useApi.js';

const props = defineProps({
  userId: {
    type: Number,
    required: false
  }
});

const emit = defineEmits(['go-back']);

const pedidos = ref([]);
const cargando = ref(false);
const error = ref(null);
const api = useApi();

// ✅ OBTENER userId DE LOCALSTORAGE SI NO VIENE EN PROPS
const userId = computed(() => {
  if (props.userId) return props.userId;
  const stored = localStorage.getItem('userId');
  return stored ? parseInt(stored) : null;
});

async function cargarPedidos() {
  if (!userId.value) {
    console.error('No userId available');
    return;
  }
  cargando.value = true;
  error.value = null;
  
  try {
    pedidos.value = await api.getMisPedidos(userId.value);
  } catch (err) {
    error.value = err.message || 'Error al cargar pedidos';
    console.error('Error cargando pedidos:', err);
  } finally {
    cargando.value = false;
  }
}

function formatDate(dateString) {
  const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
  return new Date(dateString).toLocaleDateString('es-ES', options);
}

function formatCurrency(value) {
  return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(value);
}

function getEstadoClass(estado) {
  return `estado-${estado.toLowerCase().replace(' ', '-')}`;
}

function onImageError(event) {
  event.target.style.display = 'none';
}


onMounted(() => {
  cargarPedidos();
});
</script>

<style scoped>
:root {
  --color-primary: #06b6d4;
  --color-primary-dark: #0b7285;
  --color-surface: #0f1724;
  --color-text: #e6eef8;
  --color-text-secondary: #9aa6b2;
  --color-border: rgba(255, 255, 255, 0.06);
  --color-bg: #071226;
  --color-success: #27ae60;
  --color-error: #ff6b6b;
  --color-warning: #f39c12;
}

.mis-pedidos-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 2rem;
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: 12px;
  box-shadow: 0 6px 18px rgba(2, 6, 23, 0.6);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 1rem;
}

.title {
  font-size: 2rem;
  color: var(--color-primary);
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  background: transparent;
  border: 2px solid var(--color-primary);
  color: var(--color-primary);
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: var(--color-primary);
  color: white;
  transform: translateY(-2px);
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  background: var(--color-primary);
  border: 2px solid var(--color-primary);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background: var(--color-primary-dark);
  transform: translateY(-2px);
}

.pedidos-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.pedido-card {
  border: 1px solid var(--color-border);
  background: var(--color-bg);
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.pedido-card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 6px 12px rgba(6, 182, 212, 0.2);
  transform: translateY(-2px);
}

.pedido-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(6, 182, 212, 0.05);
  padding: 0.75rem 1rem;
  font-size: 0.9rem;
  border-bottom: 1px solid var(--color-border);
}

.pedido-fecha {
  color: var(--color-text-secondary);
}

.pedido-estado {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: capitalize;
}

.estado-pendiente {
  background-color: var(--color-warning);
  color: white;
}

.estado-en-proceso {
  background-color: #3498db;
  color: white;
}

.estado-completado {
  background-color: var(--color-success);
  color: white;
}

.estado-enviado {
  background-color: var(--color-primary);
  color: white;
}

.estado-cancelado {
  background-color: var(--color-error);
  color: white;
}

.pedido-body {
  padding: 1rem;
}

.pedido-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.pedido-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.item-thumbnail {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
  border: 2px solid var(--color-border);
}

.thumbnail-wrapper {
  flex-shrink: 0;
}

.thumbnail-placeholder {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  border: 2px dashed var(--color-border);
  background: var(--color-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  flex-shrink: 0;
}

.item-info p {
  margin: 0;
  color: var(--color-text);
}

.item-producto {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 0.25rem;
}

.item-cantidad {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.pedido-total {
  text-align: right;
  font-size: 1.3rem;
  font-weight: 700;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 2px solid var(--color-border);
  color: var(--color-primary);
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 3rem;
  border: 2px dashed var(--color-border);
  border-radius: 8px;
  background: var(--color-bg);
  color: var(--color-text);
}

.error-state {
  border-color: var(--color-error);
  background: rgba(255, 107, 107, 0.05);
}

.error-state p {
  color: var(--color-error);
  margin-bottom: 1rem;
}

.error-state button {
  padding: 0.75rem 1.5rem;
  background: var(--color-error);
  border: none;
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.error-state button:hover {
  background: #e74c3c;
  transform: translateY(-2px);
}

.empty-state p {
  color: var(--color-text-secondary);
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .mis-pedidos-container {
    padding: 1.5rem;
    margin: 1rem;
  }

  .header {
    flex-direction: column;
    gap: 1rem;
  }

  .pedido-item {
    flex-direction: column;
    text-align: center;
  }
}
</style>
