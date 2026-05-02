// ============================================
// useApi.js - Composable para llamadas al backend
// ============================================
// Un "composable" en Vue 3 es una función reutilizable que encapsula
// lógica. En este caso, encapsula cómo hablar con el backend PHP.
//
// ¿Por qué? Para no repetir fetch() + manejo de errores en cada componente.
// Todos los componentes importan useApi() y usan sus funciones.

import { ref } from 'vue'

export function useApi() {
  // ref() crea una variable reactiva. Cuando cambia,
  // Vue actualiza automáticamente la UI.
  const loading = ref(false)
  const error = ref(null)

  // Función genérica para hacer peticiones POST al backend
  async function post(url, data) {
    loading.value = true
    error.value = null

    try {
      // fetch() es la API nativa del navegador para hacer peticiones HTTP.
      // Es el equivalente a cURL en PHP pero del lado del cliente.
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // JSON.stringify convierte un objeto JS a texto JSON
        // (igual que json_encode en PHP)
        body: JSON.stringify(data),
      })

      // Convertir la respuesta a objeto JavaScript
      // (igual que json_decode en PHP)
      const result = await response.json()

      // Verificar si la respuesta es un error HTTP
      if (!response.ok) {
        // Manejar errores específicos
        if (response.status === 401) {
          throw new Error(result.detail?.error || 'Credenciales inválidas. Verifica email y contraseña.')
        }
        if (response.status === 409) {
          throw new Error(result.detail?.error || 'Este email ya está registrado.')
        }
        if (response.status === 500) {
          console.error("ERROR BACKEND:", result)
          throw new Error(JSON.stringify(result))
        }
        throw new Error(result.detail?.error || result.error || `Error: ${response.status}`)
      }

      // Nuestro backend siempre devuelve { success: true/false, ... }
      if (!result.success) {
        throw new Error(result.error || 'Error desconocido')
      }

      return result.data

    } catch (err) {
      error.value = err.message
      throw err

    } finally {
      // finally se ejecuta siempre, haya error o no
      loading.value = false
    }
  }

  // Función GET genérica
  async function get(url) {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      })

      const result = await response.json()
      
      // Verificar si la respuesta es un error HTTP
      if (!response.ok) {
        throw new Error(result.detail?.error || result.error || `Error: ${response.status}`)
      }
      
      if (!result.success) {
        throw new Error(result.error || 'Error desconocido')
      }
      return result.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Función PUT genérica
  async function put(url, data) {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(url, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })

      const result = await response.json()
      
      if (!response.ok) {
        throw new Error(result.detail?.error || result.error || `Error: ${response.status}`)
      }
      
      if (!result.success) {
        throw new Error(result.error || 'Error desconocido')
      }
      return result.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Base URL para los endpoints PHP (ajustar si correspondiere)
  // Nuevo backend en Python (FastAPI) que corre en http://localhost:8000
  const baseApi = 'http://localhost:8000/api'

  // Funciones específicas: listar usuarios, registro y login
  async function getUsers() {
    return get(`${baseApi}/users`)
  }

  async function registerUser(payload) {
    return post(`${baseApi}/register`, payload)
  }

  async function loginUser(payload) {
    return post(`${baseApi}/login`, payload)
  }

  // --- Funciones específicas para cada endpoint ---

  // Generar imagen con IA (OpenAI DALL·E via FastAPI)
  async function generateImage(prompt, options = {}) {
    return post(`${baseApi}/generate-image`, {
      prompt,
      style: options.style || 'realista',
      width: options.width || 1024,
      height: options.height || 1024,
    })
  }

  // Crear pedido en la base de datos
  async function createOrder(orderData) {
    return post(`${baseApi}/create-order`, orderData)
  }

  // Crear pago con MercadoPago (via FastAPI)
  async function createPayment(orderData) {
    return post(`${baseApi}/create-payment`, orderData)
  }

  // Obtener todos los pedidos para el admin
  async function getAllOrders() {
    return get(`${baseApi}/admin/pedidos`)
  }

  // Actualizar estado de pedido
  async function updateOrderStatus(idDetalle, nuevoEstado) {
    return put(`${baseApi}/admin/pedidos/${idDetalle}/estado`, { estado: nuevoEstado })
  }

  // Actualizar estado de pago
  async function updateOrderPayment(idDetalle, nuevoPago) {
    return put(`${baseApi}/admin/pedidos/${idDetalle}/pago`, { estado_pago: nuevoPago })
  }

  // DELETE genérica
  async function del(url) {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(url, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
      })

      const result = await response.json()
      
      if (!response.ok) {
        throw new Error(result.detail?.error || result.error || `Error: ${response.status}`)
      }
      
      if (!result.success) {
        throw new Error(result.error || 'Error desconocido')
      }
      return result.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Actualizar producto
  async function updateProducto(idProducto, productoData) {
    return put(`${baseApi}/admin/productos/${idProducto}`, productoData)
  }

  // Actualizar precio de todas las variantes de un producto por Detalle
  async function updatePrecioProducto(detalle, nuevoPrecio, nuevoDetalle = null) {
    return put(`${baseApi}/admin/productos/detalle/${encodeURIComponent(detalle)}/precio`, {
      precio: nuevoPrecio,
      nuevo_detalle: nuevoDetalle
    })
  }

  // Eliminar producto
  async function deleteProducto(idProducto) {
    return del(`${baseApi}/admin/productos/${idProducto}`)
  }

  // Crear producto nuevo
  async function createProducto(productoData) {
    return post(`${baseApi}/admin/productos`, productoData)
  }

  // Obtener pedidos del usuario autenticado
  async function getMisPedidos(idUsuario) {
    return get(`${baseApi}/mis-pedidos/${idUsuario}`)
  }

  // Retornamos todo lo que los componentes necesitan
  return {
    loading,
    error,
    get,
    post,
    put,
    del,
    getUsers,
    registerUser,
    loginUser,
    generateImage,
    createOrder,
    createPayment,
    getAllOrders,
    updateOrderStatus,
    updateOrderPayment,
    updateProducto,
    updatePrecioProducto,
    deleteProducto,
    createProducto,
    getMisPedidos,
  }
}
