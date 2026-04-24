<template>
  <div class="dashboard-view">
    <div class="view-header">
      <h1 class="view-title">📊 Dashboard</h1>
      <p class="view-description">Resumen general del negocio</p>
    </div>

    <!-- Mensaje de carga -->
    <div v-if="cargando" class="loading-message">
      <p>⏳ Cargando datos...</p>
    </div>

    <!-- Mensaje de error -->
    <div v-if="error" class="error-message">
      <p>❌ {{ error }}</p>
      <button @click="cargarDatos" class="btn-retry">Reintentar</button>
    </div>

    <!-- Contenido del dashboard -->
    <template v-if="!cargando && !error">
      <!-- Tarjetas de estadísticas -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-content">
            <p class="stat-label">Total de usuarios</p>
            <h3 class="stat-value">{{ stats.total_usuarios || 0 }}</h3>
            <p class="stat-change" :class="{ positive: stats.usuarios_semana > 0 }">
              +{{ stats.usuarios_semana || 0 }} esta semana
            </p>
          </div>
        </div>

        <div class="stat-card" v-for="tipo in stats.usuarios_por_tipo" :key="tipo.tipo_usuario">
          <div class="stat-icon">{{ getTipoIcon(tipo.tipo_usuario) }}</div>
          <div class="stat-content">
            <p class="stat-label">{{ getTipoLabel(tipo.tipo_usuario) }}</p>
            <h3 class="stat-value">{{ tipo.total }}</h3>
            <p class="stat-change">Tipo: {{ tipo.tipo_usuario }}</p>
          </div>
        </div>
      </div>

      <!-- Actividad reciente -->
      <div class="section">
        <h2 class="section-title">📋 Actividad reciente</h2>
        <div class="activity-list" v-if="actividad.length > 0">
          <div class="activity-item" v-for="item in actividad" :key="item.id_usuario">
            <div class="activity-icon">{{ item.tipo_usuario === 'ADMIN' ? '👨‍💼' : '👤' }}</div>
            <div class="activity-content">
              <p class="activity-text">
                <strong>Nuevo {{ item.tipo_usuario.toLowerCase() }}:</strong> 
                {{ item.nombre }} {{ item.apellido }}
              </p>
              <p class="activity-time">{{ formatearTiempo(item.minutos_desde_registro) }}</p>
            </div>
          </div>
        </div>
        <p v-else class="no-data">No hay actividad reciente</p>
      </div>

      <!-- Lista de usuarios con paginación -->
      <div class="section">
        <h2 class="section-title">👥 Usuarios registrados</h2>
        
        <div class="table-container">
          <table class="users-table" v-if="usuarios.length > 0">
            <thead>
              <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Email</th>
                <th>Tipo</th>
                <th>Fecha de registro</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="usuario in usuarios" :key="usuario.id_usuario">
                <td>{{ usuario.id_usuario }}</td>
                <td>{{ usuario.nombre }} {{ usuario.apellido }}</td>
                <td>{{ usuario.email }}</td>
                <td>
                  <span class="badge" :class="'badge-' + usuario.tipo_usuario.toLowerCase()">
                    {{ usuario.tipo_usuario }}
                  </span>
                </td>
                <td>{{ formatearFecha(usuario.fecha_registro) }}</td>
              </tr>
            </tbody>
          </table>
          <p v-else class="no-data">No hay usuarios registrados</p>
        </div>

        <!-- Paginación -->
        <div class="pagination" v-if="paginacion.total_paginas > 1">
          <button 
            @click="cambiarPagina(paginacion.pagina_actual - 1)" 
            :disabled="paginacion.pagina_actual === 1"
            class="btn-pagination"
          >
            ← Anterior
          </button>
          
          <div class="pagination-info">
            <span>Página {{ paginacion.pagina_actual }} de {{ paginacion.total_paginas }}</span>
            <span class="total-records">({{ paginacion.total_registros }} registros)</span>
          </div>
          
          <button 
            @click="cambiarPagina(paginacion.pagina_actual + 1)" 
            :disabled="paginacion.pagina_actual === paginacion.total_paginas"
            class="btn-pagination"
          >
            Siguiente →
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const cargando = ref(false);
const error = ref(null);
const stats = ref({});
const usuarios = ref([]);
const actividad = ref([]);
const paginacion = ref({
  pagina_actual: 1,
  total_paginas: 1,
  total_registros: 0,
  registros_por_pagina: 10
});

const API_URL = 'http://localhost:8080/api/get-dashboard-stats.php';

async function cargarDatos(pagina = 1) {
  cargando.value = true;
  error.value = null;
  
  try {
    const response = await fetch(`${API_URL}?page=${pagina}&limit=10`);
    const data = await response.json();
    
    if (data.success) {
      stats.value = data.stats;
      usuarios.value = data.usuarios;
      actividad.value = data.actividad;
      paginacion.value = data.paginacion;
    } else {
      error.value = data.error || 'Error al cargar los datos';
    }
  } catch (err) {
    error.value = 'Error de conexión: ' + err.message;
  } finally {
    cargando.value = false;
  }
}

