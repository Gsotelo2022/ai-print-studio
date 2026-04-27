<template>
  <div class="gestion-cupones">
    <!-- Header con botones de acción -->
    <div class="header-cupones">
      <h2>🎟️ Gestión de Cupones</h2>
      <div class="acciones-header">
        <button @click="consultarIA" class="btn-ia" :disabled="cargandoIA">
          <span v-if="!cargandoIA">🤖 Proponer Cupones con IA</span>
          <span v-else>⏳ Analizando...</span>
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

    <!-- Propuestas de IA -->
    <div v-if="propuestasIA && propuestasIA.length > 0" class="propuestas-ia">
      <div class="propuestas-header">
        <h3>💡 Propuestas Inteligentes</h3>
        <p class="analisis-ia">{{ analisisIA }}</p>
      </div>
      <div class="propuestas-grid">
        <div v-for="(propuesta, index) in propuestasIA" :key="index" class="propuesta-card">
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
    </div>

    <!-- Lista de cupones -->
    <div class="lista-cupones">
      <div class="filtros">
        <label>
          <input type="checkbox" v-model="mostrarInactivos" @change="cargarCupones">
          Mostrar cupones inactivos
        </label>
      </div>

      <div v-if="cargando" class="loading">Cargando cupones...</div>
      
      <div v-else-if="cupones.length === 0" class="empty-state">
        <p>No hay cupones disponibles</p>
        <button @click="consultarIA" class="btn-ia-secondary">
          🤖 ¿Quieres que el agente sugiera cupones?
        </button>
      </div>

      <div v-else class="cupones-grid">
        <div v-for="cupon in cupones" :key="cupon.id_cupon" 
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
</template>

<script>
export default {
  name: 'GestionCupones',
  
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
      cuponEditar: null,
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
    }
  },

  mounted() {
    this.cargarCupones()
    this.cargarEstadisticas()
  },

  methods: {
    async cargarCupones() {
      this.cargando = true
      try {
        const response = await fetch(
          `http://localhost:5003/api/cupones?incluir_inactivos=${this.mostrarInactivos}`
        )
        const data = await response.json()
        if (data.success) {
          this.cupones = data.cupones
        }
      } catch (error) {
        console.error('Error cargando cupones:', error)
        alert('Error al cargar cupones')
      } finally {
        this.cargando = false
      }
    },

    async cargarEstadisticas() {
      try {
        const response = await fetch('http://localhost:5003/api/estadisticas')
        const data = await response.json()
        if (data.success) {
          this.estadisticas = data.estadisticas
        }
      } catch (error) {
        console.error('Error cargando estadísticas:', error)
      }
    },

    async consultarIA() {
      this.cargandoIA = true
      this.propuestasIA = []
      
      try {
        const response = await fetch('http://localhost:5003/api/cupones/proponer', {
          method: 'POST'
        })
        const data = await response.json()
        
        if (data.success && data.propuesta) {
          this.propuestasIA = data.propuesta.cupones || []
          this.analisisIA = data.propuesta.analisis || ''
          this.estadisticas = data.estadisticas
        } else {
          alert(data.mensaje || 'No se pudieron generar propuestas. ¿Ollama está corriendo?')
        }
      } catch (error) {
        console.error('Error consultando IA:', error)
        alert('Error al consultar al agente IA')
      } finally {
        this.cargandoIA = false
      }
    },

    crearDesdePropuesta(propuesta) {
      const fechaExpiracion = new Date()
      fechaExpiracion.setDate(fechaExpiracion.getDate() + propuesta.duracion_dias)
      
      this.formulario = {
        codigo: propuesta.codigo,
        descripcion: propuesta.descripcion,
        descuento_porcentaje: propuesta.descuento,
        usos_maximos: 100,
        fecha_expiracion: fechaExpiracion.toISOString().split('T')[0]
      }
      
      this.cuponEditar = null
      this.mostrarFormulario = true
    },

    abrirFormulario(cupon) {
      if (cupon) {
        this.cuponEditar = cupon
        this.formulario = {
          codigo: cupon.codigo,
          descripcion: cupon.descripcion,
          descuento_porcentaje: cupon.descuento_porcentaje,
          usos_maximos: cupon.usos_maximos,
          fecha_expiracion: cupon.fecha_expiracion ? cupon.fecha_expiracion.split('T')[0] : ''
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

    async guardarCupon() {
      this.guardando = true
      
      try {
        const url = this.cuponEditar
          ? `http://localhost:5003/api/cupones/${this.cuponEditar.id_cupon}`
          : 'http://localhost:5003/api/cupones'
        
        const method = this.cuponEditar ? 'PUT' : 'POST'
        
        // Preparar datos
        const datos = { ...this.formulario }
        if (!datos.usos_maximos) datos.usos_maximos = null
        if (!datos.fecha_expiracion) datos.fecha_expiracion = null
        
        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(datos)
        })
        
        const result = await response.json()
        
        if (response.ok && result.success) {
          alert(result.mensaje)
          this.cerrarFormulario()
          this.cargarCupones()
          this.propuestasIA = [] // Limpiar propuestas después de crear
        } else {
          alert(result.mensaje || 'Error al guardar cupón')
        }
      } catch (error) {
        console.error('Error guardando cupón:', error)
        alert('Error al guardar cupón')
      } finally {
        this.guardando = false
      }
    },

    async toggleEstado(cupon) {
      const nuevoEstado = !cupon.activo
      
      try {
        const response = await fetch(
          `http://localhost:5003/api/cupones/${cupon.id_cupon}`,
          {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ activo: nuevoEstado })
          }
        )
        
        const result = await response.json()
        
        if (response.ok && result.success) {
          this.cargarCupones()
        } else {
          alert('Error al actualizar estado')
        }
      } catch (error) {
        console.error('Error:', error)
        alert('Error al actualizar estado')
      }
    },

    async eliminarCupon(cupon) {
      if (!confirm(`¿Eliminar el cupón ${cupon.codigo}?`)) return
      
      try {
        const response = await fetch(
          `http://localhost:5003/api/cupones/${cupon.id_cupon}`,
          { method: 'DELETE' }
        )
        
        const result = await response.json()
        
        if (response.ok && result.success) {
          alert('Cupón eliminado')
          this.cargarCupones()
        } else {
          alert('Error al eliminar cupón')
        }
      } catch (error) {
        console.error('Error:', error)
        alert('Error al eliminar cupón')
      }
    },

    formatearFecha(fecha) {
      return new Date(fecha).toLocaleDateString('es-AR')
    },

    formatearPrecio(precio) {
      return precio.toLocaleString('es-AR', { minimumFractionDigits: 0 })
    }
  }
}
</script>

