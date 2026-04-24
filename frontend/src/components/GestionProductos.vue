<template>
  <div class="gestion-productos">
    <div class="view-header">
      <div class="header-info">
        <h1 class="view-title">👕 Gestión de productos</h1>
        <p class="view-description">Administra el catálogo de productos disponibles</p>
        <div v-if="agenteActivo" class="agente-status">
          <span class="status-dot"></span>
          <span class="status-text">🤖 Agente de precios activo</span>
        </div>
      </div>
      <button class="btn-nuevo" @click="abrirModalNuevo">
        <span>➕</span>
        <span>Nuevo producto</span>
      </button>
    </div>

    <!-- Buscador -->
    <div v-if="!cargando && !error" class="search-container">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input 
          v-model="busqueda" 
          type="text" 
          placeholder="Buscar productos por nombre, talle o color..."
          class="search-input"
        />
        <button v-if="busqueda" @click="busqueda = ''" class="clear-search">✕</button>
      </div>
      <div v-if="busqueda" class="search-results-count">
        {{ productosFiltrados.length }} resultado(s) encontrado(s)
      </div>
    </div>

    <!-- Mensajes de estado -->
    <div v-if="cargando" class="mensaje-estado">
      <div class="spinner"></div>
      <p>🔄 Cargando productos desde la base de datos...</p>
    </div>

    <div v-else-if="error" class="mensaje-estado error">
      <p>⚠️ {{ error }}</p>
      <button @click="cargarProductos" class="btn-reintentar">Reintentar</button>
    </div>

    <!-- Grid de productos -->
    <div v-else class="productos-container">
      <div v-if="busqueda && productosFiltrados.length === 0" class="sin-productos">
        <p>🔍 No se encontraron productos con "{{ busqueda }}"</p>
      </div>
      <div v-else-if="!productos || productos.length === 0" class="sin-productos">
        <p>No hay productos en la base de datos</p>
      </div>
      
      <div v-else class="productos-grid">
        <div v-for="producto in productosFiltrados" :key="producto.id_producto" class="producto-card">
        <div class="producto-imagen-container">
          <span class="producto-emoji">{{ getProductoEmoji(producto.nombre) }}</span>
        </div>
        <div class="producto-info">
          <h3 class="producto-nombre">{{ producto.nombre || 'Sin nombre' }}</h3>
          <div class="producto-detalles">
            <p v-if="producto.talles && Array.isArray(producto.talles) && producto.talles.length > 0" class="producto-talles">
              <strong>Talles:</strong> {{ producto.talles.join(', ') }}
            </p>
            <p v-if="producto.colores && Array.isArray(producto.colores) && producto.colores.length > 0" class="producto-colores">
              <strong>Colores:</strong> {{ producto.colores.join(', ') }}
            </p>
          </div>
          
          <!-- Precio normal o en edición -->
          <div v-if="productoEditando?.id_producto === producto.id_producto" class="precio-edicion">
            <span class="simbolo-peso">$</span>
            <input 
              ref="precioInput"
              v-model="precioTemporal" 
              type="number" 
              class="input-precio"
              @keyup.enter="confirmarEdicion(producto)"
              @keyup.esc="cancelarEdicion"
            />
          </div>
          <p v-else class="producto-precio">{{ formatearMoneda(producto.precio || 0) }}</p>
        </div>
        
        <!-- Acciones normales o de edición -->
        <div v-if="productoEditando?.id_producto === producto.id_producto" class="producto-acciones-edicion">
          <button class="btn-accion-sm confirm" @click="confirmarEdicion(producto)" title="Confirmar">✓</button>
          <button class="btn-accion-sm cancel" @click="cancelarEdicion" title="Cancelar">✗</button>
        </div>
        <div v-else class="producto-acciones">
          <button class="btn-accion-sm" @click="iniciarEdicion(producto)" title="Editar precio">✏️</button>
          <button class="btn-accion-sm danger" @click="eliminarProducto(producto)" title="Desactivar producto">🗑️</button>
        </div>
        </div>
      </div>
    </div>

    <!-- Modal Nuevo Producto -->
    <div v-if="mostrarModalNuevo" class="modal-overlay" @click.self="cerrarModalNuevo">
      <div class="modal-content">
        <div class="modal-header">
          <h2>➕ Nuevo Producto</h2>
          <button class="btn-cerrar" @click="cerrarModalNuevo">✕</button>
        </div>
        
        <form @submit.prevent="crearProducto" class="modal-form">
          <div class="form-group">
            <label class="form-label">Nombre *</label>
            <input 
              v-model="nuevoProducto.nombre" 
              type="text" 
              class="form-input"
              placeholder="Ej: Remera, Taza, Buzo..."
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label">Descripción</label>
            <textarea 
              v-model="nuevoProducto.descripcion" 
              class="form-textarea"
              placeholder="Descripción del producto (opcional)"
              rows="3"
            ></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Categoría</label>
              <select 
                v-model="nuevoProducto.categoria" 
                class="form-input"
              >
                <option value="">Seleccionar categoría...</option>
                <option value="Indumentaria">Indumentaria</option>
                <option value="Hogar">Hogar</option>
                <option value="Accesorios">Accesorios</option>
                <option value="Tecnología">Tecnología</option>
                <option value="Papelería">Papelería</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Orden</label>
              <input 
                v-model.number="nuevoProducto.orden_visualizacion" 
                type="number" 
                class="form-input"
                readonly
                title="El orden se asigna automáticamente al final"
              />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Imagen Mockup</label>
            <div class="file-input-container">
              <input 
                ref="fileInput"
                type="file" 
                @change="handleFileChange"
                accept="image/*"
                class="file-input"
                id="imagen-upload"
              />
              <label for="imagen-upload" class="file-input-label">
                <span class="file-icon">📁</span>
                <span>{{ archivoSeleccionado || 'Seleccionar imagen...' }}</span>
              </label>
            </div>
            <p class="file-hint">Formatos: PNG, JPG, JPEG. Máx: 2MB</p>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-cancelar" @click="cerrarModalNuevo">
              Cancelar
            </button>
            <button type="submit" class="btn btn-crear" :disabled="cargando">
              {{ cargando ? '⏳ Creando...' : '✅ Crear Producto' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Gestión de Variantes -->
    <div v-if="mostrarModalVariantes" class="modal-overlay" @click.self="cerrarModalVariantes">
      <div class="modal-content modal-variantes">
        <div class="modal-header">
          <div>
            <h2>🎨 Gestión de Variantes</h2>
            <p class="modal-subtitle">{{ productoParaVariantes?.nombre }}</p>
          </div>
          <button class="btn-cerrar" @click="cerrarModalVariantes">✕</button>
        </div>
        
        <div class="modal-body">
          <!-- Formulario para agregar variante -->
          <div class="variante-form">
            <h3 class="form-section-title">Nueva Variante</h3>
            
            <div class="form-grid">
              <!-- Atributos dinámicos (Color, Talle, etc) -->
              <div v-for="atributo in atributosDisponibles" :key="atributo.id_atributo" class="form-group">
                <label class="form-label">{{ atributo.nombre }} *</label>
                <select 
                  v-model="nuevaVariante.atributos[atributo.id_atributo]" 
                  class="form-input"
                >
                  <option v-for="valor in atributo.valores" :key="valor.id_valor" :value="valor.id_valor">
                    {{ valor.valor }}
                  </option>
                </select>
              </div>

              <!-- Precio -->
              <div class="form-group">
                <label class="form-label">Precio *</label>
                <input 
                  v-model.number="nuevaVariante.precio" 
                  type="number" 
                  class="form-input"
                  placeholder="12000"
                  min="0"
                  step="0.01"
                />
              </div>

              <!-- Stock -->
              <div class="form-group">
                <label class="form-label">Stock Actual</label>
                <input 
                  v-model.number="nuevaVariante.stock_actual" 
                  type="number" 
                  class="form-input"
                  placeholder="10"
                  min="0"
                />
              </div>

              <div class="form-group">
                <label class="form-label">Stock Mínimo</label>
                <input 
                  v-model.number="nuevaVariante.stock_minimo" 
                  type="number" 
                  class="form-input"
                  placeholder="5"
                  min="0"
                />
              </div>

              <div class="form-group">
                <label class="form-label">Stock Máximo</label>
                <input 
                  v-model.number="nuevaVariante.stock_maximo" 
                  type="number" 
                  class="form-input"
                  placeholder="100"
                  min="0"
                />
              </div>
            </div>

            <button 
              @click="agregarVariante" 
              class="btn btn-agregar"
              :disabled="cargando"
            >
              {{ cargando ? '⏳ Agregando...' : '➕ Agregar Variante' }}
            </button>
          </div>

          <!-- Lista de variantes agregadas -->
          <div v-if="variantesAgregadas.length > 0" class="variantes-lista">
            <h3 class="form-section-title">
              Variantes Agregadas ({{ variantesAgregadas.length }})
            </h3>
            
            <div class="variantes-table">
              <table>
                <thead>
                  <tr>
                    <th>SKU</th>
                    <th v-for="atributo in atributosDisponibles" :key="atributo.id_atributo">
                      {{ atributo.nombre }}
                    </th>
                    <th>Precio</th>
                    <th>Stock</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="variante in variantesAgregadas" :key="variante.id_variante">
                    <td class="sku-cell">{{ variante.sku }}</td>
                    <td v-for="atributo in atributosDisponibles" :key="atributo.id_atributo">
                      {{ variante.atributos[atributo.nombre] || '-' }}
                    </td>
                    <td class="precio-cell">${{ variante.precio.toLocaleString('es-AR') }}</td>
                    <td class="stock-cell">{{ variante.stock_actual }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div v-else class="sin-variantes">
            <p>📦 Aún no has agregado variantes</p>
            <p class="hint">Completa el formulario arriba y haz clic en "Agregar Variante"</p>
          </div>
        </div>

        <div class="modal-footer">
          <button 
            @click="cerrarModalVariantes" 
            class="btn btn-finalizar"
          >
            ✅ Finalizar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useApi } from '../composables/useApi'

const { deleteProducto, updatePrecioProducto, loading } = useApi()

const productos = ref([])
const busqueda = ref('')
const cargando = ref(false)
const error = ref(null)
const productoEditando = ref(null)
const precioTemporal = ref(null)
const precioInput = ref(null)
const agenteActivo = ref(false) // Track si el agente ya fue inicializado

// Estado del modal de nuevo producto
const mostrarModalNuevo = ref(false)
const archivoSeleccionado = ref('')
const fileInput = ref(null)
const nuevoProducto = ref({
  nombre: '',
  descripcion: '',
  categoria: '',
  imagen_mockup: '',
  area_impresion_ancho: 800,  // Valor por defecto (campos ocultos en el formulario)
  area_impresion_alto: 1000,   // Valor por defecto (campos ocultos en el formulario)
  orden_visualizacion: 0
})

// Estado del modal de variantes
const mostrarModalVariantes = ref(false)
const productoParaVariantes = ref(null)
const atributosDisponibles = ref([])
const variantesAgregadas = ref([])
const nuevaVariante = ref({
  atributos: {},
  precio: 12000,
  stock_actual: 10,
  stock_minimo: 5,
  stock_maximo: 100
})

// Productos filtrados por búsqueda
const productosFiltrados = computed(() => {
  if (!busqueda.value) {
    return productos.value
  }
  
  const query = busqueda.value.toLowerCase().trim()
  return productos.value.filter(producto => {
    // Buscar en nombre
    const nombreMatch = producto.nombre?.toLowerCase().includes(query)
    
    // Buscar en talles
    const tallesMatch = producto.talles?.some(t => t.toLowerCase().includes(query))
    
    // Buscar en colores
    const coloresMatch = producto.colores?.some(c => c.toLowerCase().includes(query))
    
    return nombreMatch || tallesMatch || coloresMatch
  })
})

onMounted(async () => {
  await cargarProductos()
})

async function cargarProductos() {
  cargando.value = true
  error.value = null
  
  try {
    console.log('🔄 Cargando productos del agente IA...')
    const response = await fetch('http://localhost:5001/productos-ia')
    
    if (!response.ok) {
      throw new Error(`Error HTTP ${response.status}`)
    }
    
    const data = await response.json()
    
    // Validar que data sea un array
    if (!Array.isArray(data)) {
      throw new Error('El agente no devolvió un array de productos')
    }
    
    // Transformar datos del agente a formato para visualización
    productos.value = data.map((item, index) => ({
      id_producto: item.id_producto || item.id || `temp-${index}`,
      nombre: item.producto || 'Sin nombre',
      talles: Array.isArray(item.talles) ? item.talles : [],
      colores: Array.isArray(item.colores) ? item.colores : [],
      precio: Number(item.precio) || 12000,
      detalle: item.detalle || ''
    }))
    
    console.log('✅ Productos cargados:', productos.value.length)
    
  } catch (err) {
    console.error('❌ Error al cargar productos:', err)
    error.value = 'Error al cargar productos del agente. Verifica que el servicio esté corriendo en http://localhost:5001'
  } finally {
    cargando.value = false
  }
}

function getProductoEmoji(nombre) {
  if (!nombre) return '📦'
  const nombreLower = nombre.toLowerCase()
  if (nombreLower.includes('remera') || nombreLower.includes('camiseta')) return '👕'
  if (nombreLower.includes('buzo') || nombreLower.includes('sudadera')) return '🧥'
  if (nombreLower.includes('taza')) return '☕'
  if (nombreLower.includes('gorra')) return '🧢'
  if (nombreLower.includes('bolso') || nombreLower.includes('tote') || nombreLower.includes('mochila')) return '👜'
  if (nombreLower.includes('cojin') || nombreLower.includes('almohadon')) return '🛋️'
  return '📦'
}

const formatearMoneda = (valor) => {
  const valorNumerico = Number(valor) || 0
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
    minimumFractionDigits: 0
  }).format(valorNumerico)
}

