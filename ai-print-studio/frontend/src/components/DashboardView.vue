<template>
  <div class="dashboard-view">

    <!-- HEADER -->
    <div class="view-header">
      <h1 class="view-title">📊 Dashboard</h1>
      <p class="view-description">Resumen general del negocio</p>
    </div>

    <!-- LOADING -->
    <div v-if="cargando" class="loading-message">
      ⏳ Cargando datos...
    </div>

    <!-- ERROR -->
    <div v-if="error" class="error-message">
      ❌ {{ error }}
      <button @click="() => cargarDatos(1)" class="btn-retry">Reintentar</button>
    </div>

    <!-- CONTENIDO -->
    <template v-if="!cargando && !error">

      <!-- 🤖 CHAT AGENTE -->


      <!-- STATS -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div>
            <p class="stat-label">Total usuarios</p>
            <h3>{{ stats.total_usuarios || 0 }}</h3>
          </div>
        </div>

        <div
          class="stat-card"
          v-for="tipo in stats.usuarios_por_tipo || []"
          :key="tipo.tipo_usuario"
        >
          <div class="stat-icon">{{ getTipoIcon(tipo.tipo_usuario) }}</div>
          <div>
            <p class="stat-label">{{ getTipoLabel(tipo.tipo_usuario) }}</p>
            <h3>{{ tipo.total }}</h3>
          </div>
        </div>
      </div>

      <!-- ACTIVIDAD (más compacta) -->
      <div class="section small">
        <h2 class="section-title">📋 Actividad reciente</h2>

        <div v-if="actividad.length">
          <div v-for="item in actividad" :key="item.id_usuario" class="activity-item small">
            <span>{{ item.nombre }}</span>
            <small>{{ formatearTiempo(item.minutos_desde_registro) }}</small>
          </div>
        </div>

        <p v-else class="no-data">Sin actividad</p>
      </div>

      <!-- USUARIOS -->
      <div class="section">
        <h2 class="section-title">👥 Usuarios</h2>

        <table v-if="usuarios.length" class="users-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Email</th>
              <th>Tipo</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="u in usuarios" :key="u.id_usuario">
              <td>{{ u.id_usuario }}</td>
              <td>{{ u.nombre }}</td>
              <td>{{ u.email }}</td>
              <td>{{ u.tipo_usuario }}</td>
            </tr>
          </tbody>
        </table>

        <p v-else class="no-data">Sin usuarios</p>
      </div>

    </template>
  </div>
  

</template>

<script setup>
import { ref, onMounted } from 'vue'

// =====================
// STATE
// =====================
const cargando = ref(false)
const error = ref(null)
const stats = ref({})
const usuarios = ref([])
const actividad = ref([])


// =====================
// URLS
// =====================
const API_URL = 'http://localhost:8001/api/get-dashboard-stats.php'
const AGENTE_URL = 'http://localhost:5003/api/consultar'

// =====================
// DATA
// =====================
async function cargarDatos(pagina = 1) {
  if (typeof pagina !== 'number') pagina = 1

  cargando.value = true
  error.value = null

  try {
    const res = await fetch(`${API_URL}?page=${pagina}&limit=10`)
    const data = await res.json()

    if (!data.success) throw new Error(data.error)

    stats.value = data.stats || {}
    usuarios.value = data.usuarios || []
    actividad.value = data.actividad || []

  } catch (e) {
    error.value = e.message
  } finally {
    cargando.value = false
  }
}

// =====================
// HELPERS
// =====================
function getTipoIcon(tipo) {
  return {
    ADMIN: '👨‍💼',
    CLIENTE: '👤'
  }[tipo] || '👤'
}

function getTipoLabel(tipo) {
  return tipo
}

function formatearTiempo(min) {
  if (min < 60) return `${min} min`
  return `${Math.floor(min / 60)}h`
}

// =====================
// INIT
// =====================
onMounted(() => {
  cargarDatos(1)
})
</script>

<style scoped>
.dashboard-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section {
  background: #1e293b;
  padding: 16px;
  border-radius: 10px;
}

.section.small {
  padding: 10px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 10px;
}

.stat-card {
  background: #0f172a;
  padding: 12px;
  border-radius: 8px;
  display: flex;
  gap: 10px;
}

.activity-item.small {
  font-size: 0.8rem;
  display: flex;
  justify-content: space-between;
}

.users-table {
  width: 100%;
  font-size: 0.85rem;
}

.chat-box {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chat-messages {
  max-height: 150px;
  overflow-y: auto;
}

.msg {
  padding: 6px;
  border-radius: 6px;
}

.msg.user {
  background: #0ea5e9;
  text-align: right;
}

.msg.bot {
  background: #334155;
}

.chat-input {
  display: flex;
  gap: 6px;
}

.chat-input input {
  flex: 1;
  padding: 6px;
}
</style>