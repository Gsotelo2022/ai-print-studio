<template>
  <div class="gestion-pedidos">
    <!-- Header -->
    <div class="view-header">
      <div class="header-info">
        <h1 class="view-title">📋 Gestión de pedidos</h1>
        <p class="view-description">Visualiza y administra todos los pedidos realizados</p>
      </div>
      <button class="btn-exportar">
        <span>⬇️</span>
        <span>Exportar</span>
      </button>
    </div>

    <!-- Filtros por estado -->
    <div class="filtros-tabs">
      <button 
        @click="filtroActivo = 'todos'"
        :class="['tab-btn', { active: filtroActivo === 'todos' }]"
      >
        Todos ({{ totalPedidos }})
      </button>
      <button 
        @click="filtroActivo = 'pendientes'"
        :class="['tab-btn', { active: filtroActivo === 'pendientes' }]"
      >
        Pendientes ({{ pedidosPendientes.length }})
      </button>
      <button 
        @click="filtroActivo = 'pagados'"
        :class="['tab-btn', { active: filtroActivo === 'pagados' }]"
      >
        Pagados ({{ pedidosPagados.length }})
      </button>
      <button 
        @click="filtroActivo = 'no-pagados'"
        :class="['tab-btn', { active: filtroActivo === 'no-pagados' }]"
      >
        No pagados ({{ pedidosNoPagados.length }})
      </button>
      <button 
        @click="filtroActivo = 'entregados'"
        :class="['tab-btn', { active: filtroActivo === 'entregados' }]"
      >
        Entregados ({{ pedidosEntregados.length }})
      </button>
    </div>

    <!-- Tabla de pedidos -->
    <div class="tabla-container">
      <!-- Mensaje de carga -->
      <div v-if="cargando" class="mensaje-estado">
        <div class="spinner"></div>
        <p>Cargando pedidos...</p>
      </div>

      <!-- Mensaje de error -->
      <div v-else-if="error" class="mensaje-estado error">
        <p>⚠️ {{ error }}</p>
        <button @click="cargarPedidos" class="btn-reintentar">Reintentar</button>
      </div>

      <!-- Tabla con datos -->
      <table v-else class="tabla-pedidos">
        <thead>
          <tr>
            <th>N° Pedido</th>
            <th>Cliente</th>
            <th>Producto</th>
            <th>Fecha</th>
            <th>Estado</th>
            <th>Pago</th>
            <th>Total</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="pedido in pedidosFiltrados" :key="pedido.id">
            <!-- N° Pedido -->
            <td>
              <span class="pedido-numero">{{ pedido.numero || 'N/A' }}</span>
            </td>

            <!-- Cliente -->
            <td>
              <div class="cliente-info">
                <div class="cliente-avatar" :style="{ background: pedido.cliente?.color || '#3b82f6' }">
                  {{ pedido.cliente?.iniciales || '?' }}
                </div>
                <div class="cliente-datos">
                  <p class="cliente-nombre">{{ pedido.cliente?.nombre || 'Sin nombre' }}</p>
                  <p class="cliente-telefono">{{ pedido.cliente?.telefono || 'Sin teléfono' }}</p>
                </div>
              </div>
            </td>

            <!-- Producto -->
            <td>
              <div class="producto-info">
                <div class="producto-imagen" v-if="pedido.imagen_diseno">
                  <img :src="'/' + pedido.imagen_diseno" alt="Diseño" class="diseno-thumb" />
                </div>
                <div class="producto-imagen" v-else>
                  <span>{{ pedido.producto?.emoji || '📦' }}</span>
                </div>
                <div class="producto-datos">
                  <p class="producto-nombre">{{ pedido.producto?.nombre || 'Sin producto' }}</p>
                  <p class="producto-detalles">{{ pedido.producto?.detalles || 'Sin detalles' }}</p>
                  <p class="producto-nota" v-if="pedido.notas_cliente">📝 {{ pedido.notas_cliente }}</p>
                </div>
              </div>
            </td>

            <!-- Fecha -->
            <td>
              <div class="fecha-info">
                <p class="fecha-dia">{{ pedido.fecha?.dia || '-' }}</p>
                <p class="fecha-hora">{{ pedido.fecha?.hora || '-' }}</p>
              </div>
            </td>

            <!-- Estado -->
            <td>
              <select 
                :class="['select-estado', 'estado-' + (pedido.estado?.tipo || 'pendiente')]"
                :value="pedido.estado?.tipo || 'pendiente'"
                @change="actualizarEstado(pedido, $event.target.value)"
              >
                <option value="pendiente">Pendiente</option>
                <option value="en-proceso">En proceso</option>
                <option value="completado">Completado</option>
                <option value="entregado">Entregado</option>
                <option value="cancelado">Cancelado</option>
              </select>
            </td>

            <!-- Pago -->
            <td>
              <select 
                :class="['select-pago', 'pago-' + (pedido.pago?.valor || pedido.pago?.tipo || 'pendiente')]"
                :value="pedido.pago?.valor || 'pendiente'"
                @change="actualizarPago(pedido, $event.target.value)"
              >
                <option value="pendiente">Pendiente</option>
                <option value="aprobado">Pagado</option>
                <option value="rechazado">Rechazado</option>
              </select>
            </td>

            <!-- Total -->
            <td>
              <span class="pedido-total">{{ formatearMoneda(pedido.total || 0) }}</span>
            </td>

            <!-- Acciones -->
            <td>
              <div class="acciones">
                <button class="btn-accion" @click="verDetalle(pedido)" title="Ver detalle">
                  👁️
                </button>
                <button class="btn-accion" @click="masOpciones(pedido)" title="Más opciones">
                  ⋮
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Mensaje si no hay pedidos -->
      <div v-if="pedidosFiltrados.length === 0" class="sin-resultados">
        <p>No hay pedidos en esta categoría</p>
      </div>
    </div>

    <!-- Paginación -->
    <div class="paginacion" v-if="totalPaginas > 1">
      <p class="paginacion-info">
        Mostrando {{ (paginaActual - 1) * itemsPorPagina + 1 }} a {{ Math.min(paginaActual * itemsPorPagina, pedidosFiltrados.length) }} de {{ pedidosFiltrados.length }} pedidos
      </p>
      <div class="paginacion-controles">
        <button 
          class="btn-pagina" 
          :disabled="paginaActual === 1"
          @click="cambiarPagina(paginaActual - 1)"
        >
          Anterior
        </button>
        
        <button 
          v-for="pagina in paginasVisibles" 
          :key="pagina"
          :class="['btn-pagina', { active: pagina === paginaActual }]"
          @click="cambiarPagina(pagina)"
        >
          {{ pagina }}
        </button>
        
        <button 
          class="btn-pagina"
          :disabled="paginaActual === totalPaginas"
          @click="cambiarPagina(paginaActual + 1)"
        >
          Siguiente
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useApi } from '../composables/useApi'

