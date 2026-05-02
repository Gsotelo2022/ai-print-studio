<template>
  <div class="mis-pedidos-container">
    <div class="header">
      <h2 class="title">Mis Pedidos</h2>
      <button @click="$emit('go-back')" class="btn-secondary">Volver</button>
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
      <button @click="$emit('go-back')" class="btn-primary">Crear mi primer diseño</button>
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
              <img :src="item.ruta_thumbnail" alt="thumbnail" class="item-thumbnail" @error="onImageError"/>
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
import { ref, onMounted } from 'vue';
import { useApi } from '../composables/useApi.js';

const props = defineProps({
  userId: {
    type: Number,
    required: true
  }
});

const emit = defineEmits(['go-back']);

const pedidos = ref([]);
const { getMisPedidos, loading: cargando, error } = useApi();


async function cargarPedidos() {
  if (!props.userId) return;
  try {
    pedidos.value = await getMisPedidos(props.userId);
  } catch (err) {
    // el error ya queda en `error` del composable
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
.mis-pedidos-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 1rem;
}

.title {
  font-size: 2rem;
  color: #333;
}

.pedidos-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.pedido-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  transition: box-shadow 0.3s ease;
}

.pedido-card:hover {
  box-shadow: 0 6px 12px rgba(0,0,0,0.1);
}

.pedido-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f7f7f7;
  padding: 0.75rem 1rem;
  font-size: 0.9rem;
}

.pedido-fecha {
  color: #555;
}

.pedido-estado {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-weight: bold;
  color: #fff;
  text-transform: capitalize;
}

.estado-pendiente { background-color: #f0ad4e; }
.estado-en-proceso { background-color: #337ab7; }
.estado-completado { background-color: #5cb85c; }
.estado-enviado { background-color: #5bc0de; }
.estado-cancelado { background-color: #d9534f; }


.pedido-body {
  padding: 1rem;
}

.pedido-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.item-thumbnail {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #eee;
}

.item-info p {
  margin: 0;
}

.item-producto {
  font-weight: bold;
}

.item-cantidad {
  color: #777;
  font-size: 0.9rem;
}

.pedido-total {
  text-align: right;
  font-size: 1.2rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.loading-state, .error-state, .empty-state {
  text-align: center;
  padding: 3rem;
  border: 2px dashed #ddd;
  border-radius: 8px;
}
</style>
