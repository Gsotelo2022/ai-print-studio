# 🎯 INSTRUCCIONES PARA EJECUTAR EL TEST DE PEDIDO

## ✅ Cambios Realizados

Se han creado exitosamente los siguientes archivos:

### 1. **ProductSelector.vue** - Completado
- ✅ Se añadió el bloque `<script setup>` faltante
- ✅ Incluye toda la lógica de selección de productos
- ✅ Maneja variantes (talle, color, cantidad)
- ✅ Busca el `id_variante` correcto de la BD
- ✅ Emite evento `@product-selected` con todos los datos necesarios

### 2. **Test Completo de Flujo de Pedido**
- ✅ `frontend/tests/order-flow.test.js` - Test funcional completo
- ✅ `frontend/tests/order-flow.test.html` - Interfaz web para ejecutar tests
- ✅ `frontend/tests/README.md` - Documentación detallada
- ✅ `frontend/run-tests.bat` - Script para Windows
- ✅ `frontend/run-tests.ps1` - Script PowerShell
- ✅ `frontend/package.json` - Actualizado con dependencias y scripts

---

## 🚀 CÓMO EJECUTAR LOS TESTS

### Opción 1: Usando Scripts Automatizados (Recomendado)

#### Windows (CMD):
```cmd
cd c:\projects\ai-print-studio\frontend
run-tests.bat
```

#### Windows (PowerShell):
```powershell
cd c:\projects\ai-print-studio\frontend
.\run-tests.ps1
```

### Opción 2: Desde Node.js

```bash
cd C:\projects\ai-print-studio\frontend

# Instalar dependencias (solo la primera vez)
npm install

# Ejecutar tests
npm test
```

### Opción 3: Desde el Navegador

1. Abre el archivo: `C:\projects\ai-print-studio\frontend\tests\order-flow.test.html`
2. Configura los parámetros en el formulario
3. Presiona "Ejecutar Test"
4. Revisa los resultados en pantalla y en la consola (F12)

---

## ⚙️ CONFIGURACIÓN ANTES DE EJECUTAR

### 1. Verifica que el Backend esté corriendo

```bash
# Iniciar backend FastAPI
cd c:\projects\ai-print-studio\database\source
python app_v2.py
```

El backend debe estar activo en: `http://localhost:8000`

### 2. Configura los IDs de Prueba

Edita `frontend/tests/order-flow.test.js` (líneas 18-34):

```javascript
const TEST_USER_ID = 1 // ⚠️ Cambiar a un ID real de tu BD

const TEST_PRODUCT_DATA = {
  id_variante: 1,  // ⚠️ IMPORTANTE: Debe existir en tu BD
  // ... resto de la configuración
}
```

Para obtener IDs válidos, ejecuta en SQL Server:

```sql
-- Obtener usuarios
SELECT id_usuario, nombre, email FROM Usuarios;

-- Obtener variantes
SELECT v.id_variante, p.nombre, v.sku, v.precio 
FROM Variantes v
JOIN Productos p ON v.id_producto = p.id_producto
WHERE v.activo = 1;
```

### 3. Verifica la Base de Datos

Asegúrate de tener:
- ✅ Al menos un usuario en la tabla `Usuarios`
- ✅ Productos en la tabla `Productos`
- ✅ Variantes en la tabla `Variantes`
- ✅ Atributos configurados (Color, Talle, etc.)

Si no tienes datos, ejecuta:
```sql
-- Desde SQL Server Management Studio
-- Ejecutar: C:\projects\ai-print-studio\database\POBLAR-DATOS-INICIALES.sql
```

---

## 📊 QUÉ HACE EL TEST

El test simula el flujo completo de crear un pedido:

1. ✅ **Backend Health Check** - Verifica que el servidor esté activo
2. ✅ **Obtener Productos** - Consulta el catálogo desde `/api/productos`
3. ✅ **Seleccionar Producto** - Simula la selección en ProductSelector.vue
4. ✅ **Ajustar Preview** - Simula los ajustes de posición/zoom
5. ✅ **Crear Pedido** - POST a `/api/create-order`
6. ✅ **Crear Pago** - POST a `/api/create-payment` (Mercado Pago)
7. ✅ **Verificar BD** - Confirma que el pedido se guardó

---

## 📋 SALIDA ESPERADA

Si todo funciona correctamente, verás:

```
╔═══════════════════════════════════════════════════════════╗
║  🧪 TEST DE FLUJO COMPLETO DE PEDIDO                      ║
╚═══════════════════════════════════════════════════════════╝

╔════════════════════════════════════════╗
║  TEST 1: Backend Health Check         ║
╚════════════════════════════════════════╝

📡 GET http://localhost:8000/api/health
   ✅ Status: 200
   ✓ Backend está activo

╔════════════════════════════════════════╗
║  TEST 2: Obtener Productos             ║
╚════════════════════════════════════════╝

📡 GET http://localhost:8000/api/productos
   ✅ Status: 200
   ✓ Productos obtenidos correctamente
   ✓ 5 productos encontrados

... (continúa con los demás tests) ...

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

✅ El flujo de pedido funciona correctamente!
```