const { getAllOrders, updateOrderStatus, updateOrderPayment } = useApi()

// Estado
const filtroActivo = ref('todos')
const paginaActual = ref(1)
const itemsPorPagina = 5
const pedidos = ref([])
const cargando = ref(true)
const error = ref(null)

// Cargar pedidos al montar el componente
onMounted(async () => {
  await cargarPedidos()
})

async function cargarPedidos() {
  try {
    cargando.value = true
    error.value = null
    const data = await getAllOrders()
    
    console.log('📦 Datos recibidos del backend:', data)
    console.log('📦 Primer pedido (ejemplo):', data?.[0])
    
    // Asignar directamente sin filtrar
    pedidos.value = data || []
    
    console.log('✅ Pedidos cargados:', pedidos.value.length)
  } catch (err) {
    console.error('❌ Error al cargar pedidos:', err)
    error.value = 'Error al cargar los pedidos. ' + (err.message || '')
  } finally {
    cargando.value = false
  }
}

function getProductoEmoji(nombreProducto) {
  const nombre = nombreProducto.toLowerCase()
  if (nombre.includes('remera') || nombre.includes('camiseta')) return '👕'
  if (nombre.includes('buzo') || nombre.includes('sudadera')) return '🧥'
  if (nombre.includes('taza')) return '☕'
  if (nombre.includes('gorra')) return '🧢'
  if (nombre.includes('bolso') || nombre.includes('tote')) return '👜'
  return '📦'
}

// Computed
const totalPedidos = computed(() => pedidos.value.length)

const pedidosPendientes = computed(() => 
  pedidos.value.filter(p => p?.estado?.tipo === 'pendiente')
)

const pedidosEntregados = computed(() => 
  pedidos.value.filter(p => p?.estado?.tipo === 'entregado')
)

const pedidosPagados = computed(() => 
  pedidos.value.filter(p => p?.pago?.tipo === 'pagado')
)

const pedidosNoPagados = computed(() => 
  pedidos.value.filter(p => p?.pago?.tipo === 'no-pagado')
)

const pedidosPorFiltro = computed(() => {
  switch (filtroActivo.value) {
    case 'pendientes':
      return pedidosPendientes.value
    case 'entregados':
      return pedidosEntregados.value
    case 'pagados':
      return pedidosPagados.value
    case 'no-pagados':
      return pedidosNoPagados.value
    default:
      return pedidos.value
  }
})

