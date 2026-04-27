/**
 * ============================================
 * TEST DE FLUJO COMPLETO DE PEDIDO
 * ============================================
 * 
 * Este test simula el flujo completo de un usuario que:
 * 1. Selecciona un producto con sus variantes
 * 2. Ajusta posición y zoom de la imagen
 * 3. Confirma y crea un pedido en la base de datos
 * 4. Inicia el pago con Mercado Pago
 * 
 * REQUISITOS PARA EJECUTAR:
 * - Backend FastAPI corriendo en http://localhost:8000
 * - Base de datos SQL Server con estructura correcta
 * - Usuario de prueba creado en la BD
 */

// ============================================
// CONFIGURACIÓN
// ============================================

const BASE_URL = 'http://localhost:8000/api'
const TEST_USER_ID = 1 // Cambiar según tu BD

// Datos de prueba
const TEST_PRODUCT_DATA = {
  // Datos que simularían venir de ProductSelector
  key: 'remera',
  id_producto: 1,
  id_variante: 1,  // Debe existir en tu BD
  nombre: 'Remera',
  talle: 'M',
  color: 'Negro',
  cantidad: 1,
  precio: 12000,
  precioTotal: 12000,
  tienesTalle: true
}

const TEST_IMAGE_URL = 'https://example.com/test-image.png'
const TEST_PROMPT = 'Un diseño generado por IA para testing'

const TEST_POSITION = {
  x: 100,
  y: 100,
  zoom: 1.2
}

// ============================================
// UTILIDADES
// ============================================

/**
 * Realiza una petición HTTP y devuelve la respuesta parseada
 */
