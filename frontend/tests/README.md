# 🧪 Tests de AI Print Studio

## Test de Flujo de Pedido Completo

Este test simula todo el proceso de crear un pedido, desde la selección del producto hasta la creación del pago.

### 📋 Prerrequisitos

1. **Backend FastAPI** corriendo en `http://localhost:8000`
2. **Base de datos SQL Server** con datos de prueba
3. **Usuario de prueba** creado en la BD
4. **(Opcional)** Backend PHP en `http://localhost:8080` para el test de pagos

### 🚀 Cómo Ejecutar los Tests

#### Opción 1: Desde Node.js (Recomendado)

```bash
# Instalar node-fetch si aún no está instalado
npm install node-fetch

# Ejecutar el test
node frontend/tests/order-flow.test.js
```

#### Opción 2: Desde el Navegador

Abre el archivo `frontend/tests/order-flow.test.html` en tu navegador web. Esto ejecutará los tests y mostrará los resultados en la consola del navegador.

### ⚙️ Configuración

Antes de ejecutar los tests, **DEBES** configurar estos valores en `order-flow.test.js`:

```javascript
// Línea 18-19
const BASE_URL = 'http://localhost:8000/api'
const TEST_USER_ID = 1 // ⚠️ Cambiar al ID de un usuario real en tu BD

// Líneas 22-34
const TEST_PRODUCT_DATA = {
  key: 'remera',
  id_producto: 1,
  id_variante: 1,  // ⚠️ IMPORTANTE: Debe existir en tu BD
  nombre: 'Remera',
  talle: 'M',
  color: 'Negro',
  cantidad: 1,
  precio: 12000,
  precioTotal: 12000,
  tienesTalle: true
}
```

### 📊 Qué Testea

El test verifica el flujo completo en 7 pasos:

1. **Backend Health Check** - Verifica que el backend esté activo
2. **Obtener Productos** - Consulta el catálogo desde la BD
3. **Selección de Producto** - Simula la selección en ProductSelector.vue
4. **Ajustes de Preview** - Simula posición/zoom en PreviewPanel.vue
5. **Crear Pedido** - POST a `/api/create-order`
6. **Crear Pago** - POST a `/api/create-payment` (Mercado Pago)
7. **Verificar en BD** - Confirma que el pedido fue guardado

### ✅ Salida Esperada

Si todo funciona correctamente, verás algo como:

```
╔═══════════════════════════════════════════════════════════╗
║  ✅ TODOS LOS TESTS COMPLETADOS EXITOSAMENTE              ║
╚═══════════════════════════════════════════════════════════╝

📋 RESUMEN DEL PEDIDO CREADO:
   • ID de Pedido: 42
   • Número de Orden: ORD-2026-00042
   • Total: $12000
   • Items: 1
   • Producto: Remera
   • Variante: Negro - M
   • Cantidad: 1

💳 INFORMACIÓN DE PAGO:
   • URL: https://www.mercadopago.com/mla/checkout/start?pref_id=...

✅ El flujo de pedido funciona correctamente!
```

### ⚠️ Solución de Problemas

#### Error: "Backend no responde"
- Verifica que FastAPI esté corriendo: `python database/source/app_v2.py`
- Comprueba la URL: `http://localhost:8000/api/health`

#### Error: "Usuario no existe"
- Asegúrate de cambiar `TEST_USER_ID` a un ID válido
- Verifica en SQL Server: `SELECT * FROM Usuarios`

#### Error: "id_variante no existe"
- Cambia `TEST_PRODUCT_DATA.id_variante` a un ID válido
- Consulta variantes disponibles: `SELECT * FROM Variantes`

#### Error: "No hay productos"
- Ejecuta el script de población de datos: `database/POBLAR-DATOS-INICIALES.sql`
- O crea productos desde el panel de administrador

### 🔍 Debugging

Para ver más detalles de las peticiones HTTP:

1. **Node.js**: Los logs ya se muestran automáticamente
2. **Navegador**: Abre DevTools (F12) → Pestaña Console

### 📝 Estructura del Test

```javascript
order-flow.test.js
├── Configuración (líneas 1-45)
├── Utilidades (líneas 48-80)
└── Tests (líneas 83-400)
    ├── testBackendHealth()
    ├── testGetProducts()
    ├── testProductSelection()
    ├── testPreviewAdjustments()
    ├── testCreateOrder()
    ├── testCreatePayment()
    ├── testVerifyOrderInDB()
    └── runAllTests()
```

### 🛠️ Personalizar el Test

Para testear diferentes escenarios, modifica:

- **Producto diferente**: Cambia `TEST_PRODUCT_DATA`
- **Múltiples items**: Modifica el payload en `testCreateOrder()` para incluir más items
- **Usuario diferente**: Cambia `TEST_USER_ID`
- **Dirección de envío**: Modifica los campos en `testCreateOrder()`

### 📚 Próximos Tests a Implementar

- [ ] Test de actualizaciones de estado de pedidos
- [ ] Test de webhooks de Mercado Pago
- [ ] Test de generación de imágenes con IA
- [ ] Test de eliminación de fondos
- [ ] Test de gestión de productos (CRUD)
- [ ] Test de autenticación de usuarios

### 💡 Tips

- Ejecuta los tests después de cada cambio en el backend
- Usa variantes con stock disponible para evitar errores
- Los tests no eliminan los pedidos creados, revísalos en el panel admin
- Puedes modificar `TEST_IMAGE_URL` para usar imágenes reales

---

**¿Necesitas ayuda?** Revisa el código fuente, está bien comentado para entender cada paso.