// Total de páginas basado en el filtro activo
const totalPaginas = computed(() => 
  Math.ceil(pedidosPorFiltro.value.length / itemsPorPagina)
)

// Pedidos filtrados Y paginados
const pedidosFiltrados = computed(() => {
  const inicio = (paginaActual.value - 1) * itemsPorPagina
  const fin = inicio + itemsPorPagina
  return pedidosPorFiltro.value.slice(inicio, fin)
})

// Páginas visibles en la paginación (máximo 5 botones)
const paginasVisibles = computed(() => {
  const paginas = []
  const maxPaginas = totalPaginas.value
  
  if (maxPaginas <= 5) {
    for (let i = 1; i <= maxPaginas; i++) {
      paginas.push(i)
    }
  } else {
    if (paginaActual.value <= 3) {
      paginas.push(1, 2, 3, 4, 5)
    } else if (paginaActual.value >= maxPaginas - 2) {
      for (let i = maxPaginas - 4; i <= maxPaginas; i++) {
        paginas.push(i)
      }
    } else {
      for (let i = paginaActual.value - 2; i <= paginaActual.value + 2; i++) {
        paginas.push(i)
      }
    }
  }
  
  return paginas
})

// Métodos
function cambiarPagina(nuevaPagina) {
  if (nuevaPagina >= 1 && nuevaPagina <= totalPaginas.value) {
    paginaActual.value = nuevaPagina
  }
}

// Watch para resetear página cuando cambia el filtro
watch(filtroActivo, () => {
  paginaActual.value = 1
})

const formatearMoneda = (valor) => {
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
    minimumFractionDigits: 0
  }).format(valor)
}

async function actualizarEstado(pedido, nuevoEstado) {
  try {
    if (!pedido?.id) {
      throw new Error('Pedido inválido')
    }
    
    // Usar el id del pedido directamente
    const idPedido = pedido.id
    
    // Actualizar en el backend
    await updateOrderStatus(idPedido, nuevoEstado)
    
    // Actualizar localmente
    if (pedido.estado) {
      pedido.estado.tipo = nuevoEstado
      pedido.estado.texto = nuevoEstado.charAt(0).toUpperCase() + nuevoEstado.slice(1).replace('-', ' ')
    }
    
    console.log('✅ Estado actualizado:', nuevoEstado)
  } catch (err) {
    console.error('❌ Error al actualizar estado:', err)
    alert('Error al actualizar el estado: ' + err.message)
    // Recargar para restaurar el valor original
    await cargarPedidos()
  }
}

async function actualizarPago(pedido, nuevoPago) {
  try {
    if (!pedido?.id) {
      throw new Error('Pedido inválido')
    }
    
    // Usar el id del pedido directamente
    const idPedido = pedido.id
    
    // Actualizar en el backend
    await updateOrderPayment(idPedido, nuevoPago)
    
    // Actualizar localmente
    if (pedido.pago) {
      const tipoPago = nuevoPago === 'aprobado' ? 'pagado' : 'no-pagado'
      pedido.pago.tipo = tipoPago
      pedido.pago.valor = nuevoPago
      pedido.pago.texto = nuevoPago === 'aprobado' ? 'Pagado' : nuevoPago === 'rechazado' ? 'Rechazado' : 'Pendiente'
    }
    
    console.log('✅ Pago actualizado:', nuevoPago)
  } catch (err) {
    console.error('❌ Error al actualizar pago:', err)
    alert('Error al actualizar el pago: ' + err.message)
    // Recargar para restaurar el valor original
    await cargarPedidos()
  }
}

const verDetalle = (pedido) => {
  console.log('Ver detalle de pedido:', pedido)
  // Aquí se implementará el modal de detalle
}

const masOpciones = (pedido) => {
  console.log('Más opciones para pedido:', pedido)
  // Aquí se implementará el menú contextual
}
</script>

<style scoped>
.gestion-pedidos {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* HEADER */
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.header-info {
  flex: 1;
}

.view-title {
  font-size: 1.4rem;
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

.btn-exportar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.8rem;
}

.btn-exportar:hover {
  background: rgba(6, 182, 212, 0.1);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

/* FILTROS TABS */
.filtros-tabs {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 6px 14px;
  background: var(--color-surface);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.8rem;
}

.tab-btn:hover {
  background: rgba(6, 182, 212, 0.05);
  color: var(--color-text);
}

.tab-btn.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

/* TABLA */
.tabla-container {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  overflow: hidden;
}

.tabla-pedidos {
  width: 100%;
  border-collapse: collapse;
}

.tabla-pedidos thead {
  background: rgba(6, 182, 212, 0.05);
}

.tabla-pedidos th {
  text-align: left;
  padding: 8px 10px;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--color-border);
}

.tabla-pedidos td {
  padding: 8px 10px;
  border-bottom: 1px solid var(--color-border);
}

.tabla-pedidos tbody tr:last-child td {
  border-bottom: none;
}

.tabla-pedidos tbody tr:hover {
  background: rgba(6, 182, 212, 0.03);
}

/* Celdas específicas */
.pedido-numero {
  color: var(--color-primary);
  font-weight: 600;
  font-size: 0.85rem;
}

.cliente-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cliente-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 0.75rem;
  flex-shrink: 0;
}

