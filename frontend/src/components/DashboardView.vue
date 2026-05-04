<template>
  <div class="dashboard-view">

    <!-- HEADER -->
    <div class="view-header">
      <h1 class="view-title">📊 Dashboard</h1>
      <p class="view-description">Gestión de pedidos y ventas</p>
    </div>

    <!-- MÉTRICAS EN TIEMPO REAL -->
    <div class="metricas-grid" v-if="metricas">

      <div class="metrica-card">
        <span class="metrica-icon">💰</span>
        <div class="metrica-datos">
          <p class="metrica-valor">${{ metricas.hoy.ingresos.toLocaleString('es-AR') }}</p>
          <p class="metrica-label">Ingresos hoy</p>
        </div>
      </div>

      <div class="metrica-card">
        <span class="metrica-icon">📦</span>
        <div class="metrica-datos">
          <p class="metrica-valor">{{ metricas.hoy.pedidos }}</p>
          <p class="metrica-label">Pedidos hoy</p>
        </div>
      </div>

      <div class="metrica-card">
        <span class="metrica-icon">📅</span>
        <div class="metrica-datos">
          <p class="metrica-valor">${{ metricas.mes_actual.ingresos.toLocaleString('es-AR') }}</p>
          <p class="metrica-label">Ingresos este mes</p>
        </div>
      </div>

      <div class="metrica-card">
        <span class="metrica-icon">👥</span>
        <div class="metrica-datos">
          <p class="metrica-valor">{{ metricas.mes_actual.clientes_nuevos }}</p>
          <p class="metrica-label">Clientes nuevos este mes</p>
        </div>
      </div>

      <div class="metrica-card" :class="{ 'alerta': metricas.totales.pendientes > 5 }">
        <span class="metrica-icon">🔔</span>
        <div class="metrica-datos">
          <p class="metrica-valor">{{ metricas.totales.pendientes }}</p>
          <p class="metrica-label">Pendientes sin atender</p>
        </div>
      </div>

      <div class="metrica-card" :class="{ 'alerta': metricas.alertas.checkout_abandonado > 0 }">
        <span class="metrica-icon">⚠️</span>
        <div class="metrica-datos">
          <p class="metrica-valor">{{ metricas.alertas.checkout_abandonado }}</p>
          <p class="metrica-label">Checkout abandonado (+2hs)</p>
        </div>
      </div>

    </div>

    <div v-if="cargandoMetricas" class="metricas-cargando">
      ⏳ Cargando métricas...
    </div>

    <!-- TOP PRODUCTOS -->
    <div class="top-productos" v-if="metricas && metricas.top_productos.length">
      <h3 class="top-titulo">🏆 Top 5 productos más vendidos</h3>
      <div class="top-lista">
        <div
          v-for="(prod, i) in metricas.top_productos"
          :key="prod.nombre"
          class="top-item"
        >
          <span class="top-pos">{{ i + 1 }}</span>
          <span class="top-nombre">{{ prod.nombre }}</span>
          <span class="top-cant">{{ prod.cantidad_vendida }} uds.</span>
          <span class="top-ingreso">${{ prod.ingreso_generado.toLocaleString('es-AR') }}</span>
        </div>
      </div>
    </div>


    <!-- PEDIDOS CON FILTROS -->
    <div class="section pedidos-section">
        <div class="section-header">
          <div class="header-left">
            <button @click="cargarPedidos" class="btn-refresh" title="Actualizar">
              🔄
            </button>
          </div>
          <div class="header-right">
            <button @click="abrirModalGraficos" class="btn-graficos">
              📊 Ver en Gráfico
            </button>
            <div class="export-dropdown">
              <button @click="mostrarMenuExport = !mostrarMenuExport" class="btn-export">
                📄 Exportar ▾
              </button>
              <div v-if="mostrarMenuExport" class="dropdown-menu">
                <button @click="exportar('excel')" class="dropdown-item">
                  📊 Excel (.xlsx)
                </button>
                <button @click="exportar('csv')" class="dropdown-item">
                  📋 CSV (.csv)
                </button>
                <button @click="exportar('pdf')" class="dropdown-item">
                  📄 PDF (.pdf)
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- FILTROS RÁPIDOS -->
        <div class="filtros-rapidos">
          <button 
            v-for="filtro in filtrosRapidos" 
            :key="filtro.id"
            @click="aplicarFiltroRapido(filtro.id)"
            :class="['btn-filtro', { active: filtroActual === filtro.id }]"
          >
            {{ filtro.icon }} {{ filtro.label }}
            <span v-if="filtro.count !== undefined" class="badge">{{ filtro.count }}</span>
          </button>
        </div>



        <!-- FILTROS POR COLUMNA -->
        <div class="filtros-columna">
          <input 
            v-model="filtroNumero" 
            type="text" 
            placeholder="🔍 Buscar número de pedido..."
            class="input-filtro"
          >
          <input 
            v-model="filtroCliente" 
            type="text" 
            placeholder="🔍 Buscar cliente..."
            class="input-filtro"
          >
          <select v-model="filtroEstado" class="select-filtro">
            <option value="">Todos los estados</option>
            <option value="pendiente">Pendiente</option>
            <option value="en-proceso">En Proceso</option>
            <option value="completado">Completado</option>
            <option value="cancelado">Cancelado</option>
          </select>
          <select v-model="filtroPago" class="select-filtro">
            <option value="">Todos los pagos</option>
            <option value="aprobado">Pagado</option>
            <option value="pendiente">Pendiente</option>
            <option value="rechazado">Rechazado</option>
          </select>
          <button @click="limpiarFiltros" class="btn-limpiar">Limpiar</button>
        </div>

        <!-- TABLA DE PEDIDOS -->
        <div v-if="cargandoPedidos" class="loading-inline">
          ⏳ Cargando pedidos...
        </div>
        
        <div v-else-if="errorPedidos" class="error-inline">
          ❌ {{ errorPedidos }}
        </div>

        <div v-else-if="pedidosFiltrados.length === 0" class="no-data">
          Sin pedidos que coincidan con los filtros
        </div>

        <div v-else class="tabla-container">
          <table class="pedidos-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Número</th>
                <th>Cliente</th>
                <th>Producto</th>
                <th>Fecha</th>
                <th>Total</th>
                <th>Estado</th>
                <th>Pago</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(pedido, idx) in pedidosPaginados" :key="pedido.id">
                <td>{{ (paginaActual - 1) * itemsPorPagina + idx + 1 }}</td>
                <td><strong>{{ pedido.numero }}</strong></td>
                <td>
                  <div class="cliente-info">
                    <div class="avatar" :style="{ backgroundColor: pedido.cliente.color }">
                      {{ pedido.cliente.iniciales }}
                    </div>
                    <div class="cliente-texto">
                      <div class="nombre">{{ pedido.cliente.nombre }}</div>
                      <div class="email">{{ pedido.cliente.email }}</div>
                    </div>
                  </div>
                </td>
                <td>
                  <div class="producto-info">
                    <span class="emoji">{{ pedido.producto.emoji }}</span>
                    <div>
                      <div class="nombre">{{ pedido.producto.nombre }}</div>
                      <div class="detalles">{{ pedido.producto.detalles }}</div>
                    </div>
                  </div>
                </td>
                <td>
                  <div class="fecha-info">
                    <div class="dia">{{ pedido.fecha.dia }}</div>
                    <div class="hora">{{ pedido.fecha.hora }}</div>
                  </div>
                </td>
                <td class="precio">${{ formatearPrecio(pedido.total) }}</td>
                <td>
                  <span :class="['badge-estado', 'estado-' + pedido.estado.tipo]">
                    {{ pedido.estado.texto }}
                  </span>
                </td>
                <td>
                  <span :class="['badge-pago', 'pago-' + pedido.pago.tipo]">
                    {{ pedido.pago.texto }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- PAGINACIÓN -->
        <div v-if="totalPaginas > 1" class="paginacion">
          <button 
            @click="paginaActual > 1 && paginaActual--" 
            :disabled="paginaActual === 1"
            class="btn-pag"
          >
            ◀
          </button>
          <span class="pag-info">
            Página {{ paginaActual }} de {{ totalPaginas }}
            ({{ pedidosFiltrados.length }} pedidos)
          </span>
          <button 
            @click="paginaActual < totalPaginas && paginaActual++" 
            :disabled="paginaActual === totalPaginas"
            class="btn-pag"
          >
            ▶
          </button>
        </div>
      </div>
  </div>

</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useApi } from '../composables/useApi.js'