function cambiarPagina(nuevaPagina) {
  if (nuevaPagina >= 1 && nuevaPagina <= paginacion.value.total_paginas) {
    cargarDatos(nuevaPagina);
  }
}

function getTipoIcon(tipo) {
  const icons = {
    'ADMIN': '👨‍💼',
    'CLIENTE': '👤',
    'USUARIO': '👥',
    'VENDEDOR': '🛒'
  };
  return icons[tipo.toUpperCase()] || '👤';
}

function getTipoLabel(tipo) {
  const labels = {
    'ADMIN': 'Administradores',
    'CLIENTE': 'Clientes',
    'USUARIO': 'Usuarios',
    'VENDEDOR': 'Vendedores'
  };
  return labels[tipo.toUpperCase()] || tipo;
}

function formatearFecha(fechaStr) {
  if (!fechaStr) return '-';
  const fecha = new Date(fechaStr);
  return fecha.toLocaleDateString('es-AR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function formatearTiempo(minutos) {
  if (minutos < 1) return 'Hace menos de un minuto';
  if (minutos < 60) return `Hace ${minutos} minuto${minutos > 1 ? 's' : ''}`;
  const horas = Math.floor(minutos / 60);
  if (horas < 24) return `Hace ${horas} hora${horas > 1 ? 's' : ''}`;
  const dias = Math.floor(horas / 24);
  return `Hace ${dias} día${dias > 1 ? 's' : ''}`;
}

onMounted(() => {
  cargarDatos();
});
</script>

<style scoped>
.dashboard-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.view-header {
  margin-bottom: 4px;
}

.view-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 4px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.view-description {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  margin: 0;
}

/* MENSAJES */
.loading-message, .error-message {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 16px;
  text-align: center;
}

.loading-message p {
  font-size: 1rem;
  color: var(--color-text-secondary);
  margin: 0;
}

.error-message p {
  font-size: 1rem;
  color: var(--color-danger);
  margin: 0 0 12px 0;
}

.btn-retry {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-retry:hover {
  background: var(--color-primary-dark);
}

.no-data {
  text-align: center;
  color: var(--color-text-secondary);
  padding: 12px;
  font-style: italic;
  font-size: 0.85rem;
}

/* STATS GRID */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.stat-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 14px 16px;
  display: flex;
  gap: 12px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.stat-icon {
  font-size: 1.8rem;
  line-height: 1;
}

.stat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
}

.stat-change {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  margin: 0;
}

.stat-change.positive {
  color: var(--color-success);
}

/* SECCIÓN */
.section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 16px;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* ACTIVIDAD */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.activity-item {
  display: flex;
  gap: 10px;
  padding: 8px 12px;
  background: rgba(6, 182, 212, 0.05);
  border-radius: var(--radius-sm);
  transition: background 0.2s;
}

.activity-item:hover {
  background: rgba(6, 182, 212, 0.1);
}

.activity-icon {
  font-size: 1.2rem;
  line-height: 1;
}

.activity-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.activity-text {
  font-size: 0.85rem;
  color: var(--color-text);
  margin: 0;
}

.activity-time {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  margin: 0;
}

/* TABLA */
.table-container {
  overflow-x: auto;
  margin-bottom: 12px;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.users-table thead {
  background: rgba(6, 182, 212, 0.1);
}

.users-table th {
  text-align: left;
  padding: 8px 10px;
  font-weight: 600;
  color: var(--color-text);
  border-bottom: 2px solid var(--color-border);
  font-size: 0.8rem;
}

.users-table td {
  padding: 8px 10px;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text);
}

.users-table tbody tr:hover {
  background: rgba(6, 182, 212, 0.05);
}

.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
}

.badge-admin {
  background: rgba(220, 38, 38, 0.1);
  color: rgb(220, 38, 38);
}

.badge-cliente {
  background: rgba(6, 182, 212, 0.1);
  color: rgb(6, 182, 212);
}

.badge-usuario {
  background: rgba(34, 197, 94, 0.1);
  color: rgb(34, 197, 94);
}

.badge-vendedor {
  background: rgba(251, 146, 60, 0.1);
  color: rgb(251, 146, 60);
}

/* PAGINACIÓN */
.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border);
}

.btn-pagination {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.2s, opacity 0.2s;
}

.btn-pagination:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.btn-pagination:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  font-size: 0.85rem;
  color: var(--color-text);
}

.total-records {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

@media (max-width: 768px) {
  .pagination {
    flex-direction: column;
  }
  
  .table-container {
    font-size: 0.8rem;
  }
  
  .users-table th,
  .users-table td {
    padding: 6px 8px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