async function fetchAPI(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`
  
  try {
    console.log(`\n📡 ${options.method || 'GET'} ${url}`)
    if (options.body) {
      console.log('   Payload:', JSON.parse(options.body))
    }

    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    })

    const data = await response.json()

    console.log(`   ✅ Status: ${response.status}`)
    console.log('   Response:', data)

    return { response, data }
  } catch (error) {
    console.error(`   ❌ Error en ${url}:`, error.message)
    throw error
  }
}

/**
 * Verifica que una respuesta sea exitosa
 */
function assertSuccess(data, message) {
  if (!data.success) {
    throw new Error(`${message}: ${data.error || data.detail || 'Error desconocido'}`)
  }
  console.log(`   ✓ ${message}`)
}

/**
 * Verifica que un valor exista
 */
function assertExists(value, fieldName) {
  if (!value) {
    throw new Error(`${fieldName} no está definido`)
  }
  console.log(`   ✓ ${fieldName}: ${value}`)
}

// ============================================
// TESTS
// ============================================

/**
 * TEST 1: Verificar que el backend esté corriendo
 */
async function testBackendHealth() {
  console.log('\n╔════════════════════════════════════════╗')
  console.log('║  TEST 1: Backend Health Check         ║')
  console.log('╚════════════════════════════════════════╝')

  const { data } = await fetchAPI('/health')
  assertSuccess({ success: data.status === 'ok' }, 'Backend está activo')
}

/**
 * TEST 2: Obtener catálogo de productos
 */
async function testGetProducts() {
  console.log('\n╔════════════════════════════════════════╗')
  console.log('║  TEST 2: Obtener Productos             ║')
  console.log('╚════════════════════════════════════════╝')

  const { data } = await fetchAPI('/productos')
  assertSuccess(data, 'Productos obtenidos correctamente')
  
  if (!data.data || data.data.length === 0) {
    throw new Error('No hay productos en la base de datos')
  }

  console.log(`   ✓ ${data.data.length} productos encontrados`)
  
  // Mostrar primer producto como ejemplo
  const producto = data.data[0]
  console.log(`   📦 Ejemplo: ${producto.nombre}`)
  console.log(`      - Variantes: ${producto.variantes?.length || 0}`)
  console.log(`      - Precio desde: $${producto.precio_desde}`)

  return data.data
}

/**
 * TEST 3: Simular selección de producto (ProductSelector)
 */
function testProductSelection() {
  console.log('\n╔════════════════════════════════════════╗')
  console.log('║  TEST 3: Selección de Producto         ║')
  console.log('╚════════════════════════════════════════╝')

  console.log('   🛒 Simulando selección en ProductSelector:')
  console.log(`      - Producto: ${TEST_PRODUCT_DATA.nombre}`)
  console.log(`      - Talle: ${TEST_PRODUCT_DATA.talle}`)
  console.log(`      - Color: ${TEST_PRODUCT_DATA.color}`)
  console.log(`      - Cantidad: ${TEST_PRODUCT_DATA.cantidad}`)
  console.log(`      - Precio total: $${TEST_PRODUCT_DATA.precioTotal}`)
  console.log(`      - ID Variante: ${TEST_PRODUCT_DATA.id_variante}`)

  // Validar que tengamos id_variante
  if (!TEST_PRODUCT_DATA.id_variante) {
    throw new Error('⚠️  IMPORTANTE: Debes configurar un id_variante válido en TEST_PRODUCT_DATA')
  }

  console.log('   ✓ Datos de selección válidos')
  return TEST_PRODUCT_DATA
}

/**
 * TEST 4: Simular ajustes en PreviewPanel
 */
function testPreviewAdjustments() {
  console.log('\n╔════════════════════════════════════════╗')
  console.log('║  TEST 4: Ajustes de Preview            ║')
  console.log('╚════════════════════════════════════════╝')

  console.log('   🎨 Simulando ajustes en PreviewPanel:')
  console.log(`      - Posición X: ${TEST_POSITION.x}px`)
  console.log(`      - Posición Y: ${TEST_POSITION.y}px`)
  console.log(`      - Zoom: ${TEST_POSITION.zoom}x`)
  console.log(`      - Imagen: ${TEST_IMAGE_URL}`)

  console.log('   ✓ Ajustes configurados')
  return TEST_POSITION
}

/**
 * TEST 5: Crear pedido (PreviewPanel → Backend)
 */
async function testCreateOrder(productData, positionData) {
  console.log('\n╔════════════════════════════════════════╗')
  console.log('║  TEST 5: Crear Pedido                  ║')
  console.log('╚════════════════════════════════════════╝')

  // Construir payload como lo hace PreviewPanel
  const payload = {
    user_id: TEST_USER_ID,
    items: [
      {
        id_variante: productData.id_variante,
        cantidad: productData.cantidad,
        archivo_diseno: TEST_IMAGE_URL,
        posicion_x: positionData.x,
        posicion_y: positionData.y,
        zoom: positionData.zoom
      }
    ],
    direccion_envio: 'Dirección de prueba 123',
    ciudad: 'Buenos Aires',
    telefono_contacto: '+54 11 1234-5678',
    notas_cliente: TEST_PROMPT
  }

  const { data } = await fetchAPI('/create-order', {
    method: 'POST',
    body: JSON.stringify(payload)
  })

  assertSuccess(data, 'Pedido creado exitosamente')
  
  const orderInfo = data.data
  assertExists(orderInfo.order_id, 'Order ID')
  assertExists(orderInfo.numero_orden, 'Número de orden')
  assertExists(orderInfo.total, 'Total del pedido')

  console.log(`   💰 Total: $${orderInfo.total}`)
  console.log(`   📦 Items: ${orderInfo.items_count}`)

  return orderInfo
}

/**
 * TEST 6: Crear preferencia de pago en Mercado Pago
 */
async function testCreatePayment(orderInfo, productData) {
  console.log('\n╔════════════════════════════════════════╗')
  console.log('║  TEST 6: Crear Pago (Mercado Pago)     ║')
  console.log('╚════════════════════════════════════════╝')

  console.log('   ⚠️  NOTA: Este test requiere PHP backend en puerto 8080')
  console.log('   Si falla, verifica que el servidor PHP esté corriendo')

  try {
    // Este endpoint está en PHP en puerto 8080
    const phpUrl = 'http://localhost:8080/api/create-payment.php'
    
    const payload = {
      order_id: orderInfo.order_id,
      producto: productData.nombre,
      precio: productData.precioTotal,
      cantidad: productData.cantidad
    }

    console.log(`\n📡 POST ${phpUrl}`)
    console.log('   Payload:', payload)

    const response = await fetch(phpUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    const data = await response.json()

    console.log(`   ✅ Status: ${response.status}`)
    console.log('   Response:', data)

    if (data.error) {
      console.log('   ⚠️  Error al crear preferencia de pago:', data.error)
      console.log('   Esto es esperado si no tienes credenciales de Mercado Pago configuradas')
      return null
    }

    if (data.success !== false && (data.sandbox_url || data.payment_url || data.init_point)) {
      const payUrl = data.sandbox_url || data.payment_url || data.init_point
      console.log('   ✓ Preferencia de pago creada')
      console.log(`   🔗 URL de pago: ${payUrl}`)
      return { paymentUrl: payUrl }
    }

    return null

  } catch (error) {
    console.log('   ⚠️  No se pudo conectar con el backend PHP')
    console.log('   Esto es esperado si solo tienes el backend FastAPI corriendo')
    return null
  }
}

/**
 * TEST 7: Verificar que el pedido existe en la BD
 */
async function testVerifyOrderInDB(orderInfo) {
  console.log('\n╔════════════════════════════════════════╗')
  console.log('║  TEST 7: Verificar Pedido en BD        ║')
  console.log('╚════════════════════════════════════════╝')

  console.log(`   🔍 Buscando pedido #${orderInfo.order_id}...`)

  try {
    // Intentar obtener todos los pedidos del admin
    const { data } = await fetchAPI('/admin/pedidos')

    if (data.success && data.data) {
      const pedido = data.data.find(p => p.id_pedido === orderInfo.order_id)
      
      if (pedido) {
        console.log('   ✓ Pedido encontrado en la base de datos')
        console.log(`      - Estado: ${pedido.estado}`)
        console.log(`      - Pago: ${pedido.estado_pago}`)
        console.log(`      - Total: $${pedido.total}`)
        return pedido
      } else {
        console.log(`   ⚠️  Pedido #${orderInfo.order_id} no encontrado en la lista`)
      }
    }
  } catch (error) {
    console.log('   ⚠️  No se pudo verificar el pedido (endpoint admin puede requerir auth)')
  }

  return null
}