<style scoped>
.gestion-cupones {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

/* Header */
.header-cupones {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.header-cupones h2 {
  font-size: 26px;
  font-weight: 600;
  margin: 0;
}

.acciones-header {
  display: flex;
  gap: 12px;
}

.btn-ia, .btn-nuevo {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
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
  opacity: 0.6;
  cursor: wait;
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
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 25px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-valor {
  font-size: 32px;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

/* Propuestas IA */
.propuestas-ia {
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  border: 2px solid #667eea;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 25px;
}

.propuestas-header {
  margin-bottom: 20px;
}

.propuestas-header h3 {
  font-size: 20px;
  margin: 0 0 10px 0;
  color: #667eea;
}

.analisis-ia {
  color: #555;
  font-size: 14px;
  margin: 0;
  line-height: 1.6;
}

.propuestas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 15px;
}

.propuesta-card {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  position: relative;
  border: 2px solid #667eea;
}

.propuesta-badge {
  position: absolute;
  top: -10px;
  right: 10px;
  background: #667eea;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.propuesta-card h4 {
  font-size: 20px;
  margin: 0 0 10px 0;
  color: #333;
  font-family: 'Courier New', monospace;
}

.propuesta-desc {
  color: #666;
  font-size: 14px;
  margin: 0 0 12px 0;
}

.propuesta-detalles {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}

.propuesta-detalles span {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
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
  font-size: 13px;
  color: #555;
  margin: 0 0 15px 0;
  font-style: italic;
}

.btn-aplicar {
  width: 100%;
  padding: 10px;
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
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.filtros {
  margin-bottom: 20px;
}

.filtros label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
}

.loading, .empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
}

.btn-ia-secondary {
  margin-top: 15px;
  padding: 12px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.cupones-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.cupon-card {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  padding: 20px;
  transition: all 0.3s;
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
  margin-bottom: 12px;
}

.codigo-cupon {
  font-size: 20px;
  font-weight: 700;
  font-family: 'Courier New', monospace;
  color: #333;
}

.descuento-badge {
  background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 700;
  font-size: 14px;
}

.cupon-descripcion {
  color: #666;
  font-size: 14px;
  margin: 0 0 15px 0;
  min-height: 40px;
}

.cupon-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 15px;
  padding: 12px;
  background: #f8f8f8;
  border-radius: 6px;
}

.cupon-stats .stat {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
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
  gap: 8px;
  margin-top: 15px;
}

.cupon-acciones button {
  flex: 1;
  padding: 8px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
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

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
}

.btn-cerrar {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 30px;
  height: 30px;
}

.btn-cerrar:hover {
  color: #333;
}

.form-cupon {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
  font-size: 14px;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
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
  margin-top: 5px;
  color: #999;
  font-size: 12px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 25px;
}

.form-actions button {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  font-size: 15px;
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
</style>
