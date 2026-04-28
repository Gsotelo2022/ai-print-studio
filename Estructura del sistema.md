# Estructura del sistema

Este documento describe la arquitectura y el flujo de funcionamiento del sistema AI Print Studio, tanto para el cliente (usuarios finales) como para el administrador (panel de gestión).

---

## 1. Arquitectura general

- **Frontend:** SPA desarrollada en Vue.js (ubicada en `/frontend`).
- **Backend:** API REST construida con FastAPI (ubicada en `/backend/api_python/app_v2.py`).
- **Base de datos:** SQL Server (`PrendeteRock`).
- **Scripts y utilidades:** Herramientas para migración, limpieza y pruebas en `/database`, `/ai-print-studio` y subcarpetas.

---

## 2. Flujo del lado del cliente (usuario final)

1. **Registro y autenticación:**
   - El usuario se registra o inicia sesión desde la interfaz de cliente.
   - El frontend envía los datos a `/api/register` o `/api/login`.
   - El backend valida, crea el usuario y responde con los datos necesarios.

2. **Navegación y catálogo:**
   - El usuario navega por el catálogo de productos y variantes.
   - El frontend consulta `/api/productos` para obtener la información.

3. **Creación de pedidos:**
   - El usuario selecciona productos, variantes y sube diseños.
   - El frontend envía el pedido a `/api/create-order`.
   - El backend valida stock, calcula totales y registra el pedido.

4. **Seguimiento:**
   - El usuario puede consultar el estado de sus pedidos.

---

## 3. Flujo del lado del administrador (panel de gestión)

1. **Acceso al panel:**
   - El administrador accede a la interfaz de administración (rutas protegidas).

2. **Gestión de clientes:**
   - Visualiza, busca y edita clientes desde el componente `GestionClientes.vue`.
   - El frontend consulta `/api/admin/clientes` para obtener la lista.
   - Para editar, envía un `PUT` a `/api/admin/clientes/{id}` con los datos modificados.
   - El backend valida y actualiza la información en la base de datos.

3. **Gestión de productos y pedidos:**
   - Puede ver, filtrar y modificar productos y pedidos desde los componentes correspondientes.
   - Endpoints principales:
     - `/api/admin/productos` (GET)
     - `/api/admin/pedidos` (GET)
     - `/api/admin/pedidos/{id}` (GET)
     - `/api/admin/pedidos/{id}/estado` (PUT)

4. **Gestión de cupones:**
   - Visualiza, crea y modifica cupones de descuento desde el componente `GestionCupones.vue`.
   - El frontend consulta `/api/admin/cupones` para obtener la lista.
   - Para crear, envía un `POST` a `/api/admin/cupones` con los datos del cupón.
   - Para editar, envía un `PUT` a `/api/admin/cupones/{id}`.
   - Para estadísticas, consulta `/api/admin/cupones/estadisticas`.
   - Se integra con el Agente de Cupones (puerto 5003) para funcionalidades avanzadas.
   - Ver documentación completa: [Agente de Cupones README](ai-print-studio/agentes-Ollama/agente-cupones/README.md)

5. **Migraciones y mantenimiento:**
   - Scripts en `/database` y `/ai-print-studio` permiten migrar datos, limpiar registros y mantener la integridad del sistema.

---

## 4. Resumen de carpetas principales

- `/frontend`: Aplicación Vue.js (componentes, vistas, assets, configuración Vite).
- `/database/source`: Backend FastAPI y scripts de migración.
- `/database`: Archivos SQL, backups y utilidades.
- `/ai-print-studio`: Scripts de automatización, limpieza y documentación.

---

## 5. Notas adicionales

- El sistema está preparado para ser extendido con nuevos módulos y agentes.
- El backend implementa CORS para permitir el acceso desde el frontend.
- El sistema de autenticación y bloqueo de cuentas protege el acceso a funciones sensibles.

---

## Explicación global del sistema

AI Print Studio es una plataforma integral para la gestión y venta de productos personalizados, pensada para cubrir todo el ciclo de vida de un pedido, desde la selección y personalización de productos por parte del cliente, hasta la administración y control de pedidos, clientes y productos por parte del equipo administrativo.

