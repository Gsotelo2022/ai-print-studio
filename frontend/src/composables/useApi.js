// ============================================
// useApi.js - Composable PRO (VERSIÓN FINAL)
// ============================================

import { ref } from 'vue'

// ============================================
// 🌐 BASE URL DINÁMICA
// ============================================
const getBaseUrl = () => {
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  return `${apiUrl}/api`
}

export function useApi() {
  const loading = ref(false)
  const error = ref(null)
  const baseApi = getBaseUrl()

  // ============================================
  // 🔐 HEADERS + JWT
  // ============================================
  function getHeaders(isFormData = false) {
    const headers = {}
    const token = localStorage.getItem('token')

    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    if (!isFormData) {
      headers['Content-Type'] = 'application/json'
    }

    return headers
  }

  // ============================================
  // 🧠 PARSE JSON SEGURO
  // ============================================
  async function safeJson(response) {
    try {
      return await response.json()
    } catch {
      throw new Error('El backend no respondió JSON válido')
    }
  }

  // ============================================
  // 🚨 MANEJO DE ERRORES HTTP
  // ============================================
  function handleHttpError(response, result) {
    if (response.status === 401) {
      localStorage.removeItem('token')
      throw new Error('Sesión expirada. Iniciá sesión nuevamente.')
    }

    if (response.status === 403) {
      throw new Error('No tenés permisos para esta acción')
    }

    if (response.status === 404) {
      throw new Error('Recurso no encontrado')
    }

    if (response.status === 409) {
      throw new Error(result?.detail?.error || 'Conflicto de datos')
    }

    if (response.status === 500) {
      console.error('🔥 ERROR BACKEND:', result)
      const backendMsg = result?.detail?.error || result?.detail || result?.error || null
      throw new Error(backendMsg || 'Error interno del servidor')
    }

    throw new Error(result?.detail?.error || result?.error || `Error HTTP ${response.status}`)
  }

  // ============================================
  // 📡 GET
  // ============================================
  async function get(url) {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${baseApi}${url}`, {
        method: 'GET',
        headers: getHeaders(),
      })

      const result = await safeJson(response)

      if (!response.ok) handleHttpError(response, result)
      if (!result.success) throw new Error(result.error || 'Error desconocido')

      return result.data

    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // ============================================
  // 📡 POST
  // ============================================
  async function post(url, data, isFormData = false) {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${baseApi}${url}`, {
        method: 'POST',
        headers: getHeaders(isFormData),
        body: isFormData ? data : JSON.stringify(data),
      })

      const result = await safeJson(response)

      if (!response.ok) handleHttpError(response, result)
      if (!result.success) throw new Error(result.error || 'Error desconocido')

      return result.data

    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // ============================================
  // 📡 PUT
  // ============================================
  async function put(url, data) {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${baseApi}${url}`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify(data),
      })

      const result = await safeJson(response)

      if (!response.ok) handleHttpError(response, result)
      if (!result.success) throw new Error(result.error || 'Error desconocido')

      return result.data

    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // ============================================
  // 📡 DELETE
  // ============================================
  async function del(url) {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${baseApi}${url}`, {
        method: 'DELETE',
        headers: getHeaders(),
      })

      const result = await safeJson(response)

      if (!response.ok) handleHttpError(response, result)
      if (!result.success) throw new Error(result.error || 'Error desconocido')

      return result.data

    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // ============================================
  // 🔐 AUTH
  // ============================================
  async function registerUser(payload) {
    return post('/register', payload)
  }

  async function loginUser(payload) {
    const data = await post('/login', payload)

    if (data.token) {
      localStorage.setItem('token', data.token)
    }

    return data
  }

  async function login(email, password) {
    return loginUser({ email, password })
  }

  // ============================================
  // 🤖 IA
  // ============================================
  async function generateImage(prompt, options = {}) {
    return post('/generate-image', {
      prompt,
      style: options.style || 'realista',
      width: options.width || 1024,
      height: options.height || 1024,
    })
  }

  async function removeBackground(file) {
    const formData = new FormData()
    formData.append('file', file)
    return post('/remove-background', formData, true)
  }

  // ============================================
  // 🎨 DISEÑOS
  // ============================================
  async function uploadDesign(file, userId) {
    const formData = new FormData()
    formData.append('file', file)
    // user_id va como query param porque el backend usa FastAPI Form Query
    return post(`/upload-design?user_id=${userId}`, formData, true)
  }

  async function getMisDisenos(userId) {
    return get(`/mis-disenos/${userId}`)
  }

  // ============================================
  // 🛒 PEDIDOS
  // ============================================
  async function createOrder(orderData) {
    return post('/create-order', orderData)
  }

  async function createPayment(orderData) {
    return post('/create-payment', orderData)
  }

  async function getMisPedidos(idUsuario) {
    return get(`/mis-pedidos/${idUsuario}`)
  }

  async function getAllOrders() {
    return get('/admin/pedidos')
  }

  async function updateOrderStatus(id, estado) {
    return put(`/admin/pedidos/${id}/estado`, { estado })
  }

  async function updateOrderPayment(id, estado_pago) {
    return put(`/admin/pedidos/${id}/pago`, { estado_pago })
  }

  // ============================================
  // 📦 PRODUCTOS
  // ============================================
  async function createProducto(data) {
    return post('/admin/productos', data)
  }

  async function updateProducto(id, data) {
    return put(`/admin/productos/${id}`, data)
  }

  async function deleteProducto(id) {
    return del(`/admin/productos/${id}`)
  }
  // ============================================
  // 🎟️ CUPONES
  // ============================================
  async function getCuponesDisponibles() {
    return get('/cupones')
  }

  async function getCuponesUsuario(userId) {
    return get(`/cupones/disponibles/${userId}`)
  }

  // ============================================
  // 🚀 EXPORT
  // ============================================
  return {
    loading,
    error,

    get,
    post,
    put,
    del,

    login,
    loginUser,
    registerUser,

    generateImage,
    removeBackground,

    uploadDesign,
    getMisDisenos,

    createOrder,
    createPayment,
    getMisPedidos,
    getAllOrders,
    updateOrderStatus,
    updateOrderPayment,

    createProducto,
    updateProducto,
    deleteProducto,

    getCuponesDisponibles,
    getCuponesUsuario,
  }
}