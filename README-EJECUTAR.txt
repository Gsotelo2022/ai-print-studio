╔════════════════════════════════════════════════════════╗
║         INSTRUCCIONES - EJECUTAR APLICACIÓN            ║
║                                                        ║
║              🚀 Prendete Rock AI Print Studio         ║
╚════════════════════════════════════════════════════════╝


✅ REQUISITOS ANTES DE EJECUTAR:

1️⃣  PYTHON 3.8+ instalado
    └─ Verificar: python --version

2️⃣  NODE.JS 18+ instalado  
    └─ Verificar: node --version

3️⃣  SQL Server Express instalado y corriendo
    ├─ Servidor: .\SQLEXPRESS01
    ├─ BD: PrendeteRock
    └─ Con tabla de productos poblada

4️⃣  OLLAMA instalado (OPCIONAL pero RECOMENDADO)
    ├─ Descargar: https://ollama.com
    ├─ Windows: descarga el instalador .exe
    └─ Verificar: ollama --version

5️⃣  PHP 8.0+ instalado (si quieres Mercado Pago)
    └─ Verificar: php --version


🎯 PASOS PARA EJECUTAR:

1. Primera vez con OLLAMA:
   ────────────────────────
   a) Ejecuta: descargar-modelo-ia.bat
   b) Espera a que descargue qwen2.5:1.5b (3-5 minutos)
   c) Cierra la ventana cuando termine
   d) Luego: RUN.bat

   ⏭️  Al ejecutar RUN.bat, OLLAMA se inicia automáticamente


2. Próximas veces:
   ───────────────
   Solo ejecuta: RUN.bat
   
   El script detectará automáticamente:
   ✓ Si OLLAMA está corriendo
   ✓ Si está descargado el modelo
   ✓ Las dependencias de Python/Node


3. En el navegador:
   ────────────────
   - Se abrirá automáticamente: http://localhost:5173
   - Registrate o usa:
     Email: cliente@test.com
     Pwd: password123


📊 SERVIDORES QUE SE LEVANTARÁN:

① FastAPI Backend ........... http://127.0.0.1:8000
② OLLAMA (IA) .............. http://localhost:11434
③ Agente de Productos ...... http://localhost:5001
④ Vue.js Frontend .......... http://localhost:5173
⑤ PHP Backend (opcional) ... http://localhost:8080


🛑 PARA DETENER LA APLICACIÓN:

Cierra las ventanas que se abrieron automáticamente:
├─ Ventana de FastAPI
├─ Ventana de OLLAMA
├─ Ventana del Agente
├─ Ventana de Vue.js
└─ Ventana de PHP (si está abierta)

O ejecuta en PowerShell:
  Get-Process ollama, python, node, php | Stop-Process


⚠️  TROUBLESHOOTING:

Problema: Error 500 en http://localhost:5001
Causa: OLLAMA no está corriendo o no descargó el modelo
Solución:
  a) Ejecuta: descargar-modelo-ia.bat
  b) Verifica: ollama list | findstr qwen2.5:1.5b
  c) Si no aparece, ejecuta: ollama pull qwen2.5:1.5b

Problema: "No se puede conectar a SQL Server"
Causa: SQL Server Express no está corriendo o BD no existe
Solución:
  a) Abre Services (services.msc)
  b) Busca "SQL Server (SQLEXPRESS01)"
  c) Verifica que esté en estado "Running"
  d) Si no existe la BD, ejecuta: crear-base-datos.bat

Problema: Port ya está en uso
Causa: Quedan procesos de ejecución anterior
Solución:
  Get-Process | Select-Object ProcessName, Id


✨ CARACTERÍSTICAS:

✓ Registro y login con hash PBKDF2
✓ Generación de imágenes con IA (DALL-E compatible)
✓ Remoción de fondo automática
✓ Catálogo dinámico de productos (desde Agente IA)
✓ Carrito de compras inteligente
✓ Integración WhatsApp
✓ Pagos con Mercado Pago
✓ Admin Dashboard


📧 SOPORTE:

Para más información, contacta al equipo de desarrollo.

═══════════════════════════════════════════════════════════

Última actualización: 21/04/2026
Versión: 1.0 - Sistema Completo con Agente IA