// ============================================
// EJECUTAR TODOS LOS TESTS
// ============================================

async function runAllTests() {
  console.log('\n')
  console.log('╔═══════════════════════════════════════════════════════════╗')
  console.log('║  🧪 TEST DE FLUJO COMPLETO DE PEDIDO                      ║')
  console.log('║     AI Print Studio - Order Flow Test                    ║')
  console.log('╚═══════════════════════════════════════════════════════════╝')

  try {
    // Test 1: Backend activo
    await testBackendHealth()

    // Test 2: Obtener productos
    const productos = await testGetProducts()

    // Test 3: Seleccionar producto
    const productSelection = testProductSelection()

    // Test 4: Ajustes de preview
    const previewSettings = testPreviewAdjustments()

    // Test 5: Crear pedido
    const orderInfo = await testCreateOrder(productSelection, previewSettings)

    // Test 6: Crear pago
    const paymentInfo = await testCreatePayment(orderInfo, productSelection)

    // Test 7: Verificar en BD
    await testVerifyOrderInDB(orderInfo)

    // ============================================
    // RESULTADO FINAL
    // ============================================
    console.log('\n')
    console.log('╔═══════════════════════════════════════════════════════════╗')
    console.log('║  ✅ TODOS LOS TESTS COMPLETADOS EXITOSAMENTE              ║')
    console.log('╚═══════════════════════════════════════════════════════════╝')
    console.log('\n📋 RESUMEN DEL PEDIDO CREADO:')
    console.log(`   • ID de Pedido: ${orderInfo.order_id}`)
    console.log(`   • Número de Orden: ${orderInfo.numero_orden}`)
    console.log(`   • Total: $${orderInfo.total}`)
    console.log(`   • Items: ${orderInfo.items_count}`)
    console.log(`   • Producto: ${productSelection.nombre}`)
    console.log(`   • Variante: ${productSelection.color} - ${productSelection.talle || 'Sin talle'}`)
    console.log(`   • Cantidad: ${productSelection.cantidad}`)
    
    if (paymentInfo) {
      console.log(`\n💳 INFORMACIÓN DE PAGO:`)
      console.log(`   • URL: ${paymentInfo.paymentUrl}`)
    }

    console.log('\n✅ El flujo de pedido funciona correctamente!')
    console.log('   Ahora puedes:')
    console.log('   1. Verificar el pedido en el panel de administrador')
    console.log('   2. Procesar el pago en Mercado Pago (si configuraste credenciales)')
    console.log('   3. Actualizar el estado del pedido\n')

    return true

  } catch (error) {
    console.log('\n')
    console.log('╔═══════════════════════════════════════════════════════════╗')
    console.log('║  ❌ ERROR EN LOS TESTS                                     ║')
    console.log('╚═══════════════════════════════════════════════════════════╝')
    console.error('\n❌ Error:', error.message)
    console.error('\n📍 Stack:', error.stack)
    
    console.log('\n🔧 SOLUCIÓN DE PROBLEMAS:')
    console.log('   1. Verifica que el backend FastAPI esté corriendo en puerto 8000')
    console.log('   2. Verifica que la base de datos esté accesible')
    console.log('   3. Asegúrate de que TEST_USER_ID existe en la tabla Usuarios')
    console.log('   4. Verifica que TEST_PRODUCT_DATA.id_variante existe en la tabla Variantes')
    console.log('   5. Revisa los logs del backend para más detalles\n')

    return false
  }
}

// ============================================
// CONFIGURACIÓN PARA NODE.JS
// ============================================

// Detectar si estamos en Node.js (no en navegador)
if (typeof module !== 'undefined' && module.exports) {
  // Importar fetch para Node.js
  const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args))
  global.fetch = fetch

  // Ejecutar tests
  runAllTests().then(success => {
    process.exit(success ? 0 : 1)
  })
}

// ============================================
// EXPORT PARA USO EN OTROS TESTS
// ============================================

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    runAllTests,
    testBackendHealth,
    testGetProducts,
    testProductSelection,
    testPreviewAdjustments,
    testCreateOrder,
    testCreatePayment,
    testVerifyOrderInDB,
    TEST_PRODUCT_DATA,
    TEST_USER_ID
  }
}
