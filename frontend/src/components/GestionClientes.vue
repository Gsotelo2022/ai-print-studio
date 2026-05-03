<template>
  <div class="gestion-clientes">
    <div class="view-header">
      <div class="header-info">
        <h1 class="view-title">👥 Gestión de clientes</h1>
        <p class="view-description">Administra la base de datos de clientes</p>
      </div>
      <div class="header-actions">
        <div class="search-container">
          <input type="text" v-model="terminoBusqueda" placeholder="Buscar cliente..." class="search-input">
          <span class="search-icon">🔍</span>
        </div>
        <button class="btn-exportar" @click="exportarCSV">
          <span>⬇️</span>
          <span>Exportar CSV</span>
        </button>
        <button @click="cargarClientes" class="btn-recarga">
          <span>🔄</span>
          <span>Recargar</span>
        </button>
      </div>
    </div>

    <!-- Mensaje de carga -->
    <div v-if="cargando" class="mensaje-estado">
      <div class="spinner"></div>
      <p>Cargando clientes...</p>
    </div>

    <!-- Mensaje de error -->
    <div v-else-if="error" class="mensaje-estado error">
      <p>⚠️ {{ error }}</p>
      <button @click="cargarClientes" class="btn-reintentar">Reintentar</button>
    </div>

    <!-- Tabla de clientes -->
    <div v-else class="tabla-container">
      <!-- Mensaje si no hay clientes -->
      <div v-if="clientesFiltrados.length === 0" class="mensaje-vacio">
        <p>📭 No se encontraron clientes</p>
        <p class="texto-secundario">Intenta con otro término de búsqueda o registra un nuevo cliente.</p>
      </div>

      <table v-else class="tabla-clientes">
        <thead>
          <tr>
            <th>Cliente</th>
            <th>Email</th>
            <th>Teléfono</th>
            <th>Pedidos</th>
            <th>
              Total gastado
              <button
                @click="mostrarTotal = !mostrarTotal"
                :title="mostrarTotal ? 'Ocultar totales' : 'Mostrar totales'"
                style="background:none;border:none;cursor:pointer;color:var(--color-text-secondary);margin-left:4px;"
              >{{ mostrarTotal ? '👁️' : '🙈' }}</button>
            </th>

            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cliente in clientesFiltrados" :key="cliente.id">
            <td>
              <div class="cliente-info">
                <div class="cliente-avatar" :style="{ background: cliente.color }">
                  {{ cliente.iniciales }}
                </div>
                <span class="cliente-nombre">{{ cliente.nombre }}</span>
              </div>
            </td>
            <td>{{ cliente.email }}</td>
            <td>{{ cliente.telefono }}</td>
            <td>
              <span class="badge-numero">{{ cliente.pedidos }}</span>
            </td>
            <td>
              <span v-if="mostrarTotal" class="cliente-total">{{ formatearMoneda(cliente.totalGastado) }}</span>
              <span v-else class="cliente-total" style="filter: blur(4px); user-select: none;">••••••</span>
            </td>
            <td>
              <div class="acciones">
                <button @click="abrirModalEdicion(cliente)" class="btn-accion" title="Editar">✏️</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <EditClienteModal
      :visible="modalVisible"
      :cliente="clienteSeleccionado"
      @cerrar="cerrarModalEdicion"
      @guardar="guardarCambiosCliente"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import EditClienteModal from './EditClienteModal.vue'
import { useApi } from '../composables/useApi.js'
import { useToast } from '../composables/useToast.js'

const { success, error: toastError } = useToast()

const { get, put } = useApi()

const clientes = ref([])
const cargando = ref(false)
const error = ref(null)
const modalVisible = ref(false)
const clienteSeleccionado = ref(null)
const terminoBusqueda = ref('')

const clientesFiltrados = computed(() => {
  if (!terminoBusqueda.value) {
    return clientes.value
  }
  const busqueda = terminoBusqueda.value.toLowerCase()
  return clientes.value.filter(cliente => {
    return cliente.nombre.toLowerCase().includes(busqueda) ||
           cliente.email.toLowerCase().includes(busqueda)
  })
})

const abrirModalEdicion = (cliente) => {
  clienteSeleccionado.value = { ...cliente }
  modalVisible.value = true
}

const cerrarModalEdicion = () => {
  modalVisible.value = false
  clienteSeleccionado.value = null
}

const guardarCambiosCliente = async (clienteEditado) => {
  console.log('Guardando cambios para:', clienteEditado)
  
  try {
    const datosActualizacion = {
      nombre: clienteEditado.nombre,
      email: clienteEditado.email,
      telefono: clienteEditado.telefono || null,
      tipo: clienteEditado.tipo,
      cuenta_bloqueada: clienteEditado.cuenta_bloqueada
    }

    await put(`/admin/clientes/${clienteEditado.id}`, datosActualizacion)

    await cargarClientes()
    success('Cliente actualizado correctamente')

  } catch (err) {
    console.error('❌ Error al guardar cambios:', err)
    toastError('Error al actualizar el cliente: ' + (err.message || ''))
  }

  cerrarModalEdicion()
}

