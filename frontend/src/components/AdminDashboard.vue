<template>
  <div class="admin-layout" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
    <!-- Sidebar -->
    <aside class="admin-sidebar">
      <div class="sidebar-header">
        <div class="logo-container" v-if="isSidebarCollapsed">
          <img src="../assets/logo-prendete-rock.jpg" alt="Logo" class="sidebar-logo">
        </div>
        <template v-else>
          <div class="logo-container-expanded">
            <img src="../assets/logo-prendete-rock.jpg" alt="Logo" class="sidebar-logo-expanded">
          </div>
          <h2 class="sidebar-title">PRENDETE ROCK</h2>
          <p class="sidebar-subtitle">Panel de Administración</p>
        </template>
      </div>

      <nav class="sidebar-nav">
        <a 
          href="#" 
          @click.prevent="currentView = 'dashboard'"
          :class="['sidebar-link', { active: currentView === 'dashboard' }]"
        >
          <span class="icon">📊</span>
          <span v-if="!isSidebarCollapsed">Dashboard</span>
        </a>
        <a 
          href="#" 
          @click.prevent="currentView = 'pedidos'"
          :class="['sidebar-link', { active: currentView === 'pedidos' }]"
        >
          <span class="icon">📦</span>
          <span v-if="!isSidebarCollapsed">Pedidos</span>
        </a>
        <a 
          href="#" 
          @click.prevent="currentView = 'productos'"
          :class="['sidebar-link', { active: currentView === 'productos' }]"
        >
          <span class="icon">👕</span>
          <span v-if="!isSidebarCollapsed">Productos</span>
        </a>
        <a 
          href="#" 
          @click.prevent="currentView = 'clientes'"
          :class="['sidebar-link', { active: currentView === 'clientes' }]"
        >
          <span class="icon">👥</span>
          <span v-if="!isSidebarCollapsed">Clientes</span>
        </a>
        <a 
          href="#" 
          @click.prevent="currentView = 'cupones'"
          :class="['sidebar-link', { active: currentView === 'cupones' }]"
        >
          <span class="icon">🎟️</span>
          <span v-if="!isSidebarCollapsed">Cupones</span>
        </a>
        <a 
          href="#" 
          @click.prevent="currentView = 'configuracion'"
          :class="['sidebar-link', { active: currentView === 'configuracion' }]"
        >
          <span class="icon">⚙️</span>
          <span v-if="!isSidebarCollapsed">Configuración</span>
        </a>
      </nav>

      <button @click="toggleSidebar" class="sidebar-toggle-btn">
        <span class="icon">{{ isSidebarCollapsed ? '▶' : '◀' }}</span>
      </button>

      <div class="sidebar-footer">
        <a href="#" @click.prevent="handleLogout" class="sidebar-link logout">
          <span class="icon">🚪</span>
          <span v-if="!isSidebarCollapsed">Cerrar sesión</span>
        </a>
      </div>
    </aside>

    <!-- Contenido principal -->
    <main class="admin-content">
      <!-- Header con info del usuario -->
      <header class="admin-header">
        <div class="admin-user-info">
          <div class="user-avatar">
            <span>{{ userInitials }}</span>
          </div>
          <div class="user-details">
            <p class="user-name">Admin Usuario</p>
            <p class="user-email">{{ userEmail }}</p>
          </div>
        </div>
      </header>

      <!-- Vistas dinámicas -->
      <div class="admin-view">
        <GestionCupones
          v-if="currentView === 'cupones'"
          :propuestas-externas="propuestasIA"
          :analisis-externo="analisisIA"
          :cargando-i-a-externo="cargandoIA"
        />
        <component v-else :is="currentViewComponent" />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import GestionPedidos from './GestionPedidos.vue'
import DashboardView from './DashboardView.vue'
import GestionProductos from './GestionProductos.vue'
import GestionClientes from './GestionClientes.vue'
import GestionCupones from './GestionCupones.vue'
import ConfiguracionView from './ConfiguracionView.vue'

const emit = defineEmits(['logout'])

// Estado
const isSidebarCollapsed = ref(true)
const currentView = ref('pedidos')
const userEmail = ref(localStorage.getItem('userEmail') || 'admin@prendeterock.com')

// Estado agente IA cupones
const propuestasIA = ref([])
const analisisIA = ref('')
const cargandoIA = ref(false)

// Computed
const userInitials = computed(() => {
  const email = userEmail.value
  if (!email) return 'AU'
  const name = email.split('@')[0]
  return name.substring(0, 2).toUpperCase()
})

const currentViewComponent = computed(() => {
  const views = {
    dashboard: DashboardView,
    pedidos: GestionPedidos,
    productos: GestionProductos,
    clientes: GestionClientes,
    configuracion: ConfiguracionView
  }
  return views[currentView.value]
})