// ============================================
// EDICIÓN INLINE DE PRECIOS
// ============================================

function iniciarEdicion(producto) {
  console.log('✏️ Iniciando edición de:', producto.nombre)
  productoEditando.value = producto
  precioTemporal.value = producto.precio
  
  // Focus en el input después del render
  nextTick(() => {
    if (precioInput.value) {
      precioInput.value.focus()
      precioInput.value.select()
    }
  })
}

function cancelarEdicion() {
  console.log('✗ Edición cancelada')
  productoEditando.value = null
  precioTemporal.value = null
}

async function confirmarEdicion(producto) {
  const nuevoPrecio = parseFloat(precioTemporal.value)
  
  // Validar precio
  if (isNaN(nuevoPrecio) || nuevoPrecio <= 0) {
    alert('❌ El precio debe ser un número válido mayor a 0')
    return
  }
  
  // Si el precio no cambió, cancelar
  if (nuevoPrecio === producto.precio) {
    console.log('Sin cambios en el precio')
    cancelarEdicion()
    return
  }
  
  try {
    cargando.value = true
    console.log(`💰 Actualizando precio de "${producto.nombre}" a ${formatearMoneda(nuevoPrecio)}...`)
    
    // Actualizar precio en el backend FastAPI
    const response = await fetch(`http://localhost:8000/api/admin/productos/${producto.id_producto}/precio`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        precio: nuevoPrecio
      })
    })
    
    const resultado = await response.json()
    
    if (!response.ok || !resultado.success) {
      throw new Error(resultado.error || resultado.data?.error || 'Error al actualizar precio')
    }
    
    console.log('✅ Precio actualizado:', resultado.data)
    
    // Actualizar precio localmente
    producto.precio = nuevoPrecio
    
    // Mostrar notificación
    alert(`✅ Precio actualizado correctamente\n${resultado.data.variantes_actualizadas} variante(s) actualizada(s)`)
    
    // Limpiar edición
    cancelarEdicion()
    
  } catch (err) {
    console.error('❌ Error al actualizar precio:', err)
    alert(`❌ Error al actualizar precio\n\n${err.message}`)
  } finally {
    cargando.value = false
  }
}