const { get } = useApi()

// =====================
// STATE
// =====================
const cargandoPedidos = ref(false)
const errorPedidos = ref(null)
const pedidos = ref([])

// Métricas
const metricas = ref(null)
const cargandoMetricas = ref(false)


const filtroActual = ref('todos')
const filtroNumero = ref('')
const filtroCliente = ref('')
const filtroEstado = ref('')
const filtroPago = ref('')
const paginaActual = ref(1)
const itemsPorPagina = 10
const mostrarMenuExport = ref(false)

// =====================
// FILTROS RÁPIDOS
// =====================
const filtrosRapidos = computed(() => {
  const hoy = new Date()
  const inicioSemana = new Date(hoy)
  inicioSemana.setDate(hoy.getDate() - hoy.getDay())
  
  const pedidosSemana = pedidos.value.filter(p => {
    // Parsear fecha desde el objeto { dia, hora }
    const [dia, mes, anio] = p.fecha.dia.split('/')
    const fecha = new Date(anio, mes - 1, dia)
    return fecha >= inicioSemana
  }).length

  const inicioMes = new Date(hoy.getFullYear(), hoy.getMonth(), 1)
  const pedidosMes = pedidos.value.filter(p => {
    const [dia, mes, anio] = p.fecha.dia.split('/')
    const fecha = new Date(anio, mes - 1, dia)
    return fecha >= inicioMes
  }).length

  const pedidosPagados = pedidos.value.filter(p => p.pago.valor === 'aprobado').length
  const pedidosPendientes = pedidos.value.filter(p => p.estado.tipo === 'pendiente').length
  const pedidosEnProceso = pedidos.value.filter(p => p.estado.tipo === 'en-proceso').length
  const pedidosEntregados = pedidos.value.filter(p => p.estado.tipo === 'completado').length
  const pedidosNoPagados = pedidos.value.filter(p => p.pago.valor === 'pendiente' || p.pago.valor === 'rechazado').length

  return [
    { id: 'todos', label: 'Todos', icon: '📋', count: pedidos.value.length },
    { id: 'mes', label: 'Este mes', icon: '📅', count: pedidosMes },
    { id: 'semana', label: 'Esta semana', icon: '📆', count: pedidosSemana },
    { id: 'pagados', label: 'Pagados', icon: '✅', count: pedidosPagados },
    { id: 'no-pagados', label: 'Sin pagar', icon: '⏳', count: pedidosNoPagados },
    { id: 'pendientes', label: 'Pendientes', icon: '🔔', count: pedidosPendientes },
    { id: 'en-proceso', label: 'En Proceso', icon: '⚙️', count: pedidosEnProceso },
    { id: 'entregados', label: 'Entregados', icon: '📦', count: pedidosEntregados }
  ]
})

