<template>
  <div class="gestion-cupones">
    <!-- Header con botones de acción -->
    <div class="header-cupones">
      <h2>🎟️ Gestión de Cupones</h2>
      <div class="acciones-header">
        <button @click="clickBotonIA" class="btn-ia" :disabled="esCargandoIA">
          <span v-if="esCargandoIA" class="btn-ia-pensando">
            <span class="dot-pulse"></span> Agente analizando datos
          </span>
          <span v-else-if="todasPropuestas.length > 0">🤖 Propuesta del agente</span>
          <span v-else>🤖 Proponer Cupones con IA</span>
        </button>
        <button @click="abrirFormulario(null)" class="btn-nuevo">
          ➕ Crear Cupón
        </button>
      </div>
    </div>

    <!-- Estadísticas rápidas -->
    <div class="estadisticas-rapidas" v-if="estadisticas">
      <div class="stat-card">
        <div class="stat-valor">{{ estadisticas.ultimo_mes?.total_pedidos || 0 }}</div>
        <div class="stat-label">Pedidos (30 días)</div>
      </div>
      <div class="stat-card">
        <div class="stat-valor">${{ formatearPrecio(estadisticas.ultimo_mes?.ticket_promedio || 0) }}</div>
        <div class="stat-label">Ticket Promedio</div>
      </div>
      <div class="stat-card">
        <div class="stat-valor">{{ estadisticas.clientes?.nuevos || 0 }}</div>
        <div class="stat-label">Clientes Nuevos</div>
      </div>
      <div class="stat-card">
        <div class="stat-valor">{{ estadisticas.clientes?.recurrentes || 0 }}</div>
        <div class="stat-label">Clientes Recurrentes</div>
      </div>
    </div>

    <!-- Lista de cupones -->
    <div class="lista-cupones">
      <div class="filtros">
        <label class="stat-valor">
          <input type="checkbox" v-model="mostrarInactivos" @change="cargarCupones(true)">
          Mostrar cupones inactivos
        </label>
        <div class="buscador-wrapper">
          <span class="buscador-icon">🔍</span>
          <input
            v-model="busqueda"
            type="text"
            class="buscador-input"
            placeholder="Buscar cupón por código o descripción..."
          >
          <button v-if="busqueda" @click="busqueda = ''" class="buscador-clear">✕</button>
        </div>
      </div>

      <div v-if="cargando" class="loading">Cargando cupones...</div>

      <div v-else-if="cuponesFiltrados.length === 0 && busqueda" class="empty-state">
        <p>No se encontraron cupones para "{{ busqueda }}"</p>
      </div>
      
      <div v-else-if="cupones.length === 0" class="empty-state">
        <p>No hay cupones disponibles</p>
        <button @click="consultarIA" class="btn-ia-secondary">
          🤖 ¿Quieres que el agente sugiera cupones?
        </button>
      </div>

      <div v-else class="cupones-grid">
        <div v-for="cupon in cuponesFiltrados" :key="cupon.id_cupon" 
             :class="['cupon-card', { inactivo: !cupon.activo }]">
          
          <div class="cupon-header">
            <div class="codigo-cupon">{{ cupon.codigo }}</div>
            <div class="descuento-badge">{{ cupon.descuento_porcentaje }}% OFF</div>
          </div>

          <p class="cupon-descripcion">{{ cupon.descripcion }}</p>

          <div class="cupon-stats">
            <div class="stat">
              <span class="label">Usos:</span>
              <span class="valor">
                {{ cupon.usos_actuales }} 
                <span v-if="cupon.usos_maximos">/ {{ cupon.usos_maximos }}</span>
                <span v-else>/ ∞</span>
              </span>
            </div>
            <div class="stat" v-if="cupon.fecha_expiracion">
              <span class="label">Expira:</span>
              <span class="valor">{{ formatearFecha(cupon.fecha_expiracion) }}</span>
            </div>
            <div class="stat" v-else>
              <span class="label">Vigencia:</span>
              <span class="valor">Permanente</span>
            </div>
          </div>

          <div class="cupon-acciones">
            <button @click="abrirFormulario(cupon)" class="btn-editar">
              ✏️ Editar
            </button>
            <button @click="toggleEstado(cupon)" 
                    :class="['btn-toggle', cupon.activo ? 'desactivar' : 'activar']">
              {{ cupon.activo ? '⏸️ Desactivar' : '▶️ Activar' }}
            </button>
            <button @click="eliminarCupon(cupon)" class="btn-eliminar">
              🗑️ Eliminar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal propuestas IA automático -->
    <div v-if="mostrarModalPropuestas" class="modal-overlay" @click.self="mostrarModalPropuestas = false">
      <div class="modal-content modal-propuestas">
        <div class="modal-header">
          <h3>💡 Propuestas del Agente IA</h3>
          <button @click="mostrarModalPropuestas = false" class="btn-cerrar">✕</button>
        </div>
        <div class="modal-propuestas-body">
          <div v-if="esCargandoIA" class="propuestas-pensando">
            <div class="spinner-ia"></div>
            <p>El agente está analizando datos y generando propuestas de cupones...</p>
            <small>Esto puede tardar unos segundos</small>
          </div>
          <div v-else-if="todasPropuestas.length === 0" class="propuestas-pensando">
            <p>⚠️ No se pudieron generar propuestas en este momento.</p>
            <small>¿Ollama está corriendo?</small>
          </div>
          <div v-else>
            <p class="analisis-ia-modal">{{ analisisActivo }}</p>
            <div class="carousel-wrapper">
              <button class="carousel-arrow left" @click="scrollCarousel('modal', -1)">&#8249;</button>
              <div class="carousel-track" ref="trackModal">
                <div v-for="(propuesta, index) in todasPropuestas" :key="index" class="propuesta-card">
                  <div class="propuesta-badge">IA Sugiere</div>
                  <h4>{{ propuesta.codigo }}</h4>
                  <p class="propuesta-desc">{{ propuesta.descripcion }}</p>
                  <div class="propuesta-detalles">
                    <span class="descuento">{{ propuesta.descuento }}% OFF</span>
                    <span class="duracion">{{ propuesta.duracion_dias }} días</span>
                  </div>
                  <p class="propuesta-objetivo">🎯 {{ propuesta.objetivo }}</p>
                  <button @click="crearDesdePropuesta(propuesta)" class="btn-aplicar">
                    ✓ Crear Este Cupón
                  </button>
                </div>
              </div>
              <button class="carousel-arrow right" @click="scrollCarousel('modal', 1)">&#8250;</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de formulario -->
    <div v-if="mostrarFormulario" class="modal-overlay" @click.self="cerrarFormulario">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ cuponEditar ? 'Editar Cupón' : 'Crear Cupón Nuevo' }}</h3>
          <button @click="cerrarFormulario" class="btn-cerrar">✕</button>
        </div>

        <form @submit.prevent="guardarCupon" class="form-cupon">
          <div class="form-group">
            <label>Código del Cupón *</label>
            <input 
              v-model="formulario.codigo" 
              type="text"
              :disabled="!!cuponEditar"
              placeholder="VERANO2026"
              pattern="[A-Z0-9]+"
              maxlength="15"
              required
            >
            <small>Solo mayúsculas y números, sin espacios</small>
          </div>

          <div class="form-group">
            <label>Descripción *</label>
            <input 
              v-model="formulario.descripcion" 
              type="text"
              placeholder="Descuento de verano"
              maxlength="100"
              required
            >
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Descuento (%) *</label>
              <input 
                v-model.number="formulario.descuento_porcentaje" 
                type="number"
                min="1"
                max="99"
                step="0.1"
                required
              >
            </div>

            <div class="form-group">
              <label>Usos Máximos</label>
              <input 
                v-model.number="formulario.usos_maximos" 
                type="number"
                min="1"
                placeholder="Ilimitado"
              >
            </div>
          </div>

          <div class="form-group">
            <label>Fecha de Expiración</label>
            <input 
              v-model="formulario.fecha_expiracion" 
              type="date"
              :min="fechaMinima"
            >
            <small>Dejar vacío para cupón permanente</small>
          </div>

          <div class="form-actions">
            <button type="button" @click="cerrarFormulario" class="btn-cancelar">
              Cancelar
            </button>
            <button type="submit" class="btn-guardar" :disabled="guardando">
              {{ guardando ? 'Guardando...' : 'Guardar Cupón' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <!-- Toasts -->
  <div class="toast-container">
    <transition-group name="toast">
      <div
        v-for="t in toasts"
        :key="t.id"
        :class="['toast', t.tipo]"
      >
        <span class="toast-icon">{{ t.tipo === 'exito' ? '✅' : t.tipo === 'error' ? '❌' : '⚠️' }}</span>
        <span class="toast-msg">{{ t.msg }}</span>
      </div>
    </transition-group>
  </div>
</template>

<script>
//import { useApi } from '@/composables/useApi.js'
import { useApi } from '../composables/useApi.js'

export default {
  name: 'GestionCupones',

  setup() {
    const { get, post, put, del } = useApi()
    return { get, post, put, del }
  },

  props: {
    propuestasExternas: { type: Array, default: () => [] },
    analisisExterno: { type: String, default: '' },
    cargandoIAExterno: { type: Boolean, default: false }
  },
  
  data() {
    return {
      cupones: [],
      estadisticas: null,
      propuestasIA: [],
      analisisIA: '',
      cargando: false,
      cargandoIA: false,
      guardando: false,
      mostrarInactivos: false,
      mostrarFormulario: false,
      mostrarModalPropuestas: false,
      cuponEditar: null,
      busqueda: '',
      toasts: [],
      cuponesYaCargados: false,
      estadisticasYaCargadas: false,
      formulario: {
        codigo: '',
        descripcion: '',
        descuento_porcentaje: 10,
        usos_maximos: null,
        fecha_expiracion: ''
      }
    }
  },

  computed: {
    fechaMinima() {
      return new Date().toISOString().split('T')[0]
    },
    todasPropuestas() {
      return this.propuestasExternas.length > 0 ? this.propuestasExternas : this.propuestasIA
    },
    analisisActivo() {
      return this.analisisExterno || this.analisisIA
    },
    esCargandoIA() {
      return this.cargandoIAExterno || this.cargandoIA
    },
    cuponesFiltrados() {
      if (!this.busqueda.trim()) return this.cupones
      const q = this.busqueda.toLowerCase()
      return this.cupones.filter(c =>
        c.codigo.toLowerCase().includes(q) ||
        (c.descripcion && c.descripcion.toLowerCase().includes(q))
      )
    }
  },

  mounted() {
    this.cargarCupones()
    this.cargarEstadisticas()
  },

  methods: {

    // =========================
    // 📦 CUPONES
    // =========================
    async cargarCupones(forzarRecarga = false) {
      if (this.cuponesYaCargados && !forzarRecarga) return

      this.cargando = true
      try {
        const data = await this.get(`/admin/cupones?incluir_inactivos=${this.mostrarInactivos}`)

        this.cupones = data.cupones || data || []
        this.cuponesYaCargados = true

      } catch (error) {
        console.error(error)
        this.mostrarToast('Error al cargar cupones', 'error')
      } finally {
        this.cargando = false
      }
    },

    async cargarEstadisticas(forzarRecarga = false) {
      if (this.estadisticasYaCargadas && !forzarRecarga) return

      try {
        const data = await this.get('/admin/estadisticas')
        this.estadisticas = data.estadisticas || data
        this.estadisticasYaCargadas = true
      } catch (error) {
        console.error(error)
      }
    },

    // =========================
    // 🤖 IA
    // =========================
    clickBotonIA() {
      if (this.todasPropuestas.length > 0) {
        this.mostrarModalPropuestas = true
      } else {
        this.consultarIA()
      }
    },

    async consultarIA() {
      this.cargandoIA = true
      this.propuestasIA = []

      try {
        const data = await this.post('/admin/cupones/proponer')

        if (data?.propuesta) {
          this.propuestasIA = data.propuesta.cupones || []
          this.analisisIA = data.propuesta.analisis || ''
          this.estadisticas = data.estadisticas
          this.estadisticasYaCargadas = true
        } else {
          this.mostrarToast('No se pudieron generar propuestas', 'advertencia')
        }

      } catch (error) {
        console.error(error)
        this.mostrarToast('Error al consultar IA', 'error')
      } finally {
        this.cargandoIA = false
      }
    },

    crearDesdePropuesta(propuesta) {
      this.mostrarModalPropuestas = false

      this.$nextTick(() => {
        const fecha = new Date()
        fecha.setDate(fecha.getDate() + propuesta.duracion_dias)

        this.formulario = {
          codigo: propuesta.codigo,
          descripcion: propuesta.descripcion,
          descuento_porcentaje: propuesta.descuento,
          usos_maximos: 100,
          fecha_expiracion: fecha.toISOString().split('T')[0]
        }

        this.cuponEditar = null
        this.mostrarFormulario = true
      })
    },

    // =========================
    // 💾 CRUD
    // =========================
    async guardarCupon() {
      this.guardando = true

      try {
        const payload = {
          ...this.formulario,
          usos_maximos: this.formulario.usos_maximos || null,
          fecha_expiracion: this.formulario.fecha_expiracion || null
        }

        if (this.cuponEditar) {
          await this.put(`/admin/cupones/${this.cuponEditar.id_cupon}`, payload)
        } else {
          await this.post('/admin/cupones', payload)
        }

        this.mostrarToast('Cupón guardado', 'exito')
        this.cerrarFormulario()
        this.cargarCupones(true)
        this.propuestasIA = []

      } catch (error) {
        console.error(error)
        this.mostrarToast(error.message || 'Error al guardar cupón', 'error')
      } finally {
        this.guardando = false
      }
    },

    async toggleEstado(cupon) {
      try {
        await this.put(`/admin/cupones/${cupon.id_cupon}`, {
          activo: !cupon.activo
        })

        this.cargarCupones(true)

      } catch (error) {
        this.mostrarToast('Error al actualizar estado', 'error')
      }
    },

    async eliminarCupon(cupon) {
      if (!confirm(`¿Eliminar ${cupon.codigo}?`)) return

      try {
        await this.del(`/admin/cupones/${cupon.id_cupon}`)
        this.mostrarToast('Cupón eliminado', 'exito')
        this.cargarCupones(true)

      } catch (error) {
        this.mostrarToast('Error al eliminar cupón', 'error')
      }
    },

    // =========================
    // UI
    // =========================
    abrirFormulario(cupon) {
      if (cupon) {
        this.cuponEditar = cupon
        this.formulario = {
          codigo: cupon.codigo,
          descripcion: cupon.descripcion,
          descuento_porcentaje: cupon.descuento_porcentaje,
          usos_maximos: cupon.usos_maximos,
          fecha_expiracion: cupon.fecha_expiracion?.split('T')[0] || ''
        }
      } else {
        this.cuponEditar = null
        this.formulario = {
          codigo: '',
          descripcion: '',
          descuento_porcentaje: 10,
          usos_maximos: null,
          fecha_expiracion: ''
        }
      }
      this.mostrarFormulario = true
    },

    cerrarFormulario() {
      this.mostrarFormulario = false
      this.cuponEditar = null
    },

    mostrarToast(msg, tipo = 'info') {
      const id = Date.now()
      this.toasts.push({ id, msg, tipo })
      setTimeout(() => {
        this.toasts = this.toasts.filter(t => t.id !== id)
      }, 3500)
    },

    formatearFecha(f) {
      return new Date(f).toLocaleDateString('es-AR')
    },

    formatearPrecio(p) {
      return p.toLocaleString('es-AR')
    },

    scrollCarousel(which, direction) {
      const refs = { modal: 'trackModal' }
      const el = this.$refs[refs[which]]
      if (el) el.scrollBy({ left: direction * 340, behavior: 'smooth' })
    }
  }
}
</script>

<style scoped>
.gestion-cupones {
  padding: 14px;
  max-width: 1400px;
  margin: 0 auto;
}

/* Header */
.header-cupones {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.header-cupones h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.acciones-header {
  display: flex;
  gap: 8px;
}

.btn-ia, .btn-nuevo {
  padding: 7px 14px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-ia {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-ia:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-ia:disabled {
  opacity: 0.75;
  cursor: wait;
}

.btn-ia-pensando {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dot-pulse {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: white;
  display: inline-block;
  animation: dotPulse 1.2s ease-in-out infinite;
}

@keyframes dotPulse {
  0%, 100% { opacity: 0.3; transform: scale(0.8); }
  50%       { opacity: 1;   transform: scale(1.2); }
}

.btn-nuevo {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.btn-nuevo:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(245, 87, 108, 0.4);
}

/* Estadísticas */
.estadisticas-rapidas {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px;
  margin-bottom: 18px;
}

.stat-card {
  background: white;
  padding: 14px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-valor {
  font-size: 22px;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 11px;
  color: #666;
  font-weight: 500;
}

/* Propuestas IA */
.propuestas-ia {
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  border: 2px solid #667eea;
  border-radius: 8px;
  padding: 14px;
  margin-bottom: 18px;
}

.propuestas-header {
  margin-bottom: 14px;
}

.propuestas-header h3 {
  font-size: 14px;
  margin: 0 0 7px 0;
  color: #667eea;
}

.analisis-ia {
  color: #555;
  font-size: 11px;
  margin: 0;
  line-height: 1.6;
}

.propuestas-grid {
  display: flex;
  gap: 15px;
}

.propuesta-card {
  background: white;
  padding: 14px;
  border-radius: 7px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  position: relative;
  border: 2px solid #667eea;
  min-width: 196px;
  max-width: 196px;
  flex-shrink: 0;
}

.propuesta-badge {
  position: absolute;
  top: -7px;
  right: 7px;
  background: #667eea;
  color: white;
  padding: 3px 8px;
  border-radius: 20px;
  font-size: 9px;
  font-weight: 600;
}

.propuesta-card h4 {
  font-size: 14px;
  margin: 0 0 7px 0;
  color: #333;
  font-family: 'Courier New', monospace;
}

.propuesta-desc {
  color: #666;
  font-size: 10px;
  margin: 0 0 8px 0;
}

.propuesta-detalles {
  display: flex;
  gap: 7px;
  margin-bottom: 8px;
}

.propuesta-detalles span {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
}

.descuento {
  background: #4ade80;
  color: white;
}

.duracion {
  background: #f0f0f0;
  color: #666;
}

.propuesta-objetivo {
  font-size: 10px;
  color: #555;
  margin: 0 0 10px 0;
  font-style: italic;
}

.btn-aplicar {
  width: 100%;
  padding: 7px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-aplicar:hover {
  background: #5568d3;
  transform: scale(1.02);
}

/* Lista de cupones */
.lista-cupones {
  background: white;
  padding: 14px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  max-height: calc(100vh - 240px);
  overflow-y: auto;
}

.filtros {
  margin-bottom: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}

.filtros label {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 11px;
}

.buscador-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  max-width: 252px;
}

.buscador-icon {
  position: absolute;
  left: 8px;
  font-size: 11px;
  pointer-events: none;
}

.buscador-input {
  width: 100%;
  padding: 6px 22px 6px 26px;
  border: 2px solid #e0e0e0;
  border-radius: 14px;
  font-size: 11px;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.buscador-input:focus {
  outline: none;
  border-color: #667eea;
}

.buscador-clear {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  cursor: pointer;
  color: #999;
  font-size: 14px;
  padding: 0;
  line-height: 1;
}

.buscador-clear:hover {
  color: #333;
}

.loading, .empty-state {
  text-align: center;
  padding: 28px;
  color: #999;
  font-size: 11px;
}

.btn-ia-secondary {
  margin-top: 10px;
  padding: 8px 17px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  font-size: 11px;
}

/* Carousel */
.carousel-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
}

.carousel-track {
  display: flex;
  gap: 11px;
  overflow-x: auto;
  scroll-behavior: smooth;
  padding: 6px 3px 8px;
  flex: 1;
  scrollbar-width: none;
}

.carousel-track::-webkit-scrollbar {
  display: none;
}

.carousel-arrow {
  flex-shrink: 0;
  width: 25px;
  height: 25px;
  border-radius: 50%;
  border: 2px solid #667eea;
  background: white;
  color: #667eea;
  font-size: 15px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  box-shadow: 0 2px 6px rgba(0,0,0,0.12);
  z-index: 1;
}

.carousel-arrow:hover {
  background: #667eea;
  color: white;
  transform: scale(1.1);
}

/* Cupones y propuestas: ancho fijo en carousel */
.cupones-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  padding-right: 4px;
}

.cupon-card {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 7px;
  padding: 14px;
  transition: all 0.3s;
}

/* Ancho fijo solo para cards en carousel */
.carousel-track .cupon-card,
.carousel-track .propuesta-card {
  min-width: 210px;
  max-width: 210px;
  flex-shrink: 0;
}

.cupon-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  transform: translateY(-2px);
}

.cupon-card.inactivo {
  opacity: 0.5;
  background: #f5f5f5;
}

.cupon-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.codigo-cupon {
  font-size: 14px;
  font-weight: 700;
  font-family: 'Courier New', monospace;
  color: #333;
}

.descuento-badge {
  background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
  color: white;
  padding: 4px 8px;
  border-radius: 14px;
  font-weight: 700;
  font-size: 10px;
}

.cupon-descripcion {
  color: #666;
  font-size: 10px;
  margin: 0 0 10px 0;
  min-height: 28px;
}

.cupon-stats {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 10px;
  padding: 8px;
  background: #f8f8f8;
  border-radius: 4px;
}

.cupon-stats .stat {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
}

.cupon-stats .label {
  color: #666;
  font-weight: 500;
}

.cupon-stats .valor {
  color: #333;
  font-weight: 600;
}

.cupon-acciones {
  display: flex;
  gap: 6px;
  margin-top: 10px;
}

.cupon-acciones button {
  flex: 1;
  padding: 6px;
  border: none;
  border-radius: 4px;
  font-size: 9px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-editar {
  background: #3b82f6;
  color: white;
}

.btn-editar:hover {
  background: #2563eb;
}

.btn-toggle {
  color: white;
}

.btn-toggle.desactivar {
  background: #f59e0b;
}

.btn-toggle.activar {
  background: #10b981;
}

.btn-eliminar {
  background: #ef4444;
  color: white;
}

.btn-eliminar:hover {
  background: #dc2626;
}

/* Modal propuestas IA */
.modal-propuestas {
  max-width: 546px;
  width: 100%;
}

.modal-propuestas-body {
  padding: 14px;
}

.propuestas-pensando {
  text-align: center;
  padding: 28px 14px;
  color: #555;
}

.propuestas-pensando p {
  font-size: 13px;
  margin: 11px 0 4px;
}

.propuestas-pensando small {
  color: #999;
  font-size: 10px;
}

.analisis-ia-modal {
  color: #555;
  font-size: 11px;
  margin: 0 0 11px 0;
  line-height: 1.6;
  padding: 7px 10px;
  background: #f8f8ff;
  border-left: 3px solid #667eea;
  border-radius: 4px;
}

.spinner-ia {
  width: 34px;
  height: 34px;
  border: 3px solid #e0e0e0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

/* El formulario siempre por encima del modal de propuestas */
.modal-overlay:has(.form-cupon) {
  z-index: 1001;
}

.modal-content {
  background: white;
  border-radius: 8px;
  max-width: 420px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px;
  border-bottom: 2px solid #f0f0f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 14px;
}

.btn-cerrar {
  background: none;
  border: none;
  font-size: 17px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 21px;
  height: 21px;
}

.btn-cerrar:hover {
  color: #333;
}

.form-cupon {
  padding: 14px;
}

.form-group {
  margin-bottom: 14px;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 6px;
  color: #333;
  font-size: 11px;
}

.form-group input {
  width: 100%;
  padding: 7px;
  border: 2px solid #e0e0e0;
  border-radius: 4px;
  font-size: 11px;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.form-group input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.form-group small {
  display: block;
  margin-top: 4px;
  color: #999;
  font-size: 9px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.form-actions {
  display: flex;
  gap: 8px;
  margin-top: 18px;
}

.form-actions button {
  flex: 1;
  padding: 8px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  font-size: 11px;
}

.btn-cancelar {
  background: #e0e0e0;
  color: #666;
}

.btn-cancelar:hover {
  background: #d0d0d0;
}

.btn-guardar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-guardar:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-guardar:disabled {
  opacity: 0.6;
  cursor: wait;
}

@media (max-width: 768px) {
  .acciones-header {
    flex-direction: column;
    width: 100%;
  }

  .acciones-header button {
    width: 100%;
  }

  .estadisticas-rapidas {
    grid-template-columns: repeat(2, 1fr);
  }

  .cupones-grid {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}

/* Toasts */
.toast-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  display: flex;
  flex-direction: column-reverse;
  gap: 10px;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 18px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  color: white;
  box-shadow: 0 4px 16px rgba(0,0,0,0.2);
  min-width: 240px;
  max-width: 360px;
}

.toast.exito    { background: #16a34a; }
.toast.error    { background: #dc2626; }
.toast.advertencia { background: #d97706; }
.toast.info     { background: #2563eb; }

.toast-icon { font-size: 16px; flex-shrink: 0; }

.toast-enter-active { animation: toastIn 0.3s ease; }
.toast-leave-active { animation: toastIn 0.25s ease reverse; }

@keyframes toastIn {
  from { opacity: 0; transform: translateX(60px); }
  to   { opacity: 1; transform: translateX(0); }
}
</style>