.cliente-datos {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.cliente-nombre {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-text);
  margin: 0;
}

.cliente-telefono {
  font-size: 0.7rem;
  color: var(--color-text-secondary);
  margin: 0;
}

.producto-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.producto-imagen {
  width: 32px;
  height: 32px;
  background: rgba(6, 182, 212, 0.1);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.producto-datos {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.producto-nombre {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-text);
  margin: 0;
}

.producto-detalles {
  font-size: 0.7rem;
  color: var(--color-text-secondary);
  margin: 0;
}

.producto-nota {
  font-size: 0.7rem;
  color: var(--color-primary);
  margin: 2px 0 0;
  font-style: italic;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.diseno-thumb {
  width: 36px;
  height: 36px;
  object-fit: cover;
  border-radius: 6px;
}

.fecha-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.fecha-dia {
  font-size: 0.8rem;
  color: var(--color-text);
  margin: 0;
}

.fecha-hora {
  font-size: 0.7rem;
  color: var(--color-text-secondary);
  margin: 0;
}

/* SELECTORES DE ESTADO Y PAGO */
.select-estado,
.select-pago {
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 0.7rem;
  font-weight: 500;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
  appearance: none;
  background-repeat: no-repeat;
  background-position: right 6px center;
  background-size: 10px;
  padding-right: 22px;
}

.select-estado:hover,
.select-pago:hover {
  opacity: 0.8;
}

.select-estado:focus,
.select-pago:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 1px;
}

/* Flecha hacia abajo */
.select-estado {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='white' d='M2 4l4 4 4-4z'/%3E%3C/svg%3E");
}

.select-pago {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='white' d='M2 4l4 4 4-4z'/%3E%3C/svg%3E");
}

/* Estados */
.estado-pendiente {
  background: rgba(255, 193, 7, 0.15);
  color: #ffc107;
  border-color: rgba(255, 193, 7, 0.3);
}

.estado-en-proceso {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
  border-color: rgba(59, 130, 246, 0.3);
}

.estado-completado {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border-color: rgba(16, 185, 129, 0.3);
}

.estado-entregado {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border-color: rgba(16, 185, 129, 0.3);
}

.estado-cancelado {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.3);
}

/* Pagos */
.pago-pagado,
.pago-aprobado {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border-color: rgba(16, 185, 129, 0.3);
}

.pago-no-pagado,
.pago-pendiente {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.3);
}

.pago-rechazado {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.3);
}

.pedido-total {
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--color-text);
}

/* ACCIONES */
.acciones {
  display: flex;
  gap: 4px;
}

.btn-accion {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.btn-accion:hover {
  background: rgba(6, 182, 212, 0.1);
  border-color: var(--color-primary);
}

/* SIN RESULTADOS */
.sin-resultados {
  padding: 40px 20px;
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 0.85rem;
}

/* MENSAJES DE ESTADO */
.mensaje-estado {
  padding: 40px 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.mensaje-estado.error {
  color: var(--color-error);
}

.mensaje-estado p {
  font-size: 0.9rem;
  margin: 0;
}

/* SPINNER DE CARGA */
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.btn-reintentar {
  padding: 8px 20px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.8rem;
}

.btn-reintentar:hover {
  background: var(--color-primary-dark);
}

/* PAGINACIÓN */
.paginacion {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
}

.paginacion-info {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  margin: 0;
}

.paginacion-controles {
  display: flex;
  gap: 4px;
}

.btn-pagina {
  min-width: 32px;
  height: 32px;
  padding: 0 10px;
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.8rem;
}

.btn-pagina:hover:not(:disabled) {
  background: rgba(6, 182, 212, 0.1);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.btn-pagina.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.btn-pagina:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 1200px) {
  .tabla-pedidos {
    font-size: 0.75rem;
  }

  .tabla-pedidos th,
  .tabla-pedidos td {
    padding: 6px 8px;
  }
  
  .cliente-avatar,
  .producto-imagen {
    width: 28px;
    height: 28px;
    font-size: 0.7rem;
  }
  
  .producto-imagen {
    font-size: 1rem;
  }
}
</style>