async function eliminarProducto(producto) {
  console.log('🗑️ Intentando desactivar producto:', producto)
  
  const confirmacion = confirm(
    `¿Desactivar el producto "${producto.nombre}"?\n\n` +
    `El producto dejará de aparecer en el catálogo pero se preservarán:\n` +
    `✓ Los pedidos históricos\n` +
    `✓ Las variantes y atributos\n` +
    `✓ Toda la información del producto\n\n` +
    `Puedes reactivarlo más tarde si lo necesitas.`
  )
  
  if (!confirmacion) {
    console.log('Operación cancelada')
    return
  }
  
  try {
    cargando.value = true
    console.log('🔄 Desactivando producto...')
    
    const response = await fetch(`http://localhost:8000/api/admin/productos/${producto.id_producto}`, {
      method: 'DELETE'
    })
    
    const resultado = await response.json()
    
    if (!response.ok || !resultado.success) {
      throw new Error(resultado.error || resultado.data?.error || 'Error al desactivar producto')
    }
    
    console.log('✅ Producto desactivado:', resultado.data)
    
    const mensaje = resultado.data.variantes_desactivadas 
      ? `✅ Producto desactivado correctamente\n\n` +
        `• ${resultado.data.variantes_desactivadas} variante(s) desactivada(s)\n` +
        `• El producto no aparecerá más en el catálogo`
      : '✅ Producto desactivado correctamente'
    
    alert(mensaje)
    
    // Recargar productos
    await cargarProductos()
    
  } catch (err) {
    console.error('❌ Error al desactivar producto:', err)
    alert(`❌ Error al desactivar producto\n\n${err.message}`)
  } finally {
    cargando.value = false
  }
}