El sistema está compuesto por:
- Un frontend moderno y responsivo, que permite a los usuarios navegar, registrarse, personalizar productos, realizar pedidos y hacer seguimiento de los mismos.
- Un backend robusto, que expone una API RESTful para gestionar la lógica de negocio, la autenticación, la administración de usuarios, productos, variantes y pedidos, y la integración con la base de datos.
- Una base de datos relacional que almacena toda la información relevante del negocio, asegurando integridad y consistencia.
- Herramientas y scripts de soporte para migraciones, limpieza, pruebas y mantenimiento, facilitando la evolución y el soporte del sistema.

El objetivo es ofrecer una experiencia fluida y segura tanto para los clientes como para los administradores, permitiendo escalar y adaptar el sistema a nuevas necesidades comerciales o técnicas.

---

**Actualizado:** 28/04/2026

## 6. Agentes IA (Ollama)

El sistema implementa tres agentes de Inteligencia Artificial que operan de forma asincrónica:

| Agente | Puerto | Función | Documentación |
|--------|--------|---------|---------------|
| **Agente de Productos** | 5001 | Catálogo dinámico desde BD | [Ver README](ai-print-studio/agentes-Ollama/agente-productos/README.md) |
| **Agente de Precios** | 5002 | Actualización de precios vía IA | [Ver README](ai-print-studio/agentes-Ollama/agente-precios/README.md) |
| **Agente de Cupones** | 5003 | Gestión inteligente de descuentos | [Ver README](ai-print-studio/agentes-Ollama/agente-cupones/README.md) |

**Nota:** Cada agente incluye documentación técnica completa, endpoints, ejemplos de uso y troubleshooting en su README correspondiente.

---

## 7. Sistema de Cupones para Clientes

### 7.1 Endpoint de Cupones Disponibles

**Endpoint:** `GET /api/cupones/disponibles/{id_cliente}`

**Descripción:** Endpoint inteligente que analiza el perfil del cliente y retorna los cupones disponibles según su historial de compras y comportamiento.

**Características principales:**
- ⚡ Respuesta rápida (solo SQL, sin procesamiento IA)
- 🎯 Perfilado automático del cliente
- 📊 Reglas de negocio integradas
- 🔄 No requiere servicios adicionales

**Reglas de negocio implementadas:**

| Tipo de Cupón | Condición | Ejemplo |
|---------------|-----------|---------|
| **BIENVENIDA/PRIMERA** | Cliente sin compras (total_pedidos = 0) | `BIENVENIDA10`, `PRIMERA20` |
| **FIDELIDAD/VIP** | Cliente con 5+ compras | `FIDELIDAD15`, `VIP20` |
| **REGRESO/VUELVE** | Cliente inactivo (>30 días sin comprar) | `REGRESO25`, `VUELVE10` |
| **ESPECIAL/EXCLUSIVO** | Cliente de alto valor (>$10,000 gastados) | `ESPECIAL30`, `ELITE25` |
| **Cupones genéricos** | Todos los clientes | `VERANO20`, `PROMO15` |

**Estructura de respuesta:**

```json
{
  "success": true,
  "data": {
    "cupones": [
      {
        "id_cupon": 1,
        "codigo": "BIENVENIDA10",
        "descuento": 10,
        "descripcion": "Descuento de bienvenida",
        "expiracion": "2026-05-31",
        "es_limitado": true,
        "usos_restantes": 50,
        "categoria": "primera_compra",
        "razon": "¡Es tu primera compra con nosotros!"
      }
    ],
    "perfil_cliente": {
      "total_pedidos": 0,
      "gasto_total": 0,
      "dias_inactivo": null,
      "es_cliente_nuevo": true,
      "es_cliente_vip": false,
      "ultima_compra": null
    },
    "total": 1,
    "mensaje": "¡Tienes 1 cupón(es) disponible(s)!"
  }
}
```

**Integración en Frontend:**
- ✅ **PreviewPanel.vue** - Badge y modal de cupones disponibles ANTES de confirmar pedido
- ✅ Muestra descuento aplicado en tiempo real
- ✅ Badge mostrando cantidad de cupones disponibles
- ✅ Modal para seleccionar y aplicar cupones
- ✅ Cálculo automático de descuento en el resumen del pedido
- ✅ Mensaje "No tienes cupones disponibles" si no hay cupones

**Flujo de aplicación de cupón:**