// Cargar clientes al montar el componente
onMounted(async () => {
  await cargarClientes()
})

async function cargarClientes() {
  cargando.value = true
  error.value = null
  
  try {
    console.log('🔄 Cargando clientes desde la base de datos...')
    const data = await get('/admin/clientes')
    clientes.value = Array.isArray(data) ? data : (data?.clientes || [])
    console.log('✅ Clientes cargados:', clientes.value.length)
    
  } catch (err) {
    console.error('❌ Error al cargar clientes:', err)
    error.value = err.message || 'Error al cargar clientes'
  } finally {
    cargando.value = false
  }
}

const formatearMoneda = (valor) => {
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
    minimumFractionDigits: 0
  }).format(valor)
}
/*Exportacion*/ 
function exportarCSV() {
  if (!clientes.value.length) return

  const headers = ['ID', 'Nombre', 'Email', 'Telefono', 'Pedidos', 'Total Gastado']
  const rows = clientes.value.map(c => [
    c.id,
    `"${(c.nombre || '').replace(/"/g, '""')}"`,
    `"${(c.email || '').replace(/"/g, '""')}"`,
    `"${(c.telefono || '').replace(/"/g, '""')}"`,
    c.pedidos || 0,
    c.totalGastado || 0
  ])

  const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `clientes_${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

const mostrarTotal = ref(true)

</script>

<style scoped>
.gestion-clientes {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
}

.header-info {
  flex: 1;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-container {
  position: relative;
}

.search-input {
  padding: 10px 16px 10px 40px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
  width: 250px;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.2);
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-secondary);
  font-size: 1.1rem;
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

.btn-exportar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.btn-exportar:hover {
  background: rgba(6, 182, 212, 0.1);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.btn-recarga {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.btn-recarga:hover {
  background: rgba(6, 182, 212, 0.1);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.tabla-container {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  overflow-x: auto; /* Permite scroll horizontal si es necesario */
  max-height: 60vh; /* Altura máxima antes de mostrar scroll vertical */
  overflow-y: auto; /* Muestra scroll vertical cuando el contenido excede la altura máxima */
}

.tabla-clientes {
  width: 100%;
  border-collapse: collapse;
}

.tabla-clientes thead {
  background: rgba(6, 182, 212, 0.05);
}

.tabla-clientes th {
  text-align: left;
  padding: 8px 10px; /* Reducido */
  font-size: 0.7rem; /* Reducido */
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--color-border);
}

.tabla-clientes td {
  padding: 8px 10px; /* Reducido */
  border-bottom: 1px solid var(--color-border);
  font-size: 0.8rem; /* Reducido */
}

.tabla-clientes tbody tr:last-child td {
  border-bottom: none;
}

.tabla-clientes tbody tr:hover {
  background: rgba(6, 182, 212, 0.03);
}

.cliente-info {
  display: flex;
  align-items: center;
  gap: 8px; /* Reducido */
}

.cliente-avatar {
  width: 28px; /* Reducido */
  height: 28px; /* Reducido */
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 500; /* Reducido */
  font-size: 0.7rem; /* Reducido */
  flex-shrink: 0;
}

.cliente-nombre {
  font-weight: 500;
  color: var(--color-text);
  font-size: 0.85rem; /* Reducido */
}

.badge-numero {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px; /* Reducido */
  height: 18px; /* Reducido */
  padding: 0 6px;
  background: rgba(6, 182, 212, 0.15);
  color: var(--color-primary);
  border-radius: 9px; /* Reducido */
  font-size: 0.7rem; /* Reducido */
  font-weight: 600;
}

.cliente-total {
  font-weight: 600;
  color: var(--color-text);
  font-size: 0.85rem; /* Reducido */
}

.acciones {
  display: flex;
  gap: 4px; /* Reducido */
}

.btn-accion {
  width: 24px; /* Reducido */
  height: 24px; /* Reducido */
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.8rem; /* Reducido */
}

.btn-accion:hover {
  background: rgba(6, 182, 212, 0.1);
  border-color: var(--color-primary);
}
</style>

/* Estados de carga y error */
.mensaje-estado {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  gap: 16px;
}

.mensaje-estado.error {
  border-color: #ef4444;
}

.mensaje-estado p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.btn-reintentar {
  padding: 10px 24px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn-reintentar:hover {
  background: #0891b2;
  transform: translateY(-1px);
}

.mensaje-vacio {
  text-align: center;
  padding: 60px 20px;
}

.mensaje-vacio p {
  margin: 0;
  font-size: 1.1rem;
  color: var(--color-text);
}

.mensaje-vacio .texto-secundario {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  margin-top: 8px;
}