// ============================================
// CREAR NUEVO PRODUCTO
// ============================================

async function abrirModalNuevo() {
  mostrarModalNuevo.value = true
  archivoSeleccionado.value = ''
  
  // Obtener el siguiente orden disponible desde el backend
  try {
    const response = await fetch('http://localhost:8000/api/admin/productos/siguiente-orden')
    const resultado = await response.json()
    
    const siguienteOrden = resultado.success && resultado.data?.siguiente_orden 
      ? resultado.data.siguiente_orden 
      : 1
    
    // Resetear formulario con el orden correcto
    nuevoProducto.value = {
      nombre: '',
      descripcion: '',
      categoria: '',
      imagen_mockup: '',
      area_impresion_ancho: 800,
      area_impresion_alto: 1000,
      orden_visualizacion: siguienteOrden
    }
  } catch (err) {
    console.error('Error al obtener orden:', err)
    // Si falla, usar orden 1 por defecto
    nuevoProducto.value = {
      nombre: '',
      descripcion: '',
      categoria: '',
      imagen_mockup: '',
      area_impresion_ancho: 800,
      area_impresion_alto: 1000,
      orden_visualizacion: 1
    }
  }
}

function cerrarModalNuevo() {
  mostrarModalNuevo.value = false
  archivoSeleccionado.value = ''
}