---

## ⚠️ SOLUCIÓN DE PROBLEMAS

### Error: "Backend no responde"

**Causa:** El backend FastAPI no está corriendo

**Solución:**
```bash
cd c:\projects\ai-print-studio\database\source
python app_v2.py
```

Verifica en: `http://localhost:8000/docs`

---

### Error: "Usuario no existe"

**Causa:** TEST_USER_ID no es válido

**Solución:**
```sql
-- En SQL Server
SELECT id_usuario, nombre FROM Usuarios;
```
Actualiza `TEST_USER_ID` en `order-flow.test.js`

---

### Error: "id_variante no existe"

**Causa:** La variante especificada no existe en la BD

**Solución:**
```sql
-- En SQL Server
SELECT v.id_variante, p.nombre, v.sku
FROM Variantes v
JOIN Productos p ON v.id_producto = p.id_producto
WHERE v.activo = 1;
```
Actualiza `TEST_PRODUCT_DATA.id_variante` en `order-flow.test.js`

---

### Error: "No hay productos"

**Causa:** La tabla Productos está vacía

**Solución:**
```bash
# Ejecutar script de población de datos
# Desde SQL Server Management Studio:
# Abrir y ejecutar: database/POBLAR-DATOS-INICIALES.sql
```

O usa el panel de administrador para crear productos.

---

### Error: "node-fetch no está instalado"

**Causa:** Falta la dependencia node-fetch

**Solución:**
```bash
cd c:\projects\ai-print-studio\frontend
npm install node-fetch
```

---

## 🎨 COMPONENTES MODIFICADOS

### ProductSelector.vue

Se completó el componente con:
- Props: `productos`, `loading`, `loaded`
- Emits: `product-selected`, `go-back`
- Estado: selección de variantes (talle, color, cantidad)
- Lógica: búsqueda de variante correcta por atributos

**Cambio clave:** Ahora busca el `id_variante` correcto consultando las variantes del producto y comparando los atributos seleccionados (talle + color).

**Uso:**
```vue
<ProductSelector
  :productos="productos"
  :loading="productosLoading"
  :loaded="productosLoaded"
  @product-selected="onProductSelected"
  @go-back="goBack"
/>
```

**Evento emitido:**
```javascript
{
  key: 'remera',
  id_producto: 1,
  id_variante: 1,      // ← ID de BD
  nombre: 'Remera',
  talle: 'M',
  color: 'Negro',
  cantidad: 1,
  precio: 12000,
  precioTotal: 12000,
  tienesTalle: true
}
```

---

## 📚 ARCHIVOS CREADOS

```
frontend/
├── tests/
│   ├── order-flow.test.js       # Test principal
│   ├── order-flow.test.html     # UI para navegador
│   ├── README.md                # Documentación
│   └── INSTRUCCIONES.md         # Este archivo
├── run-tests.bat                # Script Windows
├── run-tests.ps1                # Script PowerShell
└── package.json                 # Actualizado con scripts de test
```

---

## 🔄 PRÓXIMOS PASOS

Después de ejecutar el test:

1. **Verifica el pedido en el panel admin**
   - Ingresa como administrador
   - Revisa la sección "Gestión de Pedidos"
   - Confirma que el pedido aparece con el estado correcto

2. **Prueba el flujo completo en la UI**
   - Registra un usuario
   - Genera una imagen con IA
   - Selecciona producto con ProductSelector
   - Ajusta en PreviewPanel
   - Confirma el pedido
   - Procesa el pago

3. **Ejecuta tests adicionales**
   - Modifica `TEST_PRODUCT_DATA` para probar otros productos
   - Prueba con diferentes cantidades
   - Prueba con productos sin talle

---

## 💡 TIPS

- Los tests no eliminan los pedidos creados - revísalos en el panel admin
- Puedes modificar `TEST_IMAGE_URL` para usar imágenes reales
- El test de pago (Mercado Pago) es opcional y puede fallar sin credenciales
- Usa `npm run test:watch` para ejecutar tests automáticamente al hacer cambios

---

## ✅ VERIFICACIÓN FINAL

Antes de ejecutar, verifica:

- [ ] Backend FastAPI corriendo en puerto 8000
- [ ] SQL Server accesible
- [ ] Usuario de prueba existe en BD
- [ ] Variante de prueba existe en BD
- [ ] Node.js y npm instalados
- [ ] Dependencias instaladas (`npm install`)

---

## 📞 SOPORTE

Si encuentras problemas:

1. Revisa los logs del backend (consola donde corre `app_v2.py`)
2. Revisa los logs del test (consola o navegador)
3. Verifica la configuración en SQL Server
4. Asegúrate de tener datos de prueba válidos

---

**¡Listo! Ahora puedes ejecutar los tests y verificar que el flujo de pedidos funciona correctamente.** 🎉