// =====================
// PEDIDOS FILTRADOS
// =====================
const pedidosFiltrados = computed(() => {
  let resultado = [...pedidos.value]

  // Filtro rápido
  const hoy = new Date()
  const inicioSemana = new Date(hoy)
  inicioSemana.setDate(hoy.getDate() - hoy.getDay())

  switch (filtroActual.value) {
    case 'mes':
      const inicioMes = new Date(hoy.getFullYear(), hoy.getMonth(), 1)
      resultado = resultado.filter(p => {
        const [dia, mes, anio] = p.fecha.dia.split('/')
        const fecha = new Date(anio, mes - 1, dia)
        return fecha >= inicioMes
      })
      break
    case 'semana':
      resultado = resultado.filter(p => {
        const [dia, mes, anio] = p.fecha.dia.split('/')
        const fecha = new Date(anio, mes - 1, dia)
        return fecha >= inicioSemana
      })
      break
    case 'pagados':
      resultado = resultado.filter(p => p.pago.valor === 'aprobado')
      break
    case 'no-pagados':
      resultado = resultado.filter(p => p.pago.valor === 'pendiente' || p.pago.valor === 'rechazado')
      break
    case 'pendientes':
      resultado = resultado.filter(p => p.estado.tipo === 'pendiente')
      break
    case 'en-proceso':
      resultado = resultado.filter(p => p.estado.tipo === 'en-proceso')
      break
    case 'entregados':
      resultado = resultado.filter(p => p.estado.tipo === 'completado')
      break
  }

  // Filtros por columna
  if (filtroNumero.value) {
    resultado = resultado.filter(p => 
      p.numero.toLowerCase().includes(filtroNumero.value.toLowerCase())
    )
  }

  if (filtroCliente.value) {
    resultado = resultado.filter(p => 
      p.cliente.nombre.toLowerCase().includes(filtroCliente.value.toLowerCase()) ||
      p.cliente.email.toLowerCase().includes(filtroCliente.value.toLowerCase())
    )
  }

  if (filtroEstado.value) {
    resultado = resultado.filter(p => p.estado.tipo === filtroEstado.value)
  }

  if (filtroPago.value) {
    resultado = resultado.filter(p => p.pago.valor === filtroPago.value)
  }

  return resultado
})

// =====================
// PAGINACIÓN
// =====================
const totalPaginas = computed(() => {
  return Math.ceil(pedidosFiltrados.value.length / itemsPorPagina)
})

const pedidosPaginados = computed(() => {
  const inicio = (paginaActual.value - 1) * itemsPorPagina
  const fin = inicio + itemsPorPagina
  return pedidosFiltrados.value.slice(inicio, fin)
})

// =====================
// DATA
// =====================

async function cargarPedidos() {
  cargandoPedidos.value = true
  errorPedidos.value = null

  try {
    const data = await get('/admin/pedidos?filtro=todos')
    pedidos.value = Array.isArray(data) ? data : (data?.pedidos || [])
    console.log('✅ Pedidos cargados:', pedidos.value.length)

  } catch (e) {
    errorPedidos.value = e.message
    console.error('❌ Error cargando pedidos:', e)
  } finally {
    cargandoPedidos.value = false
  }
}