function handleFileChange(event) {
  const file = event.target.files[0]
  if (!file) {
    archivoSeleccionado.value = ''
    nuevoProducto.value.imagen_mockup = ''
    return
  }
  
  // Validar tipo
  if (!file.type.startsWith('image/')) {
    alert('❌ Por favor selecciona una imagen válida (PNG, JPG, JPEG)')
    event.target.value = ''
    return
  }
  
  // Validar tamaño (2MB)
  if (file.size > 2 * 1024 * 1024) {
    alert('❌ La imagen es muy grande. Máximo 2MB')
    event.target.value = ''
    return
  }
  
  archivoSeleccionado.value = file.name
  // Por ahora, guardamos el nombre del archivo
  // En una implementación completa, subirías el archivo al servidor
  nuevoProducto.value.imagen_mockup = `/assets/mockups/${file.name}`
}

async function crearProducto() {
  if (!nuevoProducto.value.nombre.trim()) {
    alert('❌ El nombre del producto es obligatorio')
    return
  }
  
  try {
    cargando.value = true
    console.log('📦 Creando nuevo producto:', nuevoProducto.value)
    
    const response = await fetch('http://localhost:8000/api/admin/productos', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(nuevoProducto.value)
    })
    
    const resultado = await response.json()
    
    if (!response.ok || !resultado.success) {
      throw new Error(resultado.error || resultado.data?.error || 'Error al crear producto')
    }
    
    console.log('✅ Producto creado:', resultado.data)
    
    // Cerrar modal de nuevo producto
    cerrarModalNuevo()
    
    // Abrir modal de variantes
    productoParaVariantes.value = {
      id_producto: resultado.data.id_producto,
      nombre: resultado.data.nombre
    }
    await abrirModalVariantes()
    
  } catch (err) {
    console.error('❌ Error al crear producto:', err)
    alert(`❌ Error al crear producto\n\n${err.message}`)
  } finally {
    cargando.value = false
  }
}

