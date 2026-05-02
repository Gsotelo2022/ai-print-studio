<template>
  <div class="gestion-productos">

    <!-- HEADER -->
    <div class="view-header">
      <div>
        <h1>👕 Gestión de productos</h1>
        <p>Administra el catálogo</p>
      </div>
      <button class="btn" @click="abrirModalNuevo">
        ➕ Nuevo producto
      </button>
    </div>

    <!-- BUSCADOR -->
    <div class="search-container">
      <input
        v-model="busqueda"
        placeholder="Buscar producto..."
      />
      <span v-if="busqueda">
        {{ productosFiltrados.length }} resultado(s)
      </span>
    </div>

    <!-- LOADING -->
    <div v-if="cargando" class="estado">
      ⏳ Cargando productos...
    </div>

    <!-- ERROR -->
    <div v-else-if="error" class="estado error">
      ⚠️ {{ error }}
      <button @click="cargarProductos">Reintentar</button>
    </div>

    <!-- LISTA -->
    <div v-else class="productos-grid">

      <div
        v-for="producto in productosFiltrados"
        :key="producto.id_producto"
        class="card"
      >
        <h3>{{ producto.nombre }}</h3>

        <!-- PRECIO -->
        <div v-if="productoEditando?.id_producto === producto.id_producto">
          <input
            v-model.number="precioTemporal"
            type="number"
          />
          <div class="acciones">
            <button @click="confirmarEdicion(producto)">✓</button>
            <button @click="cancelarEdicion">✗</button>
          </div>
        </div>

        <div v-else>
          <p class="precio">{{ formatearMoneda(producto.precio) }}</p>
          <div class="acciones">
            <button @click="iniciarEdicion(producto)">✏️</button>
            <button class="danger" @click="eliminarProducto(producto)">🗑️</button>
          </div>
        </div>
      </div>

    </div>

    <!-- MODAL NUEVO -->
    <div v-if="mostrarModalNuevo" class="modal" @click.self="cerrarModalNuevo">
      <div class="modal-box">

        <h2>➕ Nuevo producto</h2>

        <input v-model="nuevoProducto.nombre" placeholder="Nombre" />
        <input v-model="nuevoProducto.descripcion" placeholder="Descripción" />

        <input type="file" @change="handleFileChange" />

        <div class="acciones">
          <button @click="crearProducto">Crear</button>
          <button @click="cerrarModalNuevo">Cancelar</button>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi.js'

const { get, put, post, del } = useApi()

/* =========================
   STATE
========================= */
const productos = ref([])
const busqueda = ref('')
const cargando = ref(false)
const error = ref(null)

const productoEditando = ref(null)
const precioTemporal = ref(0)

// modal
const mostrarModalNuevo = ref(false)
const archivoSeleccionado = ref(null)

const nuevoProducto = ref({
  nombre: '',
  descripcion: ''
})

/* =========================
   LOAD
========================= */
onMounted(cargarProductos)

async function cargarProductos() {
  cargando.value = true
  error.value = null

  try {
    const data = await get('/admin/productos')

    if (!Array.isArray(data)) {
      throw new Error('Formato inválido')
    }

    // El endpoint admin devuelve productos sin precio_desde;
    // usamos precio_desde del endpoint público si está disponible,
    // sino mostramos 0 hasta que se agreguen variantes.
    productos.value = data.map((p) => ({
      id_producto: p.id_producto,
      nombre: p.nombre || 'Sin nombre',
      descripcion: p.descripcion,
      precio: Number(p.precio_desde) || 0,
    }))

  } catch (e) {
    console.error(e)
    error.value = e.message || 'Error cargando productos'
  } finally {
    cargando.value = false
  }
}

/* =========================
   FILTRO
========================= */
const productosFiltrados = computed(() => {
  if (!busqueda.value) return productos.value

  return productos.value.filter(p =>
    p.nombre.toLowerCase().includes(busqueda.value.toLowerCase())
  )
})

/* =========================
   EDICIÓN
========================= */
function iniciarEdicion(producto) {
  productoEditando.value = producto
  precioTemporal.value = producto.precio
}

function cancelarEdicion() {
  productoEditando.value = null
  precioTemporal.value = 0
}

async function confirmarEdicion(producto) {
  const nuevo = Number(precioTemporal.value)

  if (!nuevo || nuevo <= 0) {
    alert('Precio inválido')
    return
  }

  try {
    await put(`/admin/productos/${producto.id_producto}/precio`, { precio: nuevo })
    producto.precio = nuevo
    cancelarEdicion()
  } catch (e) {
    alert('Error actualizando precio: ' + (e.message || ''))
  }
}