1. Usuario llega al **PreviewPanel** (confirmación de pedido)
2. El componente `CuponesDisponibles` carga automáticamente cupones del usuario
3. Si hay cupones: muestra badge "🎟️ Tienes X cupón(es) disponible(s)"
4. Si NO hay cupones: muestra mensaje "😔 No tienes cupones disponibles en este momento"
5. Usuario hace clic en el badge
6. Se abre modal con lista de cupones disponibles
7. Usuario selecciona cupón a aplicar
8. El sistema calcula y muestra:
   - Subtotal original
   - Descuento aplicado (-XX%)
   - Total con descuento
9. Al confirmar pedido, se envía código de cupón al backend
10. Backend valida cupón, aplica descuento y registra uso

**Backend:**
- ✅ Endpoint `/api/create-order` modificado para aceptar cupones
- ✅ Validación completa de cupón (existencia, expiración, usos restantes)
- ✅ Aplicación automática de descuento al total
- ✅ Incremento de contador de usos del cupón
- ✅ Manejo de errores descriptivos

**Ventajas de esta implementación:**
1. **Performance:** Consultas SQL optimizadas (< 50ms)
2. **Escalabilidad:** No depende de agentes IA adicionales
3. **Personalización:** Cada cliente ve cupones relevantes a su perfil
4. **Automatización:** Las reglas se aplican automáticamente
5. **Conversión:** Incentiva primera compra, fidelidad y reactivación
6. **UX:** Usuario siempre ve si tiene cupones disponibles o no

**Ubicación del código:** 
- Frontend: `frontend/src/components/PreviewPanel.vue` (integración de cupones)
- Frontend: `frontend/src/components/CuponesDisponibles.vue` (componente reutilizable)
- Backend: `backend/api_python/app_v2.py` (líneas ~670-820 validación y aplicación)

**Documentación completa:** Ver `PLAN_CUPONES_CLIENTE.md` para guía de implementación detallada.

---

## 8. Sistema de Mis Diseños (Galería de Diseños del Cliente)

### 8.1 Endpoint /api/mis-disenos/{id_usuario}

**Endpoint:** `GET /api/mis-disenos/{id_usuario}`

**Descripción:** Recupera todos los diseños (generados por IA o subidos manualmente) que el usuario ha creado, incluyendo estadísticas de uso y permitiendo reutilizarlos en nuevos pedidos.

**Características principales:**
- 📸 Historial completo de diseños del usuario
- 🔄 Reutilización de diseños sin regenerar
- 📊 Estadísticas de uso (veces usado, último uso)
- 🤖 Diferenciación entre IA y subidos manualmente
- 🖼️ Thumbnails optimizados (200x200px)
- ⚡ Consulta SQL optimizada con LEFT JOINs

**Estructura de respuesta:**

```json
{
  "success": true,
  "data": {
    "disenos": [
      {
        "id_archivo": 13,
        "nombre_original": "diseno_generado.png",
        "ruta_archivo": "uploads/designs/user2_20260428_110353.png",
        "ruta_thumbnail": "uploads/thumbnails/thumb_user2_20260428_110353.png",
        "tipo_mime": "image/png",
        "tamano_kb": 5.08,
        "dimensiones": "1024x1024",
        "es_generado_ia": true,
        "prompt_usado": "Abstract colorful gradient design",
        "fecha_subida": "2026-04-28 11:03:53",
        "estadisticas": {
          "veces_usado": 3,
          "ultimo_uso": "2026-04-28 14:25:10"
        }
      }
    ],
    "total": 7,
    "total_generados_ia": 7,
    "total_subidos": 0
  }
}
```

**SQL Query Implementation:**

```sql
SELECT ad.id_archivo, ad.nombre_original, ad.nombre_almacenado,
       ad.ruta_archivo, ad.ruta_thumbnail, ad.tipo_mime,
       ad.tamano_bytes, ad.ancho_px, ad.alto_px,
       ad.es_generado_ia, ad.fecha_subida,
       COUNT(DISTINCT pi.id_pedido) as veces_usado,
       MAX(p.fecha_pedido) as ultimo_uso
FROM Archivos_Diseno ad
LEFT JOIN Pedidos_Items pi ON ad.id_archivo = pi.archivo_diseno
LEFT JOIN Pedidos p ON pi.id_pedido = p.id_pedido
WHERE ad.id_usuario = ?
GROUP BY [all columns except prompt_usado]
ORDER BY ad.fecha_subida DESC
```

