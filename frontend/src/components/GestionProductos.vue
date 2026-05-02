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
    const res = await fetch('http://127.0.0.1:5001/productos-ia')

    if (!res.ok) throw new Error('Error HTTP')

    const data = await res.json()

    if (!Array.isArray(data)) {
      throw new Error('Formato inválido')
    }

    productos.value = data.map((p, i) => ({
      id_producto: p.id || i,
      nombre: p.producto || 'Sin nombre',
      precio: Number(p.precio) || 0
    }))

  } catch (e) {
    console.error(e)
    error.value = 'Error cargando productos'
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
    const res = await fetch(
      `http://localhost:8000/api/admin/productos/${producto.id_producto}/precio`,
      {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ precio: nuevo })
      }
    )

    if (!res.ok) throw new Error()

    producto.precio = nuevo
    cancelarEdicion()

  } catch {
    alert('Error actualizando precio')
  }
}

/* =========================
   DELETE
========================= */
async function eliminarProducto(producto) {
  if (!confirm(`Eliminar "${producto.nombre}"?`)) return

  try {
    const res = await fetch(
      `http://localhost:8000/api/admin/productos/${producto.id_producto}`,
      { method: 'DELETE' }
    )

    if (!res.ok) throw new Error()

    productos.value = productos.value.filter(
      p => p.id_producto !== producto.id_producto
    )

  } catch {
    alert('Error eliminando')
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

    const res = await fetch(
      'http://localhost:8000/api/admin/productos',
      {
        method: 'POST',
        body: formData
      }
    )

    if (!res.ok) throw new Error()

    cerrarModalNuevo()
    cargarProductos()

  } catch {
    alert('Error creando producto')
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
  margin-bottom: 15px;
}

/* BUSCADOR */
.search-container {
  margin-bottom: 15px;
}

.search-container input {
  padding: 8px;
  width: 250px;
}

/* GRID */
.productos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 15px;
}

/* CARD */
.card {
  background: white;
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

/* PRECIO */
.precio {
  font-weight: bold;
  margin: 10px 0;
}

/* BOTONES */
.acciones {
  display: flex;
  gap: 5px;
}

button {
  cursor: pointer;
}

button.danger {
  color: red;
}

/* ESTADOS */
.estado {
  padding: 20px;
}

.estado.error {
  color: red;
}

/* MODAL */
.modal {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-box {
  background: white;
  padding: 20px;
  border-radius: 10px;
  width: 300px;
}
</style>