// ============================================
// GESTIÓN DE VARIANTES
// ============================================

async function abrirModalVariantes() {
  mostrarModalVariantes.value = true
  variantesAgregadas.value = []
  
  // Cargar atributos disponibles
  try {
    const response = await fetch('http://localhost:8000/api/admin/atributos')
    const resultado = await response.json()
    
    if (resultado.success && resultado.data) {
      atributosDisponibles.value = resultado.data.atributos || []
      
      // Inicializar atributos en nuevaVariante con el primer valor de cada atributo
      const atributosIniciales = {}
      atributosDisponibles.value.forEach(atr => {
        if (atr.valores && atr.valores.length > 0) {
          atributosIniciales[atr.id_atributo] = atr.valores[0].id_valor
        }
      })
      
      nuevaVariante.value = {
        atributos: atributosIniciales,
        precio: 12000,
        stock_actual: 10,
        stock_minimo: 5,
        stock_maximo: 100
      }
    }
  } catch (err) {
    console.error('Error al cargar atributos:', err)
    alert('Error al cargar atributos disponibles')
  }
  
  // Cargar variantes existentes del producto
  await cargarVariantesExistentes()
}

async function cargarVariantesExistentes() {
  if (!productoParaVariantes.value) return
  
  try {
    const response = await fetch(
      `http://localhost:8000/api/admin/productos/${productoParaVariantes.value.id_producto}/variantes`
    )
    const resultado = await response.json()
    
    if (resultado.success && resultado.data) {
      variantesAgregadas.value = resultado.data.variantes || []
    }
  } catch (err) {
    console.error('Error al cargar variantes:', err)
  }
}

function cerrarModalVariantes() {
  mostrarModalVariantes.value = false
  productoParaVariantes.value = null
  variantesAgregadas.value = []
  
  // Recargar productos para mostrar el nuevo producto con variantes
  cargarProductos()
}

async function agregarVariante() {
  if (!productoParaVariantes.value) return
  
  // Validar que todos los atributos estén seleccionados
  const atributosRequeridos = atributosDisponibles.value.filter(a => a.valores && a.valores.length > 0)
  for (const atr of atributosRequeridos) {
    if (!nuevaVariante.value.atributos[atr.id_atributo]) {
      alert(`❌ Debes seleccionar un valor para ${atr.nombre}`)
      return
    }
  }
  
  // Validar precio
  if (!nuevaVariante.value.precio || nuevaVariante.value.precio <= 0) {
    alert('❌ El precio debe ser mayor a 0')
    return
  }
  
  try {
    cargando.value = true
    
    const response = await fetch(
      `http://localhost:8000/api/admin/productos/${productoParaVariantes.value.id_producto}/variantes`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(nuevaVariante.value)
      }
    )
    
    const resultado = await response.json()
    
    if (!response.ok || !resultado.success) {
      throw new Error(resultado.error || resultado.data?.error || 'Error al crear variante')
    }
    
    console.log('✅ Variante creada:', resultado.data)
    
    // Recargar variantes
    await cargarVariantesExistentes()
    
    // Resetear formulario manteniendo los valores por defecto
    const atributosIniciales = {}
    atributosDisponibles.value.forEach(atr => {
      if (atr.valores && atr.valores.length > 0) {
        atributosIniciales[atr.id_atributo] = atr.valores[0].id_valor
      }
    })
    
    nuevaVariante.value = {
      atributos: atributosIniciales,
      precio: nuevaVariante.value.precio, // Mantener el mismo precio
      stock_actual: 10,
      stock_minimo: 5,
      stock_maximo: 100
    }
    
  } catch (err) {
    console.error('❌ Error al crear variante:', err)
    alert(`❌ Error al crear variante\n\n${err.message}`)
  } finally {
    cargando.value = false
  }
}