**Nota técnica:** `prompt_usado` (tipo TEXT) no puede incluirse en GROUP BY en SQL Server, por lo que se obtiene con una consulta separada solo para diseños generados por IA.

### 8.2 Componente Frontend: MisDisenosGaleria.vue

**Ubicación:** `frontend/src/components/MisDisenosGaleria.vue`

**Características:**
- 🎨 **Grid responsive** de thumbnails (auto-fill minmax 250px)
- ✨ **Hover effects** con overlay y botón "Usar este diseño"
- 🔍 **Modal de detalle** con imagen completa, prompt, dimensiones, estadísticas
- 🏷️ **Badge IA** para identificar diseños generados por inteligencia artificial
- 🎯 **Filtros dinámicos:**
  - Todos los diseños
  - Solo generados por IA
  - Solo subidos manualmente
- 📊 **Estadísticas globales:**
  - Total de diseños
  - Total generados por IA
  - Total subidos manualmente
- 📅 **Formato de fecha inteligente:**
  - "Hoy" / "Ayer"
  - "Hace X días"
  - "Hace X semanas"
  - Fecha completa para más antiguos

**Integración en App.vue:**

1. Usuario logueado hace clic en **"Mis Diseños"** en el navbar
2. Se muestra `MisDisenosGaleria` con todos sus diseños
3. Usuario puede:
   - **Ver detalles** de cada diseño (click en card)
   - **Reutilizar diseño** (botón en modal o hover overlay)
   - **Filtrar** por tipo de diseño
4. Al seleccionar un diseño para reutilizar:
   - Evento `@design-selected` emite: `{ imagen_url, prompt, id_archivo }`
   - App.vue carga el diseño en `generatedImage`
   - Se cierra la galería y muestra **ProductSelector**
   - Usuario continúa el flujo normal (sin regenerar imagen)

**Flujo de reutilización de diseño:**

```
Mis Diseños → Click "Usar este diseño" → ProductSelector → PreviewPanel → Checkout
```

**Ventajas:**
1. ⚡ **Velocidad:** No necesita regenerar imágenes con IA
2. 💾 **Eficiencia:** Reutiliza archivos ya almacenados
3. 📈 **Conversión:** Facilita pedidos repetidos de diseños exitosos
4. 🎯 **UX:** Usuario ve su historial completo
5. 📊 **Insights:** Estadísticas muestran diseños más populares

**Props del componente:**

```javascript
props: {
  userId: { type: Number, required: true }
}
```

**Eventos emitidos:**

```javascript
emit('design-selected', { imagen_url, prompt, id_archivo })
emit('go-back') // Volver al dashboard
```

**Manejo de errores:**
- ✅ Estado de carga con spinner
- ✅ Mensaje de error con botón "Reintentar"
- ✅ Estado vacío con CTA "Crear nuevo diseño"
- ✅ Placeholder SVG si imagen no carga

**Estado del componente:**

```javascript
const cargando = ref(false)
const error = ref(null)
const disenos = ref([])
const estadisticas = ref({ total: 0, total_generados_ia: 0, total_subidos: 0 })
const filtroActivo = ref('todos')
const disenoSeleccionado = ref(null)
```

**Ubicación del código:**
- Frontend: `frontend/src/components/MisDisenosGaleria.vue` (componente galería)
- Frontend: `frontend/src/App.vue` (integración, líneas ~15 import, ~77 estado, ~134-142 sección, ~456-479 funciones)
- Backend: `backend/api_python/app_v2.py` (líneas ~1271-1358 endpoint)

**Branch actual:** `mis-disenos-cliente`

**Commits relacionados:**
- `5668168` - Feat: Endpoint GET /api/mis-disenos/{id_usuario}
- `919271f` - Feat: Componente MisDisenosGaleria y navegación en App.vue

**Próximos pasos opcionales:**
- [ ] Añadir filtro por rango de fechas
- [ ] Implementar búsqueda por prompt
- [ ] Agregar opción para eliminar diseños no usados
- [ ] Estadísticas de popularidad (diseños más usados)
- [ ] Opción de marcar diseños como favoritos