/* =========================
   DELETE
========================= */
async function eliminarProducto(producto) {
  if (!confirm(`Eliminar "${producto.nombre}"?`)) return

  try {
    await del(`/admin/productos/${producto.id_producto}`)
    productos.value = productos.value.filter(
      p => p.id_producto !== producto.id_producto
    )
  } catch (e) {
    alert('Error eliminando: ' + (e.message || ''))
  }
}

/* =========================
   CREAR
========================= */
function abrirModalNuevo() {
  mostrarModalNuevo.value = true
}

function cerrarModalNuevo() {
  mostrarModalNuevo.value = false

  // reset
  nuevoProducto.value = { nombre: '', descripcion: '' }
  archivoSeleccionado.value = null
}

function handleFileChange(e) {
  archivoSeleccionado.value = e.target.files[0]
}

async function crearProducto() {
  if (!nuevoProducto.value.nombre) {
    alert('Nombre requerido')
    return
  }

  try {
    const formData = new FormData()
    formData.append('nombre', nuevoProducto.value.nombre)
    formData.append('descripcion', nuevoProducto.value.descripcion)

    if (archivoSeleccionado.value) {
      formData.append('imagen', archivoSeleccionado.value)
    }

    await post('/admin/productos', formData, true)
    cerrarModalNuevo()
    cargarProductos()

  } catch (e) {
    alert('Error creando producto: ' + (e.message || ''))
  }
}

/* =========================
   UTILS
========================= */
function formatearMoneda(valor) {
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
    minimumFractionDigits: 0
  }).format(valor || 0)
}
</script>

<style scoped>
.gestion-productos {
  padding: 20px;
}

/* HEADER */
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.view-header h1 {
  margin: 0;
  font-size: 1.4rem;
  color: var(--color-text);
}

.view-header p {
  margin: 4px 0 0;
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}

.btn {
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius, 8px);
  padding: 8px 16px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn:hover {
  opacity: 0.85;
}

/* BUSCADOR */
.search-container {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-container input {
  padding: 8px 12px;
  width: 260px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius, 8px);
  color: var(--color-text);
  font-size: 0.85rem;
  outline: none;
  transition: border-color 0.2s;
}

.search-container input:focus {
  border-color: var(--color-primary);
}

.search-container span {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}

/* GRID */
.productos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 15px;
}

/* CARD */
.card {
  background: var(--color-surface);
  padding: 16px;
  border-radius: var(--radius, 8px);
  border: 1px solid var(--color-border);
  box-shadow: 0 2px 6px rgba(0,0,0,0.06);
}

.card h3 {
  margin: 0 0 10px;
  font-size: 0.95rem;
  color: var(--color-text);
}

/* PRECIO */
.precio {
  font-weight: 600;
  color: var(--color-primary);
  margin: 8px 0;
  font-size: 1rem;
}

/* EDICIÓN INLINE */
.card input[type="number"] {
  width: 100%;
  padding: 6px 10px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius, 8px);
  color: var(--color-text);
  font-size: 0.85rem;
  margin-bottom: 8px;
}

/* BOTONES */
.acciones {
  display: flex;
  gap: 6px;
  margin-top: 8px;
}

.acciones button {
  flex: 1;
  padding: 5px 0;
  border: 1px solid var(--color-border);
  border-radius: var(--radius, 8px);
  background: var(--color-bg);
  color: var(--color-text);
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.acciones button:hover {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.acciones button.danger:hover {
  background: #ef4444;
  border-color: #ef4444;
  color: white;
}

/* ESTADOS */
.estado {
  padding: 40px 20px;
  text-align: center;
  color: var(--color-text-secondary);
}

.estado.error {
  color: #ef4444;
}

.estado button {
  margin-top: 10px;
  padding: 6px 14px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius, 8px);
  cursor: pointer;
}

/* MODAL */
.modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.modal-box {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius, 8px);
  padding: 28px;
  width: 380px;
  max-width: 90vw;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
}

.modal-box h2 {
  margin: 0 0 20px;
  font-size: 1.1rem;
  color: var(--color-text);
}

.modal-box input[type="text"],
.modal-box input[type="file"] {
  display: block;
  width: 100%;
  box-sizing: border-box;
  margin-bottom: 12px;
  padding: 8px 12px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius, 8px);
  color: var(--color-text);
  font-size: 0.85rem;
  outline: none;
  transition: border-color 0.2s;
}

.modal-box input[type="text"]:focus {
  border-color: var(--color-primary);
}

.modal-box input[type="file"] {
  padding: 6px;
  cursor: pointer;
}

.modal-box .acciones {
  margin-top: 20px;
  justify-content: flex-end;
}

.modal-box .acciones button {
  flex: none;
  padding: 7px 18px;
  font-size: 0.85rem;
}

.modal-box .acciones button:first-child {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}
</style>