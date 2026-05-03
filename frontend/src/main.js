// ============================================
// main.js - Punto de entrada de Vue
// ============================================
// Este archivo hace UNA sola cosa:
// Crea la aplicación Vue y la "monta" en el div #app del HTML.

import { createApp } from 'vue'
import App from './App.vue'
import './assets/styles.css'
import { useToast } from './composables/useToast.js'

// Inicializar toasts globalmente y sobreescribir window.alert
const { showToast } = useToast()
window.alert = (msg) => showToast(msg, 'important')

createApp(App).mount('#app')
