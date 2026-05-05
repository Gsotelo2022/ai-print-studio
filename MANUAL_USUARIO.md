# AI Print Studio - Manual de Usuario

**Versión:** 2.0  
**Fecha:** Mayo 2026  
**Sistema de Pedidos con Inteligencia Artificial**

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Instalación y Configuración](#instalación-y-configuración)
4. [Inicio Rápido](#inicio-rápido)
5. [Guía del Cliente](#guía-del-cliente)
6. [Guía del Administrador](#guía-del-administrador)
7. [Agentes de Inteligencia Artificial](#agentes-de-inteligencia-artificial)
8. [Resolución de Problemas](#resolución-de-problemas)
9. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## 📖 Introducción

### ¿Qué es AI Print Studio?

AI Print Studio es una plataforma web innovadora que permite a los clientes diseñar y pedir productos personalizados utilizando imágenes propias o generadas con inteligencia artificial. El sistema combina tecnologías de última generación para ofrecer una experiencia completa de personalización de productos.

### Productos Disponibles

- 👕 **Remeras** (diferentes talles y colores)
- 🧥 **Buzos** (personalizables)
- ☕ **Tazas** (varios estilos)
- 🎒 Y muchos más productos personalizables

### Características Principales

✅ **Generación de Imágenes con IA**: Crea diseños únicos describiendo lo que imaginas  
✅ **Eliminador de Fondos**: Quita el fondo de tus imágenes automáticamente  
✅ **Sistema de Descuentos Inteligente**: Descuentos automáticos por cantidad y antigüedad  
✅ **Chatbot de Soporte**: Asistente virtual que responde tus consultas 24/7  
✅ **Panel de Administración**: Gestión completa de pedidos, productos y clientes  
✅ **Pago Online**: Integración con Mercado Pago para pagos seguros  
✅ **Galería Personal**: Guarda todos tus diseños para reutilizarlos

---

## 💻 Requisitos del Sistema

### Hardware Mínimo

- **Procesador**: Intel Core i5 o equivalente
- **RAM**: 8 GB (16 GB recomendado para agentes IA)
- **Disco**: 10 GB espacio libre
- **Red**: Conexión a internet estable

### Software Requerido

#### Esenciales (Obligatorios)

1. **Python 3.10+**
   - Descargar desde: https://www.python.org/downloads/
   - Marcar "Add Python to PATH" durante instalación

2. **Node.js 18+**
   - Descargar desde: https://nodejs.org/
   - Incluye npm automáticamente

3. **Git**
   - Descargar desde: https://git-scm.com/

#### Opcionales (Según Funcionalidad)

4. **Ollama** (para agentes IA)
   - Descargar desde: https://ollama.com
   - Modelo requerido: `qwen2.5:1.5b` (~1 GB)

5. **PostgreSQL** (para producción)
   - Descargar desde: https://www.postgresql.org/
   - En desarrollo se usa SQLite (no requiere instalación)

### Navegadores Compatibles

- ✅ Google Chrome (recomendado)
- ✅ Microsoft Edge
- ✅ Firefox
- ✅ Safari

---

## ⚙️ Instalación y Configuración

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/ai-print-studio.git
cd ai-print-studio
```

### Paso 2: Configurar Variables de Entorno

1. Copiar el archivo de ejemplo:
```bash
copy .env.example .env
```

2. Editar `.env` con tus valores:

```env
# Base de Datos PostgreSQL (Producción)
PG_HOST=127.0.0.1
PG_PORT=5432
PG_DB=PrendeteRock
PG_USER=postgres
PG_PASSWORD=tu_password_segura

# JWT Autenticación
JWT_SECRET=genera_una_clave_secreta_aleatoria_aqui

# APIs Externas
REPLICATE_API_TOKEN=r8_tu_token_replicate
REMOVE_BG_API_KEY=tu_clave_removebg
MERCADOPAGO_ACCESS_TOKEN=TEST-tu_token_mercadopago

# CORS (no modificar en desarrollo)
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Ollama (no modificar)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:1.5b
```

#### Obtener API Keys

**Replicate** (generación de imágenes):
1. Registrarse en https://replicate.com/
2. Ir a "Account" → "API Tokens"
3. Crear o copiar token existente
4. Copiar en `.env` como `REPLICATE_API_TOKEN`

**Remove.bg** (eliminar fondos):
1. Registrarse en https://www.remove.bg/api
2. Plan gratuito: 50 imágenes/mes
3. Copiar API key en `.env` como `REMOVE_BG_API_KEY`

**Mercado Pago** (pagos online):
1. Crear cuenta en https://www.mercadopago.com.ar/developers
2. Ir a "Tus credenciales"
3. Usar "Credenciales de prueba" para desarrollo
4. Copiar "Access Token" en `.env`

### Paso 3: Instalar Dependencias

#### Backend Python
```bash
cd backend\api_python
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cd ..\..
```

#### Backend Node.js
```bash
cd backend
npm install
cd ..
```

#### Frontend Vue.js
```bash
cd frontend
npm install
cd ..
```

### Paso 4: Configurar Base de Datos

#### Opción A: SQLite (Desarrollo - Recomendado)

1. Crear directorio:
```bash
mkdir backend\db
```

2. El archivo `prendeterock.db` se creará automáticamente al iniciar la API

3. Importar datos iniciales:
```bash
cd backend\api_python
python -c "from db import init_db; init_db()"
```

#### Opción B: PostgreSQL (Producción)

1. Crear base de datos:
```sql
CREATE DATABASE PrendeteRock;
```

2. Ejecutar script de creación:
```bash
psql -U postgres -d PrendeteRock -f backend\db\Base-de-datos.sql
```

3. Verificar conexión editando `.env` con credenciales correctas

### Paso 5: Instalar y Configurar Ollama (Opcional)

Si deseas usar los agentes IA (chatbot, optimizador de prompts):

1. **Descargar e instalar Ollama**:
   - Windows: https://ollama.com/download/windows
   - Instalar el ejecutable

2. **Iniciar servicio Ollama**:
```bash
ollama serve
```

3. **Descargar modelo qwen2.5:1.5b**:
```bash
ollama pull qwen2.5:1.5b
```
   - Peso: ~1 GB
   - Tiempo descarga: 5-10 minutos

4. **Verificar instalación**:
```bash
ollama list
```
   Debe aparecer: `qwen2.5:1.5b`

---

## 🚀 Inicio Rápido

### Método 1: Inicio Automático (Recomendado)

Desde la raíz del proyecto, ejecutar:

```bash
RUN.bat
```

Este script iniciará automáticamente:
- ✅ Servicio Ollama
- ✅ API FastAPI (backend Python)
- ✅ Backend Node.js (generación imágenes)
- ✅ Frontend Vue.js
- ✅ Navegador en http://localhost:5173

**⏱ Tiempo de inicio**: 30-60 segundos

### Método 2: Inicio Manual

Si prefieres controlar cada servicio por separado:

#### 1. Iniciar Backend Python
```bash
cd backend\api_python
.venv\Scripts\activate
uvicorn app_v2:app --reload --port 8000
```

#### 2. Iniciar Backend Node.js
```bash
cd backend
npm start
```

#### 3. Iniciar Frontend
```bash
cd frontend
npm run dev
```

#### 4. Iniciar Ollama (si usarás agentes IA)
```bash
ollama serve
```

### Verificar que Todo Funciona

1. Abrir navegador en: http://localhost:5173
2. Deberías ver la página de inicio de AI Print Studio
3. Verificar APIs:
   - API Python: http://localhost:8000/docs
   - Backend Node: http://localhost:3000/health

### Detener el Sistema

```bash
stop.bat
```

O presionar `Ctrl+C` en cada terminal.

---

## 👤 Guía del Cliente

### 1. Registro de Cuenta

#### Crear Nueva Cuenta

1. Ir a http://localhost:5173
2. Clic en **"Registrarme"**
3. Completar formulario:
   - 📧 **Email**: Único, será tu usuario
   - 🔑 **Contraseña**: Mínimo 6 caracteres
   - 👤 **Nombre completo**
4. Clic en **"Crear cuenta"**
5. Sistema confirma registro exitoso

**⚠️ Importante**: El email debe ser único. Si ya existe, aparecerá un error.

### 2. Iniciar Sesión

1. Clic en **"Ingresar"**
2. Ingresar:
   - Email registrado
   - Contraseña
3. Clic en **"Iniciar Sesión"**
4. Serás redirigido al panel principal

**🔒 Seguridad**: 
- Las contraseñas se almacenan encriptadas
- Token JWT válido por 24 horas
- Después de 24h deberás volver a iniciar sesión

### 3. Crear un Diseño

Tienes dos opciones para crear tu diseño personalizado:

#### Opción A: Subir Imagen Propia

1. Desde el panel principal, clic en **"Subir Imagen"**
2. Clic en **"Seleccionar archivo"** o arrastrar imagen
3. Formatos aceptados: **PNG, JPG, JPEG**
4. Tamaño máximo: **10 MB**
5. Vista previa de la imagen
6. **(Opcional)** Clic en **"Quitar fondo"**:
   - Elimina automáticamente el fondo de la imagen
   - Usa tecnología Remove.bg
   - Tarda 5-10 segundos
7. Clic en **"Guardar diseño"**
8. La imagen se guarda en tu galería personal

#### Opción B: Generar con Inteligencia Artificial

1. Clic en **"Generar con IA"**
2. Escribir descripción en español, por ejemplo:
   - *"Un lobo aullando a la luna en un bosque oscuro"*
   - *"Gato naranja astronauta flotando en el espacio"*
   - *"Montañas al atardecer con colores vibrantes"*
3. Clic en **"Optimizar Prompt"** (opcional):
   - El Agente de Prompts mejora tu descripción
   - Traduce al inglés optimizado para IA
   - Agrega keywords de calidad
4. Clic en **"Generar Imagen"**
5. ⏱ Esperar 15-30 segundos (Replicate generando imagen)
6. Ver resultado y guardar en galería

**💡 Tips para Mejores Resultados**:
- Sé específico en la descripción
- Menciona estilo: "realista", "dibujo", "acuarela"
- Incluye colores: "vibrante", "oscuro", "pastel"
- Detalles de ambiente: "bosque", "ciudad", "espacio"

**🤖 Requisito**: El Agente de Prompts debe estar corriendo para optimización automática.

### 4. Seleccionar Producto

1. Una vez guardado el diseño, clic en **"Usar en Producto"**
2. Explorar catálogo de productos:
   - 👕 Remeras
   - 🧥 Buzos
   - ☕ Tazas
   - Y más...
3. Clic en el producto deseado
4. Ver **vista previa** del diseño en el producto

### 5. Elegir Variante y Cantidad

1. **Seleccionar variante**:
   - **Talle**: XS, S, M, L, XL, XXL
   - **Color**: Blanco, Negro, Azul, etc.
2. **Indicar cantidad**: Usar botones + / - o escribir número
3. El sistema calcula automáticamente:
   - Precio unitario
   - Subtotal
   - Descuentos aplicables

### 6. Aplicar Cupón de Descuento

1. Si tienes un código promocional, ingresarlo en **"Código de cupón"**
2. Clic en **"Validar"**
3. El sistema verifica:
   - ✅ Código existe
   - ✅ No está vencido
   - ✅ Tiene usos disponibles
4. Si es válido, muestra:
   - ✅ Descuento aplicado
   - 💰 Nuevo total con descuento

#### Tipos de Descuentos

El sistema combina automáticamente múltiples descuentos:

| Tipo | Descripción | Automático |
|------|-------------|------------|
| **Por Cantidad** | Más unidades = más descuento | ✅ Sí |
| **Cliente Frecuente** | Basado en historial de compras | ✅ Sí |
| **Cupón Promocional** | Códigos entregados por admin | ⚠️ Requiere código |
| **Temporales** | Promociones por fechas especiales | ✅ Sí |

**Ejemplo de Descuentos por Cantidad**:
- 1-4 unidades: 0%
- 5-9 unidades: 10%
- 10-19 unidades: 15%
- 20+ unidades: 20%

**🔝 Descuento Máximo**: 35% combinado (sumatoria de todos los descuentos)

### 7. Finalizar Pedido

Tienes dos opciones para completar la compra:

#### Opción A: Pagar Ahora con Mercado Pago

1. Clic en **"Pagar con Mercado Pago"**
2. El sistema:
   - Crea el pedido en base de datos
   - Genera link de pago
   - Redirige a Mercado Pago
3. Completar pago en Mercado Pago:
   - Tarjeta de crédito/débito
   - Transferencia bancaria
   - Efectivo (Rapipago/Pago Fácil)
4. Tras pago exitoso, serás redirigido a página de éxito
5. Estado del pedido: **"Pagado"**

#### Opción B: Pagar Después

1. Clic en **"Enviar Pedido sin Pagar"**
2. El pedido se guarda con estado: **"Pendiente de pago"**
3. Podrás pagarlo más tarde desde **"Mis Pedidos"**
4. El administrador ve el pedido y puede contactarte

### 8. Mis Diseños

Acceder a tu galería personal:

1. Menú lateral → **"Mis Diseños"**
2. Ver todos tus diseños guardados:
   - 🖼️ Miniaturas de cada imagen
   - 📅 Fecha de creación
   - 🏷️ Origen: Subida / Generada con IA
3. Acciones disponibles:
   - 👁️ **Ver**: Ampliar imagen
   - 🛍️ **Usar en nuevo pedido**: Crear producto con ese diseño
   - 🗑️ **Eliminar**: Borrar de galería

### 9. Mis Pedidos

Ver historial de pedidos:

1. Menú lateral → **"Mis Pedidos"**
2. Lista de todos tus pedidos:
   - 📦 Número de pedido
   - 🖼️ Diseño usado
   - 🛍️ Producto
   - 📊 Cantidad
   - 💰 Total
   - 📅 Fecha
   - 🔄 Estado actual

#### Estados del Pedido

| Estado | Descripción | Acción Cliente |
|--------|-------------|----------------|
| 🟡 **Pendiente** | Pedido recibido, esperando proceso | Esperar |
| 🔵 **En Proceso** | Fabricando producto | Esperar |
| 🟢 **Listo** | Producto terminado, listo para entrega | Coordinar retiro |
| ✅ **Entregado** | Pedido completado | Ninguna |

#### Estados de Pago

| Estado | Descripción |
|--------|-------------|
| 🟡 **Pendiente** | Esperando pago |
| ✅ **Pagado** | Pago confirmado |
| 🔴 **Reembolsado** | Dinero devuelto |

### 10. Chat de Soporte (Chatbot)

Consultar al asistente virtual:

1. Clic en ícono de **chat** (esquina inferior derecha)
2. Escribir tu consulta, ejemplos:
   - *"¿Cuánto cuesta una remera?"*
   - *"¿Cuánto tarda el envío?"*
   - *"¿Cuál es el estado de mi pedido #123?"*
   - *"¿Tienen descuentos por cantidad?"*
3. El chatbot responde instantáneamente
4. Si no entiende, pregunta diferente o más específica

**🤖 Tecnología**: 
- Primero busca en base de preguntas frecuentes (FAQ)
- Si no encuentra, usa Ollama para generar respuesta

**⚠️ Requisito**: El Agente de Pedidos debe estar corriendo.

---

## 🔧 Guía del Administrador

### Acceso al Panel de Administración

1. Iniciar sesión con cuenta de administrador
2. El sistema detecta automáticamente el rol
3. Redirige al **Dashboard de Administración**

**👤 Usuario Admin por Defecto**:
- Email: `admin@prendeterock.com`
- Contraseña: `admin123`
- ⚠️ Cambiar contraseña tras primer ingreso

### Dashboard Principal

El dashboard muestra métricas en tiempo real:

#### Tarjetas de Resumen
- 📊 **Total Pedidos**: Cantidad de pedidos del período
- 💰 **Ingresos Totales**: Suma de ventas
- 👥 **Nuevos Clientes**: Registros recientes
- 📦 **Pedidos Pendientes**: Requieren atención

#### Gráficos

1. **Pedidos por Estado** (Torta):
   - Pendientes
   - En Proceso
   - Listos
   - Entregados

2. **Evolución de Ventas** (Línea):
   - Ingresos por día/semana/mes
   - Filtrable por rango de fechas

3. **Productos Más Vendidos** (Barras):
   - Top 10 productos
   - Cantidad de unidades vendidas

#### Filtros Disponibles
- 📅 **Rango de fechas**: Hoy, Semana, Mes, Personalizado
- 🔄 **Estado**: Todos, Pendientes, Completados
- 💳 **Estado pago**: Todos, Pagados, Pendientes

#### Exportar Datos
- Clic en **"Exportar"** (botón superior derecha)
- Formatos: CSV, Excel
- Incluye todos los datos filtrados

### Gestión de Pedidos

Acceder: Menú lateral → **"Pedidos"**

#### Ver Todos los Pedidos

Tabla con información completa:
- ID Pedido
- Cliente (nombre + email)
- Producto + Variante
- Cantidad
- Total (con descuentos aplicados)
- Estado
- Estado Pago
- Fecha
- Acciones

#### Filtrar Pedidos

Usar filtros superiores:
- 🔍 Buscar por cliente o ID
- 📅 Rango de fechas
- 🔄 Estado específico
- 💳 Estado de pago

#### Ver Detalle de Pedido

1. Clic en **icono "ojo"** de un pedido
2. Modal muestra:
   - 🖼️ **Diseño usado** (imagen completa)
   - 👤 **Datos del cliente**
   - 📦 **Detalle del producto**
   - 💰 **Desglose de precios**:
     - Subtotal
     - Descuentos aplicados
     - Total final
   - 📅 **Fechas** (creación y actualización)
   - 📝 **Notas** (si las hay)

#### Cambiar Estado del Pedido

1. Seleccionar pedido
2. Clic en **"Cambiar Estado"**
3. Elegir nuevo estado:
   - 🟡 Pendiente
   - 🔵 En Proceso
   - 🟢 Listo
   - ✅ Entregado
4. **(Opcional)** Agregar nota para el cliente
5. Clic en **"Guardar"**
6. 📧 El cliente recibe notificación (si está configurado)

#### Cambiar Estado de Pago

1. Seleccionar pedido
2. Clic en **"Estado Pago"**
3. Elegir:
   - 🟡 Pendiente
   - ✅ Pagado
   - 🔴 Reembolsado
4. Clic en **"Guardar"**

#### Eliminar/Cancelar Pedido

1. Clic en **icono "basura"**
2. Confirmar eliminación
3. ⚠️ **Atención**: Esto no elimina el registro, solo lo marca como cancelado

### Gestión de Productos

Acceder: Menú lateral → **"Productos"**

#### Ver Catálogo Completo

Tabla con todos los productos:
- Imagen (mockup)
- Nombre
- Tipo
- Precio Base
- Variantes disponibles
- Estado (Activo/Inactivo)
- Acciones

#### Crear Nuevo Producto

1. Clic en **"+ Nuevo Producto"**
2. Completar formulario:
   
   **Información Básica**:
   - 📝 **Nombre**: Ej. "Remera Premium"
   - 🏷️ **Tipo**: Remera/Buzo/Taza/Otro
   - 💰 **Precio Base**: Precio unitario
   - 📄 **Descripción**: Detalles del producto
   
   **Variantes**:
   - Clic en **"+ Agregar Variante"**
   - Tipo: Talle/Color/Material
   - Valor: S, M, L / Blanco, Negro / etc.
   - Precio adicional (opcional)
   - Repetir para cada variante
   
   **Mockup**:
   - Subir imagen del producto sin diseño
   - Formato: PNG con transparencia
   - Tamaño recomendado: 1000x1000 px
   
3. Clic en **"Crear Producto"**
4. Producto disponible inmediatamente para clientes

#### Editar Producto Existente

1. Clic en **icono "lápiz"** del producto
2. Modificar campos deseados:
   - Cambiar precio
   - Agregar/quitar variantes
   - Actualizar descripción
   - Cambiar mockup
3. Clic en **"Guardar Cambios"**

#### Activar/Desactivar Producto

1. Toggle **"Activo"** en la tabla
2. Productos inactivos:
   - ❌ No aparecen en catálogo para clientes
   - ✅ Se conservan en base de datos
   - ✅ Pedidos anteriores no se afectan

**⚠️ Nota**: No se eliminan productos para preservar historial de pedidos.

### Gestión de Clientes

Acceder: Menú lateral → **"Clientes"**

#### Ver Lista de Clientes

Tabla con todos los usuarios registrados:
- ID Cliente
- Nombre
- Email
- Fecha Registro
- Total Pedidos
- Total Gastado
- Estado (Activo/Bloqueado)
- Acciones

#### Ver Detalle de Cliente

1. Clic en **icono "ojo"** del cliente
2. Modal muestra:
   
   **Información Personal**:
   - 👤 Nombre completo
   - 📧 Email
   - 📞 Teléfono
   - 📅 Fecha registro
   
   **Estadísticas**:
   - 📦 Total pedidos realizados
   - 💰 Total gastado
   - 📊 Descuento promedio obtenido
   - 🏆 Tipo cliente (Nuevo/Regular/VIP)
   
   **Historial de Pedidos**:
   - Lista completa de pedidos
   - Clic en pedido para ver detalle

#### Editar Datos de Cliente

1. Clic en **icono "lápiz"**
2. Modificar:
   - Nombre
   - Email (debe ser único)
   - Teléfono
   - Dirección
3. Clic en **"Guardar"**

#### Bloquear/Desbloquear Cliente

1. Clic en **toggle "Activo"**
2. Cliente bloqueado:
   - ❌ No puede iniciar sesión
   - ❌ No puede hacer pedidos
   - ✅ Datos se conservan
   - ✅ Reversible en cualquier momento

**⚠️ Importante**: No se pueden eliminar clientes para preservar integridad del sistema.

### Gestión de Cupones

Acceder: Menú lateral → **"Cupones"**

#### Ver Lista de Cupones

Tabla con todos los cupones:
- Código
- Descuento (%)
- Fecha Inicio
- Fecha Vencimiento
- Usos (actuales/máximos)
- Estado (Activo/Vencido)
- Acciones

#### Crear Nuevo Cupón

1. Clic en **"+ Nuevo Cupón"**
2. Completar formulario:
   
   **Código**:
   - Texto único (ej: `VERANO2026`)
   - Solo mayúsculas y números
   - Sin espacios
   
   **Descuento**:
   - Porcentaje: 5% a 35%
   - ⚠️ Máximo 35% (combinado con otros descuentos)
   
   **Validez**:
   - 📅 Fecha inicio
   - 📅 Fecha vencimiento
   - ⏰ Horas específicas (opcional)
   
   **Límites**:
   - Usos máximos totales (0 = ilimitado)
   - Usos por cliente (opcional)
   - Monto mínimo de compra (opcional)
   
   **Restricciones** (opcional):
   - Solo para productos específicos
   - Solo para clientes nuevos
   - Solo para categorías

3. Clic en **"Crear Cupón"**
4. Cupón disponible inmediatamente

#### Editar Cupón Existente

1. Clic en **icono "lápiz"**
2. Modificar:
   - Fechas de validez
   - Usos máximos
   - Restricciones
3. ⚠️ **No se puede**: Cambiar código o porcentaje de cupones ya usados

#### Desactivar Cupón

1. Clic en **toggle "Activo"**
2. Cupón desactivado:
   - ❌ No se puede canjear
   - ✅ Pedidos anteriores no se afectan
   - ✅ Reversible

#### Ver Uso de Cupón

1. Clic en **icono "gráfico"**
2. Ver estadísticas:
   - Total de usos
   - Descuento total otorgado
   - Lista de pedidos que lo usaron
   - Clientes que lo canjearon

### Gestión de Configuración

Acceder: Menú lateral → **"Configuración"**

#### Configuración General

- 🏢 **Nombre del negocio**
- 📧 **Email de contacto**
- 📞 **Teléfono**
- 📍 **Dirección**
- 🕐 **Horarios de atención**

#### Configuración de Descuentos

**Descuentos por Cantidad**:
- Definir rangos y porcentajes
- Ejemplo:
  - 5-9 unidades: 10%
  - 10-19 unidades: 15%
  - 20+ unidades: 20%

**Descuentos por Historial**:
- Cliente Nuevo (0 pedidos): 0%
- Cliente Regular (1-5 pedidos): 5%
- Cliente VIP (6+ pedidos): 10%

**Descuentos Temporales**:
- Crear promociones por fechas
- Ej: "Descuento Black Friday 25%"
- Fecha inicio y fin
- Se aplican automáticamente

#### Configuración de Notificaciones

- ✅ Enviar email al crear pedido
- ✅ Enviar email al cambiar estado
- ✅ Enviar email al confirmar pago
- 📧 Plantillas de emails personalizables

#### Configuración de APIs

Verificar conexión con servicios externos:
- ✅ Replicate (generación imágenes con IA)
- ✅ Remove.bg (quitar fondos)
- ✅ Mercado Pago (pagos)
- ✅ Ollama (agentes IA)

### Exportar Datos

Desde cualquier sección (Pedidos, Clientes, Productos):

1. Aplicar filtros deseados
2. Clic en **"Exportar"**
3. Elegir formato:
   - 📄 **CSV**: Para Excel, hojas de cálculo
   - 📊 **Excel**: Con formato y fórmulas
   - 📋 **JSON**: Para procesamiento programático
4. Archivo se descarga automáticamente

---

## 🤖 Agentes de Inteligencia Artificial

AI Print Studio incluye tres agentes IA autónomos que mejoran la experiencia del usuario.

### Requisito Previo: Ollama

Todos los agentes requieren que **Ollama** esté instalado y corriendo.

#### Instalar Ollama

1. **Descargar**:
   - Windows: https://ollama.com/download/windows
   - Ejecutar instalador

2. **Iniciar servicio**:
```bash
ollama serve
```
   Debe quedar corriendo en segundo plano.

3. **Descargar modelo**:
```bash
ollama pull qwen2.5:1.5b
```
   - Modelo liviano y rápido
   - Peso: ~1 GB
   - Solo se descarga una vez

4. **Verificar**:
```bash
ollama list
```
   Debe aparecer: `qwen2.5:1.5b`

### 1. Agente de Prompts (Port 5004)

#### ¿Qué Hace?

Actúa como un **prompt engineer automático**. Convierte descripciones simples en español en prompts optimizados en inglés para generadores de imágenes con IA.

#### Ejemplo de Transformación

```
Usuario escribe:
"Un perro corriendo en la playa al atardecer"

Agente optimiza:
"Golden retriever dog running on sandy beach during sunset, 
golden hour lighting, ocean waves in background, dynamic motion, 
high quality, detailed fur texture, vibrant colors, 
professional photography, sharp focus, 4k"
```

#### Cómo Activarlo

**Opción A: Automático (con start-all-agentes.bat)**
```bash
cd agentes-Ollama
start-all-agentes.bat
```

**Opción B: Manual**
```bash
cd agentes-Ollama\agente-prompts
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python agente_prompts.py
```

#### Verificar Funcionamiento

1. Abrir: http://localhost:5004/health
2. Debe responder: `{"status": "ok"}`

#### Uso en el Sistema

- El frontend consulta automáticamente este agente
- Cuando usuario genera imagen con IA
- El botón "Optimizar Prompt" usa este servicio
- Si no está corriendo, prompt se envía sin optimizar

### 2. Agente de Pedidos (Port 5003) - Chatbot

#### ¿Qué Hace?

Chatbot de soporte al cliente con sistema **híbrido**:
1. **Primera búsqueda**: Base de preguntas frecuentes (FAQ) usando TF-IDF
2. **Si no encuentra**: Genera respuesta con Ollama

#### Tecnologías

- **Flask**: API REST
- **pandas**: Leer archivo Excel FAQ
- **scikit-learn**: Vectorización TF-IDF y similitud coseno
- **Ollama**: Generación de respuestas contextualizadas

#### Base de Conocimiento (FAQ)

Archivo: `agentes-Ollama/agente-pedidos/faq_sql_ollama.xlsx`

**Estructura del Excel**:
| Pregunta Frecuente | Respuesta | Tipo |
|--------------------|-----------|------|
| ¿Cuánto cuesta una remera? | El precio base de las remeras es $... | cliente |
| ¿Cuánto tarda el envío? | Los envíos tardan entre 3 y 5 días... | cliente |
| ¿Tienen descuentos por cantidad? | Sí, a partir de 5 unidades 10% de descuento... | cliente |

**Personalizar FAQ**:
1. Abrir `faq_sql_ollama.xlsx` en Excel
2. Agregar filas con nuevas preguntas y respuestas
3. Guardar archivo
4. Reiniciar agente

⚠️ **Sin este archivo**, el agente funciona solo con Ollama (respuestas menos precisas).

#### Cómo Activarlo

```bash
cd agentes-Ollama\agente-pedidos
start-agente-pedidos.bat
```

**El script hace automáticamente**:
- Crea entorno virtual
- Instala dependencias
- Carga FAQ (muestra cantidad de preguntas)
- Inicia servidor Flask

#### Verificar Funcionamiento

```bash
curl http://localhost:5003/health
```

Respuesta: `{"status": "ok", "faq_loaded": 42}`

#### Uso en el Sistema

- El ícono de chat en el frontend usa este agente
- Cliente escribe pregunta
- Agente busca en FAQ primero
- Si similitud < 30%, usa Ollama

### 3. Agente de Cupones (Port 5001) - Descuentos

#### ¿Qué Hace?

Gestiona toda la **lógica de descuentos** del sistema. Calcula y combina múltiples tipos de descuentos respetando el límite del 35%.

#### Tipos de Descuentos

1. **Por Cantidad**:
   - Automático
   - Basado en unidades del pedido
   - Ejemplo: 10 remeras = 15% descuento

2. **Por Historial**:
   - Automático
   - Basado en pedidos anteriores del cliente
   - Cliente VIP (6+ pedidos) = 10% extra

3. **Cupones Manuales**:
   - Requiere código
   - Creados por administrador
   - Validación de fecha y usos

4. **Temporales**:
   - Automático
   - Promociones por fecha
   - Ej: Black Friday, Navidad

#### Cálculo de Descuento Combinado

```
Pedido:
- 10 remeras
- Cliente con 8 pedidos previos
- Cupón "VERANO2026" (15%)
- Promoción temporal activa (10%)

Cálculos:
- Descuento cantidad (10 unidades): 15%
- Descuento VIP (8 pedidos): 10%
- Cupón VERANO2026: 15%
- Descuento temporal: 10%
- SUMA: 50%

👉 LÍMITE: 35% (ajustado automáticamente)

Precio original: $10,000
Descuento aplicado: $3,500 (35%)
Total final: $6,500
```

#### Requisito: PostgreSQL

Este agente requiere **PostgreSQL** para consultar historial de clientes.

**Alternativa en Desarrollo**:
- Con SQLite, el agente funciona parcialmente
- Descuentos por cantidad y cupones: ✅ Funcionan
- Descuento por historial: ❌ No funciona

#### Cómo Activarlo

1. **Configurar PostgreSQL en .env**:
```env
PG_HOST=127.0.0.1
PG_PORT=5432
PG_DB=PrendeteRock
PG_USER=postgres
PG_PASSWORD=tu_password
```

2. **Iniciar agente**:
```bash
cd agentes-Ollama\agente-cupones
start-agente-descuentos.bat
```

#### Verificar Funcionamiento

```bash
curl http://localhost:5001/health
```

Respuesta:
```json
{
  "status": "ok",
  "database": "connected",
  "max_descuento": 35
}
```

#### Uso en el Sistema

- El frontend consulta este agente automáticamente
- Cuando cliente llega a checkout
- Calcula descuento total antes de mostrar precio final
- Aplica todos los descuentos combinados

### Iniciar Todos los Agentes

Para iniciar los tres agentes con un solo comando:

```bash
cd agentes-Ollama
start-all-agentes.bat
```

**Este script abre 3 ventanas terminales**:
1. Agente de Cupones (Port 5001)
2. Agente de Prompts (Port 5004)
3. ⚠️ **No incluye** Agente de Pedidos (iniciarlo por separado)

**Verificar todos los agentes**:
```bash
curl http://localhost:5001/health
curl http://localhost:5003/health
curl http://localhost:5004/health
```

---

## 🔧 Resolución de Problemas

### Problemas Comunes

#### 1. "Puerto ya en uso"

**Error**:
```
Error: listen EADDRINUSE: address already in use :::5173
```

**Solución**:
- Verificar si ya hay una instancia corriendo
- Windows: Abrir "Administrador de Tareas" → Buscar proceso Node/Python → Finalizar
- O cambiar puerto en `vite.config.js` (frontend) o comandos de inicio

#### 2. "Ollama no encontrado"

**Error**:
```
Connection refused: http://localhost:11434
```

**Solución**:
1. Verificar que Ollama esté instalado:
```bash
ollama --version
```

2. Iniciar servicio:
```bash
ollama serve
```

3. Verificar que esté corriendo:
```bash
ollama list
```

#### 3. "Modelo no encontrado"

**Error**:
```
Error: model qwen2.5:1.5b not found
```

**Solución**:
```bash
ollama pull qwen2.5:1.5b
```

Esperar 5-10 minutos para descarga.

#### 4. "Error de base de datos"

**Error**:
```
Database connection failed
```

**Solución A (SQLite)**:
- Verificar que existe carpeta `backend/db/`
- Crear si no existe: `mkdir backend\db`
- Reiniciar API, debería crear archivo automáticamente

**Solución B (PostgreSQL)**:
1. Verificar que PostgreSQL esté corriendo
2. Verificar credenciales en `.env`
3. Probar conexión:
```bash
psql -U postgres -d PrendeteRock
```

#### 5. "API Key inválida"

**Error**:
```
Replicate API: 401 Unauthorized
```

**Solución**:
1. Verificar `.env` tiene `REPLICATE_API_TOKEN`
2. Verificar que el token sea válido en https://replicate.com/account/api-tokens
3. Reiniciar backend Node.js:
```bash
cd backend
npm start
```

#### 6. "No genera imágenes con IA"

**Posibles causas**:
- ❌ Backend Node.js no está corriendo
- ❌ API Token de Replicate inválido o sin créditos
- ❌ Prompt muy largo (>200 caracteres)

**Verificar**:
1. Backend Node corriendo: http://localhost:3000/health
2. API Key en `.env`
3. Ver logs en terminal de Node.js

#### 7. "El chatbot no responde"

**Posibles causas**:
- ❌ Agente de Pedidos no está corriendo
- ❌ Ollama no está activo
- ❌ Archivo FAQ falta

**Solución**:
1. Verificar Ollama:
```bash
ollama serve
```

2. Iniciar agente:
```bash
cd agentes-Ollama\agente-pedidos
start-agente-pedidos.bat
```

3. Verificar que cargue FAQ:
   - Al iniciar debe mostrar: "✅ FAQ cargado: X preguntas"
   - Si no, verificar que existe `faq_sql_ollama.xlsx`

#### 8. "Descuentos no se aplican"

**Posibles causas**:
- ❌ Agente de Cupones no está corriendo
- ❌ PostgreSQL no conectado (si usas historial)
- ❌ Cupón vencido o sin usos disponibles

**Solución**:
1. Verificar agente:
```bash
curl http://localhost:5001/health
```

2. Ver logs del agente en su terminal

3. Verificar cupón en panel admin:
   - Fecha vencimiento
   - Usos restantes
   - Estado activo

#### 9. "Mercado Pago no funciona"

**Posibles causas**:
- ❌ Token no configurado en `.env`
- ❌ Token expirado
- ❌ Usando token de producción en desarrollo

**Solución**:
1. Obtener credenciales de prueba: https://www.mercadopago.com.ar/developers
2. Copiar "Access Token" de **modo sandbox**
3. Actualizar `.env`:
```env
MERCADOPAGO_ACCESS_TOKEN=TEST-tu_token_aqui
```
4. Reiniciar API FastAPI

#### 10. "No se puede eliminar el fondo de imagen"

**Posibles causas**:
- ❌ API Key de Remove.bg no configurada
- ❌ Sin créditos en cuenta Remove.bg
- ❌ Imagen muy grande (>10 MB)

**Solución**:
1. Verificar `.env`:
```env
REMOVE_BG_API_KEY=tu_clave_aqui
```

2. Verificar créditos: https://www.remove.bg/dashboard
   - Plan gratuito: 50 imágenes/mes

3. Optimizar imagen:
   - Reducir tamaño/resolución
   - Convertir a PNG/JPG

### Logs y Depuración

#### Ver Logs del Backend Python

```bash
cd backend\api_python\logs
type app.log
```

#### Ver Logs en Tiempo Real

**Backend Python**:
- Los logs aparecen en la terminal donde se ejecuta `uvicorn`

**Backend Node.js**:
- Los logs aparecen en la terminal donde se ejecuta `npm start`

**Agentes IA**:
- Cada agente muestra logs en su terminal

#### Activar Modo Debug

**Backend Python** (`app_v2.py`):
```python
# Cambiar nivel de logging
logging.basicConfig(level=logging.DEBUG)
```

**Frontend Vue**:
```javascript
// En main.js, agregar:
import { createApp } from 'vue'
createApp(App).config.devtools = true
```

---

## ❓ Preguntas Frecuentes

### Generales

**¿Necesito instalar todo para usar el sistema?**
- Frontend, Backend Python y Node.js: **SÍ, obligatorio**
- Ollama y agentes IA: **NO, opcional** (pero mejora mucho la experiencia)
- PostgreSQL: **NO** (en desarrollo usa SQLite automáticamente)

**¿Funciona en Mac/Linux?**
- La mayoría del código **sí**
- Los archivos `.bat` son solo Windows
- En Mac/Linux usar comandos equivalentes sin `.bat`

**¿Puedo usar en producción?**
- **Sí**, pero tomar precauciones:
  - Cambiar `JWT_SECRET` en `.env`
  - Usar PostgreSQL en vez de SQLite
  - Usar tokens de producción de APIs externas
  - Configurar HTTPS
  - Activar límites de rate limiting

### Cliente

**¿Puedo editar una imagen después de subirla?**
- No directamente en el sistema
- Puedes:
  - Quitar el fondo (botón "Eliminar fondo")
  - Usar software externo y subir nuevamente

**¿Cuántas imágenes puedo generar con IA?**
- Depende de tu plan de Replicate
- Incluye créditos gratuitos al inicio
- Plan pagado: según uso/créditos comprados

**¿Los descuentos se acumulan?**
- **Sí**, todos los descuentos se suman
- **Límite**: 35% máximo combinado

**¿Puedo cancelar un pedido ya pagado?**
- Contactar al administrador
- El admin puede cambiar estado a "Reembolsado"

**¿Cuánto demora elaborar mi pedido?**
- Depende del producto y cantidad
- Típico: 3-5 días hábiles
- Ver estado en "Mis Pedidos"

### Administrador

**¿Cómo cambio la contraseña del admin?**
1. Iniciar sesión como admin
2. Ir a "Configuración" → "Mi Cuenta"
3. Cambiar contraseña
4. Guardar

**¿Puedo importar productos en lote?**
- No hay función nativa actualmente
- Opción: Usar script SQL para insertar en tabla `productos`

**¿Las estadísticas son en tiempo real?**
- **Sí**, se consultan directamente de la base de datos
- Al filtrar o refrescar, datos se actualizan

**¿Puedo personalizar las plantillas de email?**
- Sí, en "Configuración" → "Notificaciones"
- Editar HTML de plantillas
- Variables disponibles: `{nombre}`, `{pedido_id}`, `{total}`

### Técnicas

**¿Qué versión de Python necesito?**
- Mínimo: Python 3.10
- Recomendado: Python 3.11 o 3.12

**¿Puedo usar otra IA en vez de Ollama?**
- **Sí**, modificar código de agentes
- Opciones: OpenAI GPT, Anthropic Claude, etc.
- Requiere cambios en `agente_prompts.py` y `agente_pedidos.py`

**¿Cómo hago backup de la base de datos?**

**SQLite**:
```bash
copy backend\db\prendeterock.db backup\prendeterock_backup.db
```

**PostgreSQL**:
```bash
pg_dump -U postgres PrendeteRock > backup.sql
```

**¿Cómo restauro un backup?**

**SQLite**:
```bash
copy backup\prendeterock_backup.db backend\db\prendeterock.db
```

**PostgreSQL**:
```bash
psql -U postgres -d PrendeteRock < backup.sql
```

**¿Cómo actualizo el sistema a nueva versión?**
1. Hacer backup de base de datos
2. Hacer `git pull` de la rama principal
3. Actualizar dependencias:
```bash
pip install -r backend/api_python/requirements.txt --upgrade
cd backend && npm install
cd ../frontend && npm install
```
4. Revisar changelog para cambios en `.env`
5. Reiniciar servicios

---

## 📞 Soporte

### Documentación Adicional

- **Estructura Técnica**: Ver `ESTRUCTURA_PROYECTO.md`
- **API Docs**: http://localhost:8000/docs (cuando API esté corriendo)
- **Código Fuente**: Revisar comentarios en archivos `.py` y `.vue`

### Ayuda

Si encuentras problemas no documentados:
1. Revisar logs de los servicios
2. Verificar configuración `.env`
3. Consultar FAQ en este manual
4. Contactar a soporte técnico

---

## 📄 Información de Versión

**Versión Actual**: 2.0  
**Última Actualización**: Mayo 2026  
**Compatibilidad API**: 2.1.0

### Changelog

**v2.0 (Mayo 2026)**:
- ✅ Integración con Ollama (qwen2.5:1.5b)
- ✅ Tres agentes IA independientes
- ✅ Sistema de descuentos combinados
- ✅ Chatbot con búsqueda FAQ + IA
- ✅ Dashboard administrador mejorado
- ✅ Integración Mercado Pago
- ✅ Eliminador de fondos con Remove.bg
- ✅ Generación de imágenes con Replicate (Flux Schnell)

**v1.0 (2025)**:
- Sistema básico de pedidos
- Generación de imágenes con Stability AI
- Panel de administración simple

---

## 📝 Licencia

**AI Print Studio**  
© 2026 - Todos los derechos reservados

Este software es de uso interno. Consultar con el administrador del sistema para términos de uso específicos.

---

**Fin del Manual de Usuario**  
Para información técnica detallada, consultar `ESTRUCTURA_PROYECTO.md`
