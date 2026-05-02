// // ============================================
// // Vite Config
// // ============================================
// // Vite es el "servidor de desarrollo" del frontend.
// // Su trabajo principal:
// //   1. Servir los archivos Vue en desarrollo (hot reload)
// //   2. Compilar/empaquetar para producción
// //   3. Redirigir peticiones /api/ al backend PHP (proxy)

// import { defineConfig } from 'vite'
// import vue from '@vitejs/plugin-vue'

// export default defineConfig({
//   plugins: [vue()],

//   server: {
//     port: 5173,  // Puerto donde corre el frontend

//     // PROXY: Esto es clave para conectar frontend y backend.
//     // Cuando el frontend hace fetch('/api/generate-image.php'),
//     // Vite intercepta esa petición y la reenvía al servidor PHP
//     // que corre en el puerto 8080.
//     //
//     // Sin esto, tendrías problemas de CORS porque el frontend
//     // (puerto 5173) y el backend (puerto 8080) son "orígenes" distintos.
//     proxy: {
//       '/api': {
//         target: 'http://localhost:8080',  // Tu servidor PHP
//         changeOrigin: true,
//       },
//       '/uploads': {
//         target: 'http://localhost:8080',  // Imágenes generadas
//         changeOrigin: true,
//       },
//     },
//   },
// })
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})