async function cargarMetricas() {
  cargandoMetricas.value = true
  try {
    metricas.value = await getMetricas()
  } catch (e) {
    console.warn('⚠️ Métricas no disponibles:', e.message)
    // No bloquea el dashboard si falla
  } finally {
    cargandoMetricas.value = false
  }
}

// =====================
// ACCIONES
// =====================
function aplicarFiltroRapido(filtroId) {
  filtroActual.value = filtroId
  paginaActual.value = 1
}

function limpiarFiltros() {
  filtroNumero.value = ''
  filtroCliente.value = ''
  filtroEstado.value = ''
  filtroPago.value = ''
  filtroActual.value = 'todos'
  paginaActual.value = 1
}

// =====================
// EXPORTACIÓN
// =====================
function exportar(tipo) {
  mostrarMenuExport.value = false
  
  const datos = pedidosFiltrados.value
  
  if (datos.length === 0) {
    alert('No hay pedidos para exportar')
    return
  }

  switch (tipo) {
    case 'excel':
      exportarExcel(datos)
      break
    case 'csv':
      exportarCSV(datos)
      break
    case 'pdf':
      exportarPDF(datos)
      break
  }
}

function exportarCSV(datos) {
  const headers = ['Número', 'Cliente', 'Email', 'Producto', 'Fecha', 'Total', 'Estado', 'Pago']
  const rows = datos.map(p => [
    p.numero,
    p.cliente.nombre,
    p.cliente.email,
    p.producto.nombre,
    `${p.fecha.dia} ${p.fecha.hora}`,
    p.total,
    p.estado.texto,
    p.pago.texto
  ])

  const csv = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\\n')

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `pedidos_${new Date().toISOString().split('T')[0]}.csv`
  link.click()
}