// Métodos
const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const handleLogout = () => {
  emit('logout')
}

const iniciarAgenteIA = async () => {
  cargandoIA.value = true
  propuestasIA.value = []
  analisisIA.value = ''
  try {
    const response = await fetch('http://localhost:5003/api/cupones/proponer', {
      method: 'POST'
    })
    const data = await response.json()
    if (data.success && data.propuesta) {
      propuestasIA.value = data.propuesta.cupones || []
      analisisIA.value = data.propuesta.analisis || ''
    }
  } catch (error) {
    console.warn('[IA Cupones] Agente no disponible:', error.message)
  } finally {
    cargandoIA.value = false
  }
}

onMounted(() => {
  iniciarAgenteIA()
})
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: var(--color-bg);
  transition: padding-left 0.3s ease;
}

.admin-layout.sidebar-collapsed {
  padding-left: 62px;
}

/* SIDEBAR */
.admin-sidebar {
  width: 229px;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 100;
  transition: width 0.3s ease;
}

.admin-layout.sidebar-collapsed .admin-sidebar {
  width: 62px;
}

.sidebar-header {
  padding: 21px;
  border-bottom: 1px solid var(--color-border);
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 11px;
}

.admin-layout.sidebar-collapsed .sidebar-header {
  padding: 18px 11px;
}

.logo-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.sidebar-logo {
  width: 40px;
  height: 40px;
  border-radius: 7px;
  object-fit: cover;
}

.logo-container-expanded {
  display: flex;
  justify-content: center;
  margin-bottom: 7px;
}

.sidebar-logo-expanded {
  width: 88px;
  height: 88px;
  border-radius: 11px;
  object-fit: cover;
}

.sidebar-title {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 1.32rem;
  letter-spacing: 1.8px;
  color: var(--color-primary);
  margin: 0;
  transition: all 0.2s;
}

.admin-layout.sidebar-collapsed .sidebar-title {
  font-size: 1.1rem;
}

.sidebar-subtitle {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  margin: 3px 0 0 0;
}

.sidebar-toggle-btn {
  position: absolute;
  bottom: 70px;
  right: -13px;
  width: 26px;
  height: 26px;
  background: var(--color-primary);
  color: white;
  border: 2px solid var(--color-surface);
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 101;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.sidebar-toggle-btn:hover {
  transform: scale(1.15);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.admin-layout.sidebar-collapsed .sidebar-toggle-btn {
  right: -15px;
}

.sidebar-toggle-btn .icon {
  font-size: 0.79rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar-nav {
  flex: 1;
  padding: 14px 0;
  overflow-y: auto;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 9px 18px;
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: all 0.2s;
  border-left: 2px solid transparent;
  overflow: hidden;
  white-space: nowrap;
  font-size: 0.79rem;
}

.admin-layout.sidebar-collapsed .sidebar-link {
  justify-content: center;
  padding: 9px 0;
}

.sidebar-link:hover {
  background: rgba(6, 182, 212, 0.1);
  color: var(--color-text);
}

.sidebar-link.active {
  background: rgba(6, 182, 212, 0.15);
  color: var(--color-primary);
  border-left-color: var(--color-primary);
}

.admin-layout.sidebar-collapsed .sidebar-link.active {
  border-left-width: 0;
  border-right: 2px solid var(--color-primary);
}

.sidebar-link .icon {
  font-size: 1.01rem;
  width: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sidebar-footer {
  padding: 0;
  border-top: 1px solid var(--color-border);
}

.sidebar-link.logout {
  border-top: none;
  padding: 9px 18px;
}

.admin-layout.sidebar-collapsed .sidebar-link.logout {
  justify-content: center;
  padding: 9px 0;
}

/* MAIN CONTENT */
.admin-content {
  flex: 1;
  padding: 0;
  margin-left: 229px;
  transition: margin-left 0.3s ease;
}

.admin-layout.sidebar-collapsed .admin-content {
  margin-left: 62px;
}

.admin-header {
  padding: 21px 29px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 50;
}

.admin-user-info {
  display: flex;
  align-items: center;
  gap: 11px;
}

.user-avatar {
  width: 35px;
  height: 35px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.79rem;
}

.user-details {
  text-align: right;
}

.user-name {
  font-weight: 600;
  margin: 0;
  font-size: 1rem;
}

.user-email {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  margin: 0;
}

.admin-view {
  flex: 1;
  padding: 29px;
}

/* Responsive */
@media (max-width: 768px) {
  .admin-sidebar {
    width: 176px;
  }

  .admin-content {
    margin-left: 176px;
  }

  .sidebar-header {
    padding: 18px 14px;
  }

  .sidebar-link {
    padding: 9px 14px;
    font-size: 0.79rem;
  }

  .admin-view {
    padding: 18px;
  }
}
</style>
