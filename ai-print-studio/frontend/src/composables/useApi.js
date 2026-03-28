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

  // --- Funciones específicas para cada endpoint ---

  // Generar imagen con Stability AI
  async function generateImage(prompt, options = {}) {
    return post('http://localhost:8080/api/generate-image.php', {
      prompt,
      style: options.style || 'realista',
      width: options.width || 1024,
      height: options.height || 1024,
    })
  }

  // Crear pedido en la base de datos
  async function createOrder(orderData) {
    return post('/api/create-order.php', orderData)
  }

  // Crear pago con MercadoPago
  async function createPayment(orderId) {
    return post('/api/create-payment.php', {
      order_id: orderId,
    })
  }

  // Retornamos todo lo que los componentes necesitan
  return {
    loading,
    error,
    generateImage,
    createOrder,
    createPayment,
  }
}