function getNombreAtributo(idAtributo) {
  const atributo = atributosDisponibles.value.find(a => a.id_atributo === parseInt(idAtributo))
  return atributo ? atributo.nombre : ''
}

function getNombreValor(idAtributo, idValor) {
  const atributo = atributosDisponibles.value.find(a => a.id_atributo === parseInt(idAtributo))
  if (!atributo || !atributo.valores) return ''
  
  const valor = atributo.valores.find(v => v.id_valor === parseInt(idValor))
  return valor ? valor.valor : ''
}
</script>

<style scoped>
.gestion-productos {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* MENSAJES DE ESTADO */
.mensaje-estado {
  padding: 60px 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
}

.mensaje-estado.error {
  color: var(--color-error);
}

.mensaje-estado p {
  font-size: 1rem;
  margin: 0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--color-border);
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
  padding: 10px 24px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.btn-reintentar:hover {
  background: var(--color-primary-dark);
}

.sin-productos {
  padding: 60px 20px;
  text-align: center;
  color: var(--color-text-secondary);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  grid-column: 1 / -1;
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

.agente-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  padding: 6px 12px;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  color: #22c55e;
  font-weight: 500;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: #22c55e;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.status-text {
  display: flex;
  align-items: center;
  gap: 4px;
}

.btn-nuevo {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
  font-weight: 500;
}

.btn-nuevo:hover {
  background: var(--color-primary-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

/* BUSCADOR */
.search-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-sm);
  transition: all 0.2s;
}

.search-box:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1);
}

.search-icon {
  position: absolute;
  left: 14px;
  font-size: 1.1rem;
  color: var(--color-text-secondary);
  pointer-events: none;
}

.search-input {
  flex: 1;
  padding: 12px 40px 12px 44px;
  background: transparent;
  border: none;
  outline: none;
  font-size: 0.95rem;
  color: var(--color-text);
  font-family: inherit;
}

.search-input::placeholder {
  color: var(--color-text-secondary);
}

.clear-search {
  position: absolute;
  right: 10px;
  padding: 6px 10px;
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 1rem;
  border-radius: 4px;
  transition: all 0.2s;
}

.clear-search:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--color-text);
}

.search-results-count {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  padding-left: 4px;
}

/* CONTENEDOR DE PRODUCTOS CON SCROLL */
.productos-container {
  max-height: calc(100vh - 350px);
  overflow-y: auto;
  padding-right: 4px;
}

/* Estilos personalizados del scrollbar */
.productos-container::-webkit-scrollbar {
  width: 8px;
}

.productos-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 4px;
}

.productos-container::-webkit-scrollbar-thumb {
  background: rgba(6, 182, 212, 0.3);
  border-radius: 4px;
  transition: all 0.2s;
}

.productos-container::-webkit-scrollbar-thumb:hover {
  background: rgba(6, 182, 212, 0.5);
}

.productos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

.producto-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.producto-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow);
}

.producto-imagen-container {
  width: 100%;
  aspect-ratio: 1;
  background: rgba(6, 182, 212, 0.1);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}

.producto-emoji {
  font-size: 2.2rem;
}

.producto-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.producto-nombre {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.producto-detalles {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin: 4px 0;
}

.producto-talles,
.producto-colores {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.4;
}

.producto-talles strong,
.producto-colores strong {
  color: var(--color-text);
  font-weight: 600;
}

.producto-categoria {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  margin: 0;
}

.producto-precio {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--color-primary);
  margin: 8px 0 0 0;
}

.precio-edicion {
  display: flex;
  align-items: center;
  gap: 4px;
  margin: 8px 0 0 0;
}

.simbolo-peso {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--color-primary);
}

.input-precio {
  flex: 1;
  padding: 8px 12px;
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--color-primary);
  border: 2px solid var(--color-primary);
  border-radius: var(--radius-sm);
  background: white;
  outline: none;
  transition: all 0.2s;
  width: 100%;
}

.input-precio:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1);
}

.input-precio::-webkit-inner-spin-button,
.input-precio::-webkit-outer-spin-button {
  opacity: 1;
}

.producto-acciones {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border);
}

.producto-acciones-edicion {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border);
}

.btn-accion-sm {
  flex: 1;
  padding: 8px;
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 1.1rem;
}

.btn-accion-sm:hover {
  background: rgba(6, 182, 212, 0.1);
  border-color: var(--color-primary);
}

.btn-accion-sm.danger:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: var(--color-error);
}

.btn-accion-sm.confirm {
  background: rgba(34, 197, 94, 0.1);
  border-color: #22c55e;
  color: #22c55e;
  font-weight: bold;
}

.btn-accion-sm.confirm:hover {
  background: #22c55e;
  color: white;
  transform: scale(1.05);
}

.btn-accion-sm.cancel {
  background: rgba(239, 68, 68, 0.1);
  border-color: #ef4444;
  color: #ef4444;
  font-weight: bold;
}

.btn-accion-sm.cancel:hover {
  background: #ef4444;
  color: white;
  transform: scale(1.05);
}

/* ============================================
   MODAL NUEVO PRODUCTO
   ============================================ */

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: var(--color-surface);
  border-radius: var(--radius);
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--color-text);
}

.btn-cerrar {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  transition: all 0.2s;
}

.btn-cerrar:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.modal-form {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-label {
  font-weight: 600;
  color: var(--color-text);
  font-size: 0.9rem;
}

.form-input,
.form-textarea {
  padding: 10px 12px;
  font-size: 0.95rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-background);
  color: var(--color-text);
  outline: none;
  transition: all 0.2s;
}

.form-input:focus,
.form-textarea:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1);
}

.form-input[readonly] {
  background: rgba(100, 116, 139, 0.1);
  cursor: not-allowed;
  color: var(--color-text-secondary);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}

.btn {
  padding: 10px 20px;
  border-radius: var(--radius-sm);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  font-size: 0.95rem;
}

.btn-cancelar {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text);
}

.btn-cancelar:hover {
  background: var(--color-background);
}

.btn-crear {
  background: var(--color-primary);
  color: white;
}

.btn-crear:hover:not(:disabled) {
  background: #0891b2;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3);
}

.btn-crear:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* File input customizado */
.file-input-container {
  position: relative;
}

.file-input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.file-input-label {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  font-size: 0.95rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-background);
  color: var(--color-text);
  cursor: pointer;
  transition: all 0.2s;
}

.file-input-label:hover {
  border-color: var(--color-primary);
  background: rgba(6, 182, 212, 0.05);
}

.file-icon {
  font-size: 1.2rem;
}

.file-hint {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  margin: 4px 0 0 0;
}

/* ============================================
   MODAL GESTIÓN DE VARIANTES
   ============================================ */

.modal-variantes {
  max-width: 900px;
  max-height: 85vh;
}

.modal-subtitle {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  margin: 4px 0 0 0;
  font-weight: normal;
}

.modal-body {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.variante-form {
  background: rgba(6, 182, 212, 0.05);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 20px;
}

.form-section-title {
  margin: 0 0 16px 0;
  font-size: 1.1rem;
  color: var(--color-text);
  font-weight: 600;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.btn-agregar {
  width: 100%;
  padding: 12px 20px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.95rem;
}

.btn-agregar:hover:not(:disabled) {
  background: #0891b2;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3);
}

.btn-agregar:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.variantes-lista {
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 20px;
}

.variantes-table {
  overflow-x: auto;
}

.variantes-table table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.variantes-table th {
  background: rgba(6, 182, 212, 0.1);
  color: var(--color-text);
  font-weight: 600;
  padding: 10px 12px;
  text-align: left;
  border-bottom: 2px solid var(--color-primary);
}

.variantes-table td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text);
}

.variantes-table tr:hover {
  background: rgba(6, 182, 212, 0.05);
}

.sku-cell {
  font-family: monospace;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

.precio-cell {
  font-weight: 600;
  color: var(--color-primary);
}

.stock-cell {
  text-align: center;
  font-weight: 500;
}

.sin-variantes {
  text-align: center;
  padding: 40px 20px;
  color: var(--color-text-secondary);
}

.sin-variantes p {
  margin: 8px 0;
}

.sin-variantes .hint {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  opacity: 0.7;
}

.btn-finalizar {
  padding: 12px 32px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.95rem;
}

.btn-finalizar:hover {
  background: #059669;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}
</style>
