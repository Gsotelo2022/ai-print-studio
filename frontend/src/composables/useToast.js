import { ref } from 'vue'

// Estado global de toasts
const toasts = ref([])

export function useToast() {
  /**
   * Mostrar un toast
   * @param {string} message - Mensaje a mostrar
   * @param {string} type - Tipo: 'success', 'error', 'important' (warning)
   * @param {number} duration - Duración en ms (default 3500)
   */
  function showToast(message, type = 'success', duration = 3500) {
    const id = Date.now() + Math.random()
    
    // Mapear tipos alternos
    const tipoMapeado = {
      'exito': 'success',
      'exitoso': 'success',
      'advertencia': 'important',
      'warning': 'important',
      'info': 'important'
    }[type] || type

    const toast = {
      id,
      message,
      type: tipoMapeado
    }

    toasts.value.push(toast)

    if (duration > 0) {
      setTimeout(() => {
        toasts.value = toasts.value.filter(t => t.id !== id)
      }, duration)
    }

    return id
  }

  /**
   * Mostrar toast de éxito
   */
  function success(message, duration = 3500) {
    return showToast(message, 'success', duration)
  }

  /**
   * Mostrar toast de error
   */
  function error(message, duration = 3500) {
    return showToast(message, 'error', duration)
  }

  /**
   * Mostrar toast de advertencia/importante
   */
  function important(message, duration = 3500) {
    return showToast(message, 'important', duration)
  }

  /**
   * Remover un toast específico
   */
  function removeToast(id) {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  /**
   * Limpiar todos los toasts
   */
  function clearAll() {
    toasts.value = []
  }

  return {
    toasts,
    showToast,
    success,
    error,
    important,
    removeToast,
    clearAll
  }
}