function exportarExcel(datos) {
  // Crear tabla HTML para Excel
  const headers = ['Número', 'Cliente', 'Email', 'Producto', 'Fecha', 'Total', 'Estado', 'Pago']
  const rows = datos.map(p => [
    p.numero,
    p.cliente.nombre,
    p.cliente.email,
    p.producto.nombre,
    `${p.fecha.dia} ${p.fecha.hora}`,
    `$${formatearPrecio(p.total)}`,
    p.estado.texto,
    p.pago.texto
  ])

  const html = `
    <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel">
    <head><meta charset="UTF-8"></head>
    <body>
      <table border="1">
        <thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead>
        <tbody>
          ${rows.map(row => `<tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>`).join('')}
        </tbody>
      </table>
    </body>
    </html>
  `

  const blob = new Blob([html], { type: 'application/vnd.ms-excel' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `pedidos_${new Date().toISOString().split('T')[0]}.xls`
  link.click()
}

function exportarPDF(datos) {
  // Abrir ventana de impresión con los datos formateados
  const contenido = `
    <html>
    <head>
      <title>Pedidos - ${new Date().toLocaleDateString()}</title>
      <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        h1 { color: #333; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
      </style>
    </head>
    <body>
      <h1>📦 Reporte de Pedidos</h1>
      <p>Fecha: ${new Date().toLocaleString('es-AR')}</p>
      <p>Total de pedidos: ${datos.length}</p>
      <table>
        <thead>
          <tr>
            <th>Número</th>
            <th>Cliente</th>
            <th>Producto</th>
            <th>Fecha</th>
            <th>Total</th>
            <th>Estado</th>
            <th>Pago</th>
          </tr>
        </thead>
        <tbody>
          ${datos.map(p => `
            <tr>
              <td>${p.numero}</td>
              <td>${p.cliente.nombre}<br><small>${p.cliente.email}</small></td>
              <td>${p.producto.nombre}<br><small>${p.producto.detalles}</small></td>
              <td>${p.fecha.dia}<br><small>${p.fecha.hora}</small></td>
              <td>$${formatearPrecio(p.total)}</td>
              <td>${p.estado.texto}</td>
              <td>${p.pago.texto}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </body>
    </html>
  `

  const ventana = window.open('', '_blank')
  ventana.document.write(contenido)
  ventana.document.close()
  
  setTimeout(() => {
    ventana.print()
  }, 250)
}

// =====================
// HELPERS
// =====================
function formatearPrecio(precio) {
  return new Intl.NumberFormat('es-AR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(precio)
}

// =====================
// ABRIR GRÁFICOS EN NUEVA VENTANA
// =====================
function abrirModalGraficos() {
  if (pedidosFiltrados.value.length === 0) {
    alert('⚠️ No hay datos para mostrar gráficos. Ajusta los filtros.')
    return
  }

  const datos = pedidosFiltrados.value
  
  // Contar por estado
  const conteoEstados = {}
  datos.forEach(p => {
    const estado = p.estado.texto
    conteoEstados[estado] = (conteoEstados[estado] || 0) + 1
  })

  // Contar por pago
  const conteoPagos = {}
  datos.forEach(p => {
    const pago = p.pago.texto
    conteoPagos[pago] = (conteoPagos[pago] || 0) + 1
  })

  // Ventas por producto
  const ventasProductos = {}
  datos.forEach(p => {
    const producto = p.producto.nombre
    ventasProductos[producto] = (ventasProductos[producto] || 0) + p.total
  })

  // Timeline
  const porFecha = {}
  datos.forEach(p => {
    const fecha = p.fecha.dia
    porFecha[fecha] = (porFecha[fecha] || 0) + 1
  })

  const fechasOrdenadas = Object.keys(porFecha).sort((a, b) => {
    const [diaA, mesA, anioA] = a.split('/')
    const [diaB, mesB, anioB] = b.split('/')
    const fechaA = new Date(anioA, mesA - 1, diaA)
    const fechaB = new Date(anioB, mesB - 1, diaB)
    return fechaA - fechaB
  })

  // Crear HTML para la nueva ventana
  const htmlContent = '<!DOCTYPE html>' +
    '<html lang="es">' +
    '<head>' +
    '<meta charset="UTF-8">' +
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">' +
    '<title>Gráficos - AI Print Studio</title>' +
    '<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"><' + '/script>' +
    '<style>' +
    '* { margin: 0; padding: 0; box-sizing: border-box; }' +
    'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #e2e8f0; padding: 20px; min-height: 100vh; }' +
    '.header { text-align: center; margin-bottom: 30px; padding: 20px; background: rgba(30, 41, 59, 0.5); border-radius: 12px; border: 1px solid #334155; }' +
    '.header h1 { font-size: 2rem; margin-bottom: 8px; background: linear-gradient(135deg, #6366f1, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }' +
    '.header p { color: #94a3b8; font-size: 0.95rem; }' +
    '.graficos-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); gap: 24px; max-width: 1600px; margin: 0 auto; }' +
    '.grafico-card { background: #1e293b; padding: 24px; border-radius: 12px; border: 1px solid #334155; box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3); transition: transform 0.2s; }' +
    '.grafico-card:hover { transform: translateY(-4px); box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4); }' +
    '.grafico-card.full-width { grid-column: 1 / -1; }' +
    '.grafico-titulo { margin: 0 0 20px 0; font-size: 1.15rem; color: #e2e8f0; font-weight: 600; text-align: center; }' +
    '.chart { width: 100%; height: 400px; }' +
    '.chart-timeline { height: 320px; }' +
    '@media print { body { background: white; color: black; } .grafico-card { break-inside: avoid; page-break-inside: avoid; } }' +
    '</style>' +
    '</head>' +
    '<body>' +
    '<div class="header">' +
    '<h1>📊 Gráficos de Pedidos</h1>' +
    '<p>Total de registros: ' + datos.length + '</p>' +
    '</div>' +
    '<div class="graficos-container">' +
    '<div class="grafico-card">' +
    '<h3 class="grafico-titulo">📊 Estados de Pedidos</h3>' +
    '<div id="chart-estados" class="chart"></div>' +
    '</div>' +
    '<div class="grafico-card">' +
    '<h3 class="grafico-titulo">💰 Estado de Pagos</h3>' +
    '<div id="chart-pagos" class="chart"></div>' +
    '</div>' +
    '<div class="grafico-card">' +
    '<h3 class="grafico-titulo">📈 Ventas por Producto</h3>' +
    '<div id="chart-productos" class="chart"></div>' +
    '</div>' +
    '<div class="grafico-card full-width">' +
    '<h3 class="grafico-titulo">📅 Timeline de Pedidos</h3>' +
    '<div id="chart-timeline" class="chart chart-timeline"></div>' +
    '</div>' +
    '</div>' +
    '<script>' +
    'const conteoEstados = ' + JSON.stringify(conteoEstados) + ';' +
    'const conteoPagos = ' + JSON.stringify(conteoPagos) + ';' +
    'const ventasProductos = ' + JSON.stringify(ventasProductos) + ';' +
    'const porFecha = ' + JSON.stringify(porFecha) + ';' +
    'const fechasOrdenadas = ' + JSON.stringify(fechasOrdenadas) + ';' +
    'google.charts.load("current", { "packages": ["corechart"], "language": "es" });' +
    'google.charts.setOnLoadCallback(dibujarTodos);' +
    'function dibujarTodos() {' +
    '  dibujarGraficoEstados();' +
    '  dibujarGraficoPagos();' +
    '  dibujarGraficoProductos();' +
    '  dibujarGraficoTimeline();' +
    '}' +
    'function dibujarGraficoEstados() {' +
    '  const dataArray = [["Estado", "Cantidad"]];' +
    '  Object.entries(conteoEstados).forEach(([estado, cantidad]) => {' +
    '    dataArray.push([estado, cantidad]);' +
    '  });' +
    '  const data = google.visualization.arrayToDataTable(dataArray);' +
    '  const options = {' +
    '    title: "",' +
    '    pieHole: 0.4,' +
    '    backgroundColor: "#1e293b",' +
    '    legend: { position: "bottom", textStyle: { color: "#e2e8f0", fontSize: 13 }, alignment: "center" },' +
    '    chartArea: { width: "90%", height: "70%", top: 20 },' +
    '    colors: ["#fbbf24", "#3b82f6", "#10b981", "#ef4444"],' +
    '    pieSliceTextStyle: { color: "#1e293b", fontSize: 15, bold: true },' +
    '    tooltip: { textStyle: { fontSize: 13 } }' +
    '  };' +
    '  const chart = new google.visualization.PieChart(document.getElementById("chart-estados"));' +
    '  chart.draw(data, options);' +
    '}' +
    'function dibujarGraficoPagos() {' +
    '  const dataArray = [["Estado Pago", "Cantidad"]];' +
    '  Object.entries(conteoPagos).forEach(([pago, cantidad]) => {' +
    '    dataArray.push([pago, cantidad]);' +
    '  });' +
    '  const data = google.visualization.arrayToDataTable(dataArray);' +
    '  const options = {' +
    '    title: "",' +
    '    pieHole: 0.4,' +
    '    backgroundColor: "#1e293b",' +
    '    legend: { position: "bottom", textStyle: { color: "#e2e8f0", fontSize: 13 }, alignment: "center" },' +
    '    chartArea: { width: "90%", height: "70%", top: 20 },' +
    '    colors: ["#10b981", "#fbbf24", "#ef4444"],' +
    '    pieSliceTextStyle: { color: "#1e293b", fontSize: 15, bold: true },' +
    '    tooltip: { textStyle: { fontSize: 13 } }' +
    '  };' +
    '  const chart = new google.visualization.PieChart(document.getElementById("chart-pagos"));' +
    '  chart.draw(data, options);' +
    '}' +
    'function dibujarGraficoProductos() {' +
    '  const dataArray = [["Producto", "Ventas"]];' +
    '  Object.entries(ventasProductos).forEach(([producto, total]) => {' +
    '    dataArray.push([producto, total]);' +
    '  });' +
    '  const data = google.visualization.arrayToDataTable(dataArray);' +
    '  const options = {' +
    '    title: "",' +
    '    backgroundColor: "#1e293b",' +
    '    legend: { position: "none" },' +
    '    chartArea: { width: "80%", height: "70%", top: 20, left: 70 },' +
    '    colors: ["#3b82f6"],' +
    '    hAxis: { textStyle: { color: "#e2e8f0", fontSize: 12 }, gridlines: { color: "#334155" }, slantedText: true, slantedTextAngle: 30 },' +
    '    vAxis: { textStyle: { color: "#e2e8f0", fontSize: 12 }, gridlines: { color: "#334155" }, format: "$#,###", minValue: 0 },' +
    '    bar: { groupWidth: "65%" },' +
    '    tooltip: { textStyle: { fontSize: 13 } }' +
    '  };' +
    '  const chart = new google.visualization.ColumnChart(document.getElementById("chart-productos"));' +
    '  chart.draw(data, options);' +
    '}' +
    'function dibujarGraficoTimeline() {' +
    '  const dataArray = [["Fecha", "Pedidos"]];' +
    '  fechasOrdenadas.forEach(fecha => {' +
    '    dataArray.push([fecha, porFecha[fecha]]);' +
    '  });' +
    '  const data = google.visualization.arrayToDataTable(dataArray);' +
    '  const options = {' +
    '    title: "",' +
    '    backgroundColor: "#1e293b",' +
    '    legend: { position: "none" },' +
    '    chartArea: { width: "88%", height: "65%", top: 20, left: 60, right: 20 },' +
    '    colors: ["#8b5cf6"],' +
    '    hAxis: { textStyle: { color: "#e2e8f0", fontSize: 11 }, gridlines: { color: "#334155" }, slantedText: true, slantedTextAngle: 45 },' +
    '    vAxis: { textStyle: { color: "#e2e8f0", fontSize: 12 }, gridlines: { color: "#334155" }, minValue: 0, format: "0" },' +
    '    curveType: "function",' +
    '    pointSize: 7,' +
    '    lineWidth: 3,' +
    '    tooltip: { textStyle: { fontSize: 13 } }' +
    '  };' +
    '  const chart = new google.visualization.LineChart(document.getElementById("chart-timeline"));' +
    '  chart.draw(data, options);' +
    '}' +
    '<' + '/script>' +
    '</body>' +
    '</html>'

  // Abrir ventana nueva
  const ventana = window.open('', '_blank', 'width=1400,height=900,menubar=yes,toolbar=yes,location=yes,status=yes,scrollbars=yes')
  if (ventana) {
    ventana.document.write(htmlContent)
    ventana.document.close()
  } else {
    alert('⚠️ Por favor, permite pop-ups para ver los gráficos')
  }
}

// =====================
// INIT
// =====================
onMounted(() => {
  cargarPedidos()
  cargarMetricas()
  
  // Cerrar dropdown al hacer clic fuera
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.export-dropdown')) {
      mostrarMenuExport.value = false
    }
  })
})

</script>

<style scoped>
.dashboard-view {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 7px;
  max-height: calc(100vh - 80px);
  overflow-y: auto;
  scroll-behavior: smooth;
}

.view-header {
  margin-bottom: 4px;
}

.view-title {
  font-size: 1.2rem;
  margin: 0 0 2px 0;
  color: #e2e8f0;
}

.view-description {
  color: #94a3b8;
  margin: 0;
  font-size: 0.8rem;
}

.loading-message,
.error-message {
  background: #1e293b;
  padding: 7px;
  border-radius: 4px;
  text-align: center;
  font-size: 0.75rem;
}

.error-message {
  background: #7f1d1d;
  color: #fca5a5;
}

.btn-retry {
  margin-top: 6px;
  padding: 5px 10px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.75rem;
}

.btn-retry:hover {
  background: #dc2626;
}

/* SECTION */
.section {
  background: #1e293b;
  padding: 7px;
  border-radius: 5px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 7px;
}

.header-left,
.header-right {
  display: flex;
  gap: 6px;
  align-items: center;
}

.section-title {
  font-size: 0.9rem;
  margin: 0;
  color: #e2e8f0;
}

.btn-refresh {
  background: #334155;
  border: none;
  padding: 4px 6px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.75rem;
  transition: background 0.2s;
}

.btn-refresh:hover {
  background: #475569;
}

/* EXPORTACIÓN */
.export-dropdown {
  position: relative;
}

.btn-export {
  background: #10b981;
  border: none;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.75rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 3px;
}

.btn-export:hover {
  background: #059669;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 2px;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 3px;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.3);
  z-index: 100;
  min-width: 100px;
  overflow: hidden;
}

.dropdown-item {
  width: 100%;
  background: transparent;
  border: none;
  color: #e2e8f0;
  padding: 4px 8px;
  text-align: left;
  cursor: pointer;
  font-size: 0.7rem;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.dropdown-item:hover {
  background: #334155;
}

/* FILTROS RÁPIDOS */
.filtros-rapidos {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 6px;
  padding-bottom: 6px;
  border-bottom: 1px solid #334155;
}

.btn-filtro {
  background: #334155;
  border: 2px solid transparent;
  color: #e2e8f0;
  padding: 4px 6px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  gap: 3px;
  transition: all 0.2s;
}

.btn-filtro:hover {
  background: #475569;
  transform: translateY(-2px);
}

.btn-filtro.active {
  background: #0ea5e9;
  border-color: #0284c7;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.2);
}

.badge {
  background: #0f172a;
  padding: 1px 4px;
  border-radius: 6px;
  font-size: 0.6rem;
  font-weight: bold;
}

/* FILTROS POR COLUMNA */
.filtros-columna {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 4px;
  margin-bottom: 6px;
}

.input-filtro,
.select-filtro {
  padding: 4px 6px;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 4px;
  color: #e2e8f0;
  font-size: 0.75rem;
}

.input-filtro::placeholder {
  color: #64748b;
}

.input-filtro:focus,
.select-filtro:focus {
  outline: none;
  border-color: #0ea5e9;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.2);
}

.btn-limpiar {
  background: #475569;
  border: none;
  color: #e2e8f0;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.75rem;
  transition: background 0.2s;
}

.btn-limpiar:hover {
  background: #64748b;
}

/* TABLA */
.tabla-container {
  overflow-x: auto;
  overflow-y: auto;
  max-height: 360px;
  margin-bottom: 6px;
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.pedidos-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
}

.pedidos-table thead {
  background: #0f172a;
  position: sticky;
  top: 0;
  z-index: 10;
}

.pedidos-table th {
  padding: 4px;
  text-align: left;
  color: #94a3b8;
  font-weight: 600;
  border-bottom: 1px solid #334155;
}

.pedidos-table tbody tr {
  border-bottom: 1px solid #334155;
  transition: background 0.2s;
}

.pedidos-table tbody tr:hover {
  background: #0f172a;
}

.pedidos-table td {
  padding: 4px;
  color: #e2e8f0;
}

.pedidos-table td.precio {
  font-weight: 600;
  color: #10b981;
}

/* CLIENTE INFO */
.cliente-info {
  display: flex;
  align-items: center;
  gap: 4px;
}

.cliente-info .avatar {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 0.6rem;
  flex-shrink: 0;
}

.cliente-info .cliente-texto {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.cliente-info .nombre {
  font-weight: 600;
  color: #f1f5f9;
  font-size: 0.7rem;
}

.cliente-info .email {
  font-size: 0.6rem;
  color: #94a3b8;
}

/* PRODUCTO INFO */
.producto-info {
  display: flex;
  align-items: center;
  gap: 3px;
}

.producto-info .emoji {
  font-size: 0.8rem;
}

.producto-info .nombre {
  font-weight: 600;
  color: #f1f5f9;
  font-size: 0.7rem;
}

.producto-info .detalles {
  font-size: 0.6rem;
  color: #94a3b8;
}

/* FECHA INFO */
.fecha-info {
  display: flex;
  flex-direction: column;
  gap: 0px;
}

.fecha-info .dia {
  font-weight: 600;
  color: #f1f5f9;
  font-size: 0.7rem;
}

.fecha-info .hora {
  font-size: 0.6rem;
  color: #94a3b8;
}

/* BADGES */
.badge-estado,
.badge-pago {
  display: inline-block;
  padding: 2px 5px;
  border-radius: 6px;
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: capitalize;
}

.badge-estado.estado-pendiente {
  background: #fef3c7;
  color: #92400e;
}

.badge-estado.estado-en-proceso {
  background: #dbeafe;
  color: #1e40af;
}

.badge-estado.estado-completado {
  background: #d1fae5;
  color: #065f46;
}

.badge-estado.estado-cancelado {
  background: #fee2e2;
  color: #991b1b;
}

.badge-pago.pago-pagado {
  background: #d1fae5;
  color: #065f46;
}

.badge-pago.pago-no-pagado {
  background: #fef3c7;
  color: #92400e;
}

/* PAGINACIÓN */
.paginacion {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  padding-top: 6px;
  border-top: 1px solid #334155;
}

.btn-pag {
  background: #334155;
  border: none;
  color: #e2e8f0;
  padding: 3px 6px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 0.65rem;
  transition: background 0.2s;
}

.btn-pag:hover:not(:disabled) {
  background: #475569;
}

.btn-pag:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.pag-info {
  color: #94a3b8;
  font-size: 0.65rem;
}

/* MENSAJES */
.loading-inline,
.error-inline,
.no-data {
  text-align: center;
  padding: 14px;
  color: #94a3b8;
  font-size: 0.7rem;
}

.error-inline {
  color: #fca5a5;
}

/* SCROLLBAR PERSONALIZADA */
.dashboard-view::-webkit-scrollbar,
.tabla-container::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

.dashboard-view::-webkit-scrollbar-track,
.tabla-container::-webkit-scrollbar-track {
  background: #0f172a;
  border-radius: 10px;
}

.dashboard-view::-webkit-scrollbar-thumb,
.tabla-container::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 10px;
  border: 2px solid #0f172a;
}

.dashboard-view::-webkit-scrollbar-thumb:hover,
.tabla-container::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}

/* Firefox scrollbar */
.dashboard-view,
.tabla-container {
  scrollbar-width: thin;
  scrollbar-color: #475569 #0f172a;
}

/* BOT\u00d3N GR\u00c1FICOS */
.btn-graficos {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 600;
  transition: all 0.3s;
  box-shadow: 0 1px 2px rgba(99, 102, 241, 0.3);
  margin-right: 5px;
}

.btn-graficos:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(99, 102, 241, 0.4);
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
}
/* =====================
   MÉTRICAS
===================== */
.metricas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 14px;
  margin-bottom: 24px;
}

.metrica-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: border-color 0.2s;
}

.metrica-card.alerta {
  border-color: #f59e0b;
  background: rgba(245, 158, 11, 0.06);
}

.metrica-icon {
  font-size: 1.6rem;
  flex-shrink: 0;
}

.metrica-datos {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.metrica-valor {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
  line-height: 1.2;
}

.metrica-label {
  font-size: 0.7rem;
  color: var(--color-text-secondary);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.metricas-cargando {
  color: var(--color-text-secondary);
  font-size: 0.85rem;
  margin-bottom: 16px;
}

/* =====================
   TOP PRODUCTOS
===================== */
.top-productos {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
}

.top-titulo {
  margin: 0 0 14px 0;
  font-size: 0.95rem;
  color: var(--color-text);
}

.top-lista {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.top-item {
  display: grid;
  grid-template-columns: 24px 1fr 80px 100px;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  font-size: 0.85rem;
}

.top-pos {
  color: var(--color-primary);
  font-weight: 700;
  text-align: center;
}

.top-nombre {
  color: var(--color-text);
  font-weight: 500;
}

.top-cant {
  color: var(--color-text-secondary);
  text-align: right;
}

.top-ingreso {
  color: #4ade80;
  font-weight: 600;
  text-align: right;
}

</style>