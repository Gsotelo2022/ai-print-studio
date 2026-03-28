// ============================================
// main.js - Punto de entrada de Vue
// ============================================
// Este archivo hace UNA sola cosa:
// Crea la aplicación Vue y la "monta" en el div #app del HTML.

import { createApp } from 'vue'
import App from './App.vue'
import './assets/styles.css'

// createApp(App) → crea una instancia de la app con App.vue como raíz
// .mount('#app') → la inyecta en el HTML dentro de <div id="app">
createApp(App).mount('#app')
