# 📘 Manual del Proyecto: AI Print Studio

> **Última actualización:** 22 de abril de 2026  
> **Stack Principal:** Vue 3 + FastAPI + SQL Server + OLLAMA  
> **Propósito:** Plataforma web para diseñar y comprar estampados personalizados con IA

---

## 📋 Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Arquitectura del Proyecto](#arquitectura-del-proyecto)
3. [Estructura de Carpetas](#estructura-de-carpetas)
4. [Tecnologías Utilizadas](#tecnologías-utilizadas)
5. [Flujo de la Aplicación](#flujo-de-la-aplicación)
6. [Componentes Principales](#componentes-principales)
7. [APIs y Endpoints](#apis-y-endpoints)
8. [Base de Datos](#base-de-datos)
9. [Configuración e Instalación](#configuración-e-instalación)
10. [Scripts de Ejecución](#scripts-de-ejecución)
11. [Módulos y Dependencias](#módulos-y-dependencias)
12. [Status del Proyecto](#status-del-proyecto)

---

## Descripción General

**AI Print Studio** (conocido internamente como **Prendete Rock**) es una plataforma educativa que permite a los usuarios:

✨ **Funcionalidades Principales:**
- 🎨 Generar imágenes con IA usando prompts de texto
- 📤 Subir imágenes propias para personalizarlas
- 👕 Seleccionar productos (remeras, tazas, etc.) y variantes (color, talle)
- 👁️ Ver preview del diseño en el producto
- 💳 Realizar pagos a través de Mercado Pago
- 👤 Sistema de autenticación de usuarios (clientes y admins)
- 📋 Gestión de pedidos y historial de compras

**Objetivo Educativo:** Aprender arquitectura web moderna con tecnologías actuales.

---

## Arquitectura del Proyecto

```
┌─────────────────────────────────────────────────────────────┐
│                   CLIENTE (Navegador Web)                   │
│  Vue 3 + Vite | TypeScript-Ready | Responsive Design       │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                 SERVIDOR (Backend)                          │
│       FastAPI (Python) | Express (Node.js Legacy)           │
│                                                              │
│  • Autenticación y autorización                             │
│  • Generación de imágenes (Integration con APIs externas)   │
│  • Gestión de pedidos                                       │
│  • Procesamiento de pagos                                   │
└────────────────────────┬────────────────────────────────────┘
                         │ SQL/ODBC
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                  SQL Server (Base de Datos)                 │
│                                                              │
│  • Usuarios | Productos | Pedidos | Detalles Pedidos        │
└─────────────────────────────────────────────────────────────┘
                         
                    APIs EXTERNAS
                    ├─ Stability AI (generación de imágenes)
                    └─ Mercado Pago (procesamiento de pagos)
```

---

## Estructura de Carpetas

```
ai-print-studio/
│
├── 📁 agentes-Ollama/                   ← Agente IA para productos dinámicos
│   ├── agente_productos.py              ← Flask server con OLLAMA
│   ├── test_agente.py                   ← Test del agente
│   ├── setup_agente.bat                 ← Configuración inicial
│   └── .venv/                           ← Entorno virtual Python
│
├── 📁 frontend/                         ← App Vue 3 + Vite (Cliente Web)
│   ├── index.html                       ← Punto de entrada HTML
│   ├── package.json                     ← Dependencias y scripts npm
│   ├── vite.config.js                   ← Configuración de Vite (build + dev server)
│   └── src/
│       ├── main.js                      ← Inicialización y montaje de Vue
│       ├── App.vue                      ← Componente raíz (orquestador principal)
│       ├── assets/
│       │   ├── styles.css               ← Estilos globales
│       │   └── logo-prendete-rock.jpg   ← Branding
│       ├── components/                  ← Componentes Vue reutilizables
│       │   ├── Login.vue                ← Formulario de ingreso
│       │   ├── CreateUser.vue           ← Formulario de registro
│       │   ├── PromptGenerator.vue      ← Generador de prompts + IA
│       │   ├── ImageUploader.vue        ← Cargador de imágenes
│       │   ├── ProductSelector.vue      ← Selección de productos
│       │   ├── BackgroundRemover.vue    ← Removedor de fondo (rembg)
│       │   ├── PreviewPanel.vue         ← Vista previa del diseño
│       │   ├── CheckoutPanel.vue        ← Carrito y checkout
│       │   ├── HeroShowcase.vue         ← Sección de bienvenida
│       │   ├── UsersList.vue            ← Panel de usuarios (admin)
│       │   └── GenerateImage.vue        ← Wrapper para generación
│       ├── composables/
│       │   └── useApi.js                ← Hook reutilizable para fetch API
│       └── views/
│           └── Success.vue              ← Página de confirmación de pago
│
├── 📁 backend/                          ← API REST en PHP (Legacy)
│   ├── package.json                     ← Node.js (para servidor Express)
│   ├── server.js                        ← Servidor Express.js
│   ├── generateImage.js                 ← Lógica de generación de imágenes
│   ├── index.php                        ← Punto de entrada PHP
│   ├── composer.json                    ← Dependencias PHP (Mercado Pago SDK)
│   ├── config/
│   │   ├── app.php                      ← Claves API (Stability AI, MercadoPago)
│   │   ├── database.php                 ← Configuración de conexión a SQL Server
│   │   └── db.php                       ← Funciones auxiliares de BD
│   ├── api/                             ← Endpoints REST
│   │   ├── login.php                    ← POST: autenticación
│   │   ├── create-user.php              ← POST: registro de usuarios
│   │   ├── generate-image.php           ← POST: genera imagen con Stability AI
│   │   ├── create-order.php             ← POST: crear pedido
│   │   ├── create-payment.php           ← POST: iniciar pago en MercadoPago
│   │   ├── save-payment.php             ← POST: guardar resultado de pago
│   │   ├── remove-background.php        ← POST: quitar fondo de imagen
│   │   └── get-users.php                ← GET: listar usuarios (admin)
│   ├── helpers/
│   │   └── response.php                 ← Funciones para respuestas JSON
│   ├── uploads/                         ← Carpeta de imágenes generadas
│   └── vendor/                          ← Dependencias PHP (autoload, Mercado Pago)
│
├── 📁 backend_fastapi/                  ← API REST en FastAPI (Python) [EN DESARROLLO]
│   └── .venv/                           ← Entorno virtual Python
│
├── 📁 database/                         ← Gestión de Base de Datos
│   ├── estructura-BDD-Prendete-Rock.sql ← Script de creación de tablas
│   ├── insertar-usuarios-prueba-FINAL.sql ← Usuarios de prueba con hash correcto
│   ├── env/                             ← Entorno virtual Python (Legacy)
│   └── source/
│       ├── app.py                       ← FastAPI app principal
│       ├── db.py                        ← Conexión a SQL Server
│       ├── conexion.py                  ← Conexión alternativa
│       ├── init_db.py                   ← Inicialización de BD
│       ├── requirements.txt             ← Dependencias Python
│       ├── .venv/                       ← Entorno virtual para FastAPI
│       ├── test_login.py                ← Tests de autenticación
│       ├── test_register.py             ← Tests de registro
│       ├── test_auth_flow.py            ← Test flujo completo registro+login
│       ├── test_insert_login.py         ← Test inserción directa BD
│       └── test_register_complete.py    ← Test exhaustivo de registro
│
├── 📁 agente-Prompt-Imagenes-Ollama/    ← Proyecto relacionado (Ollama)
│
├── 🔧 Scripts de Configuración y Ejecución
│   ├── RUN.bat                          ← ⭐ Script maestro (inicia todo)
│   ├── stop.bat                         ← Detiene todos los servidores
│   ├── start-all.bat / .ps1             ← Inicia frontend + backend (legacy)
│   ├── start-frontend.ps1               ← Inicia solo Frontend
│   ├── start-backend.ps1                ← Inicia solo Backend
│   ├── install-dependencies.ps1         ← Instala dependencias
│   ├── setup-usuarios.ps1               ← Script de configuración de usuarios
│   ├── diagnostico.ps1                  ← Script de diagnóstico
│   ├── diagnostico-completo.ps1         ← Diagnóstico extendido
│   ├── restart-fastapi.bat              ← Reinicia FastAPI
│   ├── descargar-modelo-ia.bat          ← Descarga modelo OLLAMA
│   ├── generar-usuarios-prueba.py       ← Genera usuarios con hash correcto
│   ├── test-agente-completo.py          ← Test completo del agente IA
│   └── verificar-base-datos.py          ← Verifica conexión y estructura BD
│
├── 📄 Documentación
│   ├── README.md                        ← Documentación principal
│   ├── README-EJECUTAR.txt              ← Guía rápida de ejecución
│   ├── RESUMEN_TESTS_Y_CONFIG.md        ← Resumen de tests y configuración
│   ├── RUN_BAT_GUIA.md                  ← Guía del script RUN.bat
│   ├── REGISTRO_CAMBIOS.md              ← Historial de cambios
│   ├── REGISTRO_QUICKSTART.md           ← Inicio rápido
│   ├── REGISTRO_SOLUCION.md             ← Soluciones a problemas
│   └── SISTEMA_LISTO.md                 ← Estado del sistema
│
└── 📄 MANUAL_PROYECTO.md                 ← Este archivo
```

---

## Tecnologías Utilizadas

### Frontend
| Tecnología | Versión | Propósito |
|------------|---------|----------|
| **Vue** | ^3.4.0 | Framework de UI (reactividad) |
| **Vite** | ^5.0.0 | Build tool y dev server |
| **@vitejs/plugin-vue** | ^5.0.0 | Plugin para soportar archivos .vue |

### Backend (FastAPI - Actual)
| Tecnología | Versión | Propósito |
|------------|---------|----------|
| **FastAPI** | 0.104.1 | Framework web async (APIs REST) |
| **Uvicorn** | 0.24.0 | Servidor ASGI |
| **Pyodbc** | 5.3.0 | Conector a SQL Server |
| **Pydantic** | 2.5.0 | Validación de datos |
| **Pillow** | ≥10.0.0 | Procesamiento de imágenes |
| **rembg** | 2.0.56 | Removedor de fondo de imágenes |
| **python-multipart** | ≥0.0.6 | Manejo de uploads |

### Backend (PHP - Legacy)
| Tecnología | Propósito |
|------------|----------|
| **PHP** | 8.0+ (con pdo_sqlsrv, curl, json) |
| **Express.js** | Servidor para Node.js backend |
| **Mercado Pago SDK** | Procesamiento de pagos |

### Base de Datos
| Componente | Descripción |
|-----------|------------|
| **SQL Server** | RDBMS principal |
| **ODBC/PyODBC** | Driver de conexión Python |
| **PDO** | Driver de conexión PHP |

### APIs Externas
| Servicio | Uso |
|----------|-----|
| **Stability AI** | Generación de imágenes a partir de prompts |
| **Mercado Pago** | Procesamiento seguro de pagos |

---

## Flujo de la Aplicación

### User Journey: De promedio a compra

```
┌─────────────────────────────────────────────────────────────────┐
│ LÍNEA DE TIEMPO: Cómo el usuario llega a comprar un producto    │
└─────────────────────────────────────────────────────────────────┘

1️⃣  LLEGADA A LA APP
    └─→ Usuario no logueado ve Hero Section
    └─→ Links: Home, Registrarme, Ingresar

2️⃣  REGISTRO / LOGIN
    └─→ Completa formulario o ingresa credenciales
    └─→ Backend valida y retorna token/sesión
    └─→ Frontend guarda datos de usuario

3️⃣  DASHBOARD DE USUARIO
    └─→ Dos opciones:
        ├─ "Generar con IA" → PromptGenerator.vue
        └─ "Subir imagen" → ImageUploader.vue

4️⃣  GENERACIÓN / CARGA DE IMAGEN
    
    [SI ELIGE IA]
    ├─→ Escribe prompt descriptivo
    ├─→ Hace POST a /api/generate-image
    ├─→ Backend llama a Stability AI
    ├─→ Retorna URL de imagen generada
    └─→ Frontend muestra preview
    
    [SI ELIGE SUBIR]
    ├─→ Selecciona archivo local
    ├─→ Upload a backend
    ├─→ Opcionalmente: remover fondo con rembg
    └─→ Frontend muestra preview

5️⃣  SELECCIÓN DE PRODUCTO
    ├─→ ProductSelector.vue muestra opciones:
    │   ├─ Tipo de producto (remera, taza, gorro, etc.)
    │   ├─ Color disponible
    │   ├─ Talle/Variante
    │   └─ Cantidad
    └─→ Usuario elige

6️⃣  PREVIEW FINAL
    ├─→ PreviewPanel.vue simula el producto final
    ├─→ Posicionar imagen en el producto
    ├─→ Ajustar zoom, posición X/Y
    └─→ Botón "Confirmar Pedido"

7️⃣  CREACIÓN DE PEDIDO
    ├─→ Frontend hace POST a /api/create-order
    ├─→ Backend guarda en BD:
    │   ├─ Tabla Pedidos (id_usuario)
    │   └─ Tabla Pedidos_detalle (producto, imagen, cantidad)
    └─→ Retorna order_id

8️⃣  INICIACIÓN DE PAGO
    ├─→ Frontend hace POST a /api/create-payment
    ├─→ Backend crea pago en Mercado Pago API
    ├─→ Mercado Pago retorna init_point (URL de checkout)
    └─→ Frontend redirige usuario a checkout de MP

9️⃣  PROCESAMIENTO DE PAGO (Mercado Pago)
    ├─→ Usuario completa formulario de tarjeta
    ├─→ Mercado Pago valida y procesa
    └─→ Ejemplo: https://mercadopago.com/checkout/v1/xxx

🔟  CONFIRMACIÓN
    ├─→ Usuario es redirigido a /success?payment=xxx
    ├─→ Backend recibe IPN (webhook) de Mercado Pago
    ├─→ Actualiza estado de pedido a "pagado"
    └─→ Frontend muestra página de éxito

1️⃣1️⃣ SEGUIMIENTO
    ├─→ Usuario accede a "Mis Diseños"
    ├─→ Ve historial de pedidos
    ├─→ Estados: Pendiente, Completado, Cancelado
    └─→ Puede ver detalles y descargar resultados
```

### Diagrama de Comunicación

```
NAVEGADOR                  BACKEND FASTAPI           SQL SERVER         APIs EXTERNAS
   │                            │                         │                  │
   │ 1. POST /api/register      │                         │                  │
   ├───────────────────────────→│                         │                  │
   │                            │ 2. Hash contraseña      │                  │
   │                            │ 3. INSERT Usuario       │                  │
   │                            ├────────────────────────→│                  │
   │                            │                         │                  │
   │ 4. POST /api/generate-image│                         │                  │
   ├───────────────────────────→│ 5. cURL request         │                  │
   │                            ├─────────────────────────────────────────→ Stability AI
   │                            │                         │ 6. {imagen_url}  │
   │                            │                         │ ←─────────────────
   │                            │                         │                  │
   │ 7. POST /api/create-order  │                         │                  │
   ├───────────────────────────→│ 8. INSERT Pedido        │                  │
   │                            ├────────────────────────→│                  │
   │                            │    INSERT Pedidos_det   │                  │
   │                            ├────────────────────────→│                  │
   │                            │ {order_id}              │                  │
   │ 9. ← {order_id}            │                         │                  │
   │                            │                         │                  │
   │ 10. POST /api/create-payment│                        │                  │
   ├───────────────────────────→│ 11. POST /v1/preferences│                  │
   │                            ├──────────────────────────────────────────→ Mercado Pago
   │                            │ 12. {init_point}        │                  │
   │                            │ ←──────────────────────────────────────────
   │ 13. ← {payment_url}        │                         │                  │
   │                            │                         │                  │
   │ 14. REDIRECT User to MP    │                         │                  │
   │ ═══════════════════════════════════════════════════════════════════════→ Mercado Pago
   │                            │                         │                  │
   │ 15. User completes payment │                         │                  │
   │← ← ← ← ← ← ← ← ← ← ← ← ←  (payment processed)      │                  │
   │                            │                         │                  │
   │                            │ 16. IPN Webhook (async) │                  │
   │                            │←───────────────────────────────────────────
   │                            │ 17. UPDATE Pedido status│                  │
   │                            ├────────────────────────→│                  │
   │                            │                         │                  │
   │ 18. GET /success           │                         │                  │
   ├───────────────────────────→│ 19. SELECT Pedido       │                  │
   │                            ├────────────────────────→│                  │
   │ 20. ← Success Page         │                         │                  │
   │←───────────────────────────┤                         │                  │
```

---

## Componentes Principales

### Frontend

#### 1. **App.vue** (Orquestador Principal)
```vue
Responsabilidades:
├─ Navbar con navegación (Home, Registrarme, Ingresar, Crear, Mis Diseños, Logout)
├─ Gestión de estado de usuario (logueado/no logueado, tipo rol)
├─ Renderización condicional de vistas según estado
└─ Manejo de sesión y tokens

Estados principales:
├─ showRegistrationForm: muestra CreateUser.vue
├─ showLoginForm: muestra Login.vue
├─ userLogged: boolean de sesión activa
├─ userType: "cliente" o "admin"
├─ imageSourceMode: "upload" o "generate" o null
├─ generatedImage: URL de imagen actual
└─ currentStep: paso en el flujo (1-5)
```

#### 2. **CreateUser.vue** (Registro)
```vue
Campos:
├─ fullname: Nombre completo
├─ email: Correo (validación única)
├─ phone: Teléfono (opcional)
└─ password: Contraseña (hasheada en backend)

Eventos:
├─ @user-created: usuario registrado exitosamente
└─ @go-to-login: redirigir a login

Validación:
├─ Email único en BD
├─ Contraseña mínimo 6 caracteres
└─ Campos requeridos
```

#### 3. **Login.vue** (Autenticación)
```vue
Campos:
├─ email: Correo registrado
└─ password: Contraseña

Eventos:
├─ @login-success: usuario autenticado
├─ @go-to-register: ir a registro
└─ @forgot-password: recuperar contraseña (TODO)

Características:
├─ Validación de credenciales en backend
├─ Almacenamiento de token/sesión
└─ Manejo de errores (usuario no existe, contraseña incorrecta)
```

#### 4. **PromptGenerator.vue** (Generación con IA)
```vue
Campos:
└─ prompt: descripción en texto libre

Flujo:
├─ Usuario escribe descripción
├─ Hace clic en "Generar"
├─ useApi.post('/api/generate-image', { prompt })
├─ Backend llama a Stability AI
├─ Retorna imagen URL
└─ PreviewPanel.vue muestra resultado

Ejemplo Prompt:
"Un gatito naranja jugando con un ovillo de lana en un jardín soleado"
```

#### 5. **ImageUploader.vue** (Carga Manual)
```vue
Funcionalidades:
├─ Drag & drop file upload
├─ Input file tradicional
├─ Validación de formato (JPG, PNG, WebP)
├─ Preview en tiempo real
└─ Botón "Remover fondo" (opcional, usa rembg backend)

Retorna:
└─ URL de imagen procesada
```

#### 6. **ProductSelector.vue** (Selección de Producto)
```vue
Datos:
├─ Productos: [
│   { id: 1, nombre: "Remera", precios: {...}, talles: [...] },
│   { id: 2, nombre: "Taza", colores: [...], precios: {...} },
│   { id: 3, nombre: "Gorro", colores: [...] },
│   { id: 4, nombre: "Bolsa", colores: [...] }
│ ]

Campos de selección:
├─ Tipo de producto (dropdown)
├─ Color (si aplica)
├─ Talle (si aplica)
├─ Cantidad (spinner)
└─ Mostrar precio total

Evento:
└─ @product-selected: { productoId, color, talle, cantidad, precio }
```

#### 7. **PreviewPanel.vue** (Visualización Final)
```vue
Funcionalidades:
├─ Mostrar producto con imagen
├─ Controles de posición:
│   ├─ Posición X (píxeles)
│   ├─ Posición Y (píxeles)
│   └─ Zoom (escala %)
├─ Preview en tiempo real mientras ajusta
└─ Botón "Confirmar Pedido"

Datos guardados:
├─ imagen_url
├─ posicion_x
├─ posicion_y
├─ zoom
└─ producto_id
```

#### 8. **CheckoutPanel.vue** (Carrito y Pago)
```vue
Flujo:
├─ Resumen del pedido:
│   ├─ Producto seleccionado
│   ├─ Cantidad
│   ├─ Precio unitario
│   └─ Total
├─ Botón "Pagar con Mercado Pago"
├─ POST /api/create-payment
├─ Recibe payment_url
└─ Redirige a Mercado Pago

Ejemplo:
Remera Blanca x1
Precio: $800
Total: $800
[Botón] Pagar con Mercado Pago
```

#### 9. **useApi.js** (Composable Reutilizable)
```javascript
Función: post(url, data)
├─ Realiza fetch POST al backend
├─ Maneja errores y estados
├─ Retorna resultado JSON

Ejemplo de uso en componentes:
import { useApi } from '@/composables/useApi'

const { post, loading, error } = useApi()
const data = await post('/api/generate-image', { prompt })
```

### Backend FastAPI

#### Modelos Pydantic
```python
RegisterIn:
├─ fullname: str
├─ email: str
├─ phone: str | None
└─ password: str

LoginIn:
├─ email: str
└─ password: str

CreateOrderIn:
├─ producto: str
├─ talle: str | None
├─ color: str
├─ cantidad: int
├─ prompt: str
├─ imagen_url: str
├─ posicion_x: int
├─ posicion_y: int
└─ zoom: float

PaymentIn:
├─ producto: str
├─ precio: float
└─ cantidad: int
```

#### Funciones de Utilidad
```python
hash_password(pw: str) -> str
├─ PBKDF2-HMAC-SHA256
├─ 100,000 iteraciones
└─ Salado 32 bytes

verify_password(plain: str, hashed: str) -> bool
├─ Valida contraseña contra hash
└─ Retorna bool

json_success(data) -> dict
└─ Formato: { "success": True, "data": ... }
```

### Agentes de IA (OLLAMA)

El sistema implementa tres agentes de Inteligencia Artificial que operan de forma asincrónica:

| Agente | Puerto | Función Principal | README |
|--------|--------|-------------------|--------|
| **Productos** | 5001 | Catálogo dinámico desde BD | [📖 Ver documentación](agentes-Ollama/agente-productos/README.md) |
| **Precios** | 5002 | Actualización de precios vía IA | [📖 Ver documentación](agentes-Ollama/agente-precios/README.md) |
| **Cupones** | 5003 | Gestión inteligente de descuentos | [📖 Ver documentación](agentes-Ollama/agente-cupones/README.md) |

**Características comunes:**
- 🤖 Procesamiento con OLLAMA (modelo qwen2.5:1.5b)
- 🔄 Fallback automático si OLLAMA falla
- ⚡ APIs REST para integración con frontend
- 🔗 Integración con backend FastAPI y SQL Server

**Nota:** Cada agente incluye documentación técnica completa en su README con endpoints, ejemplos, troubleshooting e integración con el sistema.

---

## APIs y Endpoints

### Backend FastAPI

#### Autenticación

**POST /api/register**
```json
Entrada:
{
  "fullname": "Juan Pérez",
  "email": "juan@example.com",
  "phone": "1234567890",
  "password": "securepass123"
}

Salida (201):
{
  "success": true,
  "data": {
    "id_usuario": 1,
    "email": "juan@example.com",
    "nombre": "Juan Pérez"
  }
}

Errores:
├─ 409: Email ya registrado
├─ 422: Validación fallida
└─ 500: Error del servidor
```

**POST /api/login**
```json
Entrada:
{
  "email": "juan@example.com",
  "password": "securepass123"
}

Salida (200):
{
  "success": true,
  "data": {
    "token": "jwt_token_aqui",
    "usuario_id": 1,
    "nombre": "Juan Pérez",
    "tipo": "cliente"
  }
}

Errores:
├─ 401: Credenciales inválidas
└─ 404: Usuario no existe
```

#### Imágenes

**POST /api/generate-image**
```json
Entrada:
{
  "prompt": "Un gatito naranja jugando con un ovillo"
}

Salida (200):
{
  "success": true,
  "data": {
    "imagen_url": "https://bucket.s3.com/img_123.png",
    "timestamp": "2024-04-21T15:30:00Z"
  }
}

Notas:
├─ Usa Stability AI API
├─ Timeout: 60 segundos
└─ Almacena imagen en uploads/
```

**POST /api/remove-background**
```json
Entrada: FormData
├─ file: imagen_file

Salida (200):
{
  "success": true,
  "data": {
    "image_url": "https://bucket.s3.com/img_nobg_123.png"
  }
}

Notas:
└─ Usa librería rembg (IA para removedor de fondo)
```

#### Pedidos

**POST /api/create-order**
```json
Entrada:
{
  "producto": "remera",
  "talle": "L",
  "color": "blanco",
  "cantidad": 1,
  "prompt": "Descripción de la IA",
  "imagen_url": "https://...",
  "posicion_x": 50,
  "posicion_y": 75,
  "zoom": 1.2
}

Salida (201):
{
  "success": true,
  "data": {
    "id_pedido": 42,
    "usuario_id": 1,
    "total": 800.00,
    "estado": "pendiente"
  }
}

Validación:
├─ Usuario autenticado (token requerido)
├─ Producto válido en BD
└─ Imagen URL accesible
```

#### Pagos

**POST /api/create-payment**
```json
Entrada:
{
  "producto": "remera",
  "precio": 800.00,
  "cantidad": 1
}

Salida (200):
{
  "success": true,
  "data": {
    "payment_url": "https://mercadopago.com/checkout/v1/xxxxx",
    "preference_id": "12345678-1234-1234-1234-123456789012"
  }
}

Notas:
├─ Integración con Mercado Pago SDK
├─ Crea preferencia de pago
└─ URL válida por 24 horas
```

**POST /api/save-payment**
```json
Entrada:
{
  "order_id": 42,
  "payment_id": "payment_123456",
  "status": "approved"
}

Salida (200):
{
  "success": true,
  "data": {
    "pedido_id": 42,
    "nuevo_estado": "pagado"
  }
}

Notas:
└─ Webhook de Mercado Pago
```

#### Sistema de Cupones - Experiencia de Usuario

##### 📍 ¿Cuándo y dónde se muestran los cupones?

Los cupones se muestran en el **Paso 3: Vista Previa del Pedido** (PreviewPanel), justo DESPUÉS del resumen de precios y ANTES del botón "Confirmar Pedido".

**Ubicación en el flujo:**

```
1️⃣ Seleccionar Producto
    ↓
2️⃣ Crear Diseño (IA)
    ↓
3️⃣ Vista Previa
    ├─ Mockup del producto
    ├─ Detalles (talle, color, cantidad)
    ├─ Resumen de precios
    │
    ├─ 🎟️ **CUPONES DISPONIBLES** ← Aquí aparecen
    │   ├─ Badge: "🎟️ Tienes X cupón(es) disponible(s)"
    │   ├─ O mensaje: "😔 No tienes cupones disponibles"
    │   └─ Click → Modal con lista de cupones
    │
    └─ Botón "Confirmar Pedido"
```

##### 🎯 Casos de uso

**Caso 1: Cliente CON cupones disponibles**

1. Usuario llega a Vista Previa y ve el resumen con precio del producto
2. Sistema carga cupones automáticamente consultando `/api/cupones/disponibles/{id_usuario}`
3. Aparece badge morado: `🎟️ Tienes 2 cupón(es) disponible(s) | Hasta 20% OFF`
4. Usuario hace clic en el badge y se abre modal con lista de cupones
5. Modal muestra cada cupón con:
   - Código (ej: BIENVENIDA10)
   - Porcentaje de descuento (10% OFF)
   - Descripción y razón personalizada
   - Fecha de expiración
   - Usos restantes
6. Usuario selecciona cupón haciendo clic en "Aplicar"
7. Se muestra badge verde con código del cupón y botón "✕" para removerlo
8. Resumen de precios actualizado:
   ```
   Remera                      $2,500
   🎟️ Descuento (BIENVENIDA10) -10%   -$250
   Total                       $2,250
   ```
9. Usuario confirma pedido con descuento aplicado

**Caso 2: Cliente SIN cupones disponibles**

1. Usuario llega a Vista Previa
2. Sistema consulta cupones pero no encuentra ninguno aplicable
3. NO aparece el badge de cupones (sección oculta)
4. Usuario ve el resumen de precios normal sin descuentos
5. Usuario confirma pedido con precio completo

##### 🔍 Tipos de cupones según perfil

| Perfil del Cliente | Cupones que ve | Ejemplo |
|-------------------|----------------|---------|
| **Nuevo** (0 compras) | BIENVENIDA, PRIMERA | 🎟️ BIENVENIDA10 (10% OFF) |
| **Regular** (1-4 compras) | Cupones generales | 🎟️ VERANO20 (20% OFF) |
| **VIP** (5+ compras) | FIDELIDAD, VIP | 🎟️ FIDELIDAD15 (15% OFF) |
| **Inactivo** (>30 días) | REGRESO, VUELVE | 🎟️ REGRESO25 (25% OFF) |
| **Alto valor** (>$10,000) | ESPECIAL, ELITE | 🎟️ ELITE25 (25% OFF) |

##### ⚙️ Validaciones del backend

Cuando el usuario confirma el pedido con un cupón, el backend valida:

1. ✅ **Cupón existe y está activo** - Error: "Cupón 'XXX' no válido o inactivo"
2. ✅ **Cupón no expiró** - Error: "Cupón 'XXX' expirado"
3. ✅ **Cupón tiene usos disponibles** - Error: "Cupón 'XXX' alcanzó el límite de usos"

Si todas las validaciones pasan:
- Aplica descuento al total
- Incrementa contador de usos
- Crea el pedido con precio con descuento

##### 📊 Ejemplo completo - Cliente nuevo

**Escenario:** María (nueva cliente) compra su primera remera

1. **Estado inicial:**
   - Cliente: María (0 compras)
   - Producto: Remera Blanca (Talle M)
   - Precio: $2,500

2. **Sistema carga cupones:**
   - Backend analiza: 0 compras → Cliente nuevo
   - Cupones aplicables: BIENVENIDA10, PRIMERA20

3. **Aparece badge:** `🎟️ Tienes 2 cupón(es) disponible(s) | Hasta 20% OFF`

4. **María ve modal con opciones:**
   ```
   BIENVENIDA10 - 10% OFF
   "¡Es tu primera compra con nosotros!"
   
   PRIMERA20 - 20% OFF
   "Bienvenida a Prendete Rock"
   ```

5. **María selecciona PRIMERA20 y se muestra:**
   ```
   Badge verde: PRIMERA20  -20%  [✕]
   
   Resumen:
   Remera                      $2,500
   🎟️ Descuento (PRIMERA20) -20%   -$500
   Total                       $2,000
   ```

6. **María confirma y backend procesa:**
   - Valida cupón PRIMERA20 ✅
   - Aplica 20% descuento ✅
   - Total final: $2,000 ✅
   - Incrementa usos del cupón ✅

##### 🚀 Resumen ejecutivo

- **¿Dónde?** Vista Previa del Pedido (PreviewPanel.vue)
- **¿Cuándo?** Antes de confirmar pedido, después del resumen de precios
- **¿Cómo funciona?**
  1. Badge morado si hay cupones disponibles
  2. Sin badge si no hay cupones
  3. Click abre modal con lista
  4. Seleccionar cupón lo aplica automáticamente
  5. Descuento visible en resumen de precios
  6. Backend valida al confirmar pedido

- **¿Por qué así?**
  - Momento justo: cuando el usuario ya decidió comprar
  - No invasivo: solo aparece si hay cupones
  - Transparente: muestra descuento en tiempo real
  - Fácil de usar: un clic para ver, otro para aplicar

##### 📝 Archivos del sistema de cupones

- `frontend/src/components/PreviewPanel.vue` - Integración de cupones
- `frontend/src/components/CuponesDisponibles.vue` - Componente reutilizable
- `backend/api_python/app_v2.py` - Validación y aplicación de cupones (líneas ~670-820)

---

#### Cupones - Endpoints Técnicos

**GET /api/cupones/disponibles/{id_cliente}**

**Descripción:** Endpoint inteligente que analiza el perfil del cliente y retorna cupones personalizados según su historial de compras y comportamiento.

**Características principales:**
- ⚡ Respuesta rápida (solo SQL, sin procesamiento IA)
- 🎯 Perfilado automático del cliente
- 📊 Reglas de negocio integradas
- 🔄 No requiere servicios adicionales

**Reglas de negocio:**

| Tipo | Condición | Código Ejemplo |
|------|-----------|----------------|
| BIENVENIDA | Sin compras (0 pedidos) | `BIENVENIDA10` |
| FIDELIDAD | 5+ compras | `FIDELIDAD15`, `VIP20` |
| REGRESO | Inactivo >30 días | `REGRESO25` |
| ESPECIAL | Gasto >$10,000 | `ESPECIAL30` |
| GENERAL | Todos | `VERANO20` |

```json
Entrada:
GET /api/cupones/disponibles/1

Salida (200):
{
  "success": true,
  "data": {
    "cupones": [
      {
        "id_cupon": 1,
        "codigo": "BIENVENIDA10",
        "descuento": 10,
        "descripcion": "Descuento de bienvenida para nuevos clientes",
        "expiracion": "2026-05-31",
        "es_limitado": true,
        "usos_restantes": 50,
        "categoria": "primera_compra",
        "razon": "¡Es tu primera compra con nosotros!"
      },
      {
        "id_cupon": 5,
        "codigo": "VERANO20",
        "descuento": 20,
        "descripcion": "Promoción de verano",
        "expiracion": "2026-06-30",
        "es_limitado": false,
        "usos_restantes": null,
        "categoria": "general",
        "razon": null
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
    "total": 2,
    "mensaje": "¡Tienes 2 cupón(es) disponible(s)!"
  }
}

Errores:
├─ 404: Cliente no encontrado
└─ 500: Error del servidor
```

**Ventajas:**
1. **Performance:** Consultas SQL optimizadas (< 50ms)
2. **Escalabilidad:** No depende de agentes IA adicionales
3. **Personalización:** Cada cliente ve cupones relevantes
4. **Automatización:** Reglas aplicadas automáticamente
5. **Conversión:** Incentiva compra, fidelidad y reactivación

**Integración Frontend:**
- Badge en carrito/checkout mostrando cupones disponibles
- Modal para seleccionar y aplicar cupones
- Cálculo automático de descuento en el resumen del pedido

---

#### Panel de Administrador - Gestión de Cupones

El panel de administrador incluye una sección completa para gestionar cupones de descuento.

**Endpoints de Admin:**

**POST /api/admin/cupones**
```json
Entrada:
{
  "codigo": "BLACKFRIDAY50",
  "descuento": 50.0,
  "descripcion": "Descuento Black Friday",
  "fecha_expiracion": "2026-11-30",
  "es_limitado": true,
  "usos_maximos": 100,
  "categoria": "especial"
}

Salida (201):
{
  "success": true,
  "data": {
    "id_cupon": 15,
    "codigo": "BLACKFRIDAY50",
    "descuento": 50.0,
    "mensaje": "Cupón creado exitosamente"
  }
}
```

**GET /api/admin/cupones**
```
Query params:
├─ activo: true/false
├─ categoria: primera_compra, fidelidad, general, especial
└─ limit: 50 (default)

Salida (200):
{
  "success": true,
  "cupones": [
    {
      "id_cupon": 1,
      "codigo": "VIP25",
      "descuento": 25,
      "fecha_creacion": "2026-01-15",
      "fecha_expiracion": "2026-12-31",
      "usos_totales": 45,
      "usos_restantes": 55,
      "activo": true,
      "categoria": "fidelidad"
    }
  ],
  "total": 12
}
```

**PUT /api/admin/cupones/{id_cupon}**
```json
Entrada:
{
  "activo": false,
  "usos_maximos": 200,
  "fecha_expiracion": "2027-01-31"
}

Salida (200):
{
  "success": true,
  "mensaje": "Cupón actualizado correctamente"
}
```

**GET /api/admin/cupones/estadisticas**
```json
Salida (200):
{
  "success": true,
  "data": {
    "total_cupones": 12,
    "activos": 8,
    "inactivos": 4,
    "mas_usados": [
      {"codigo": "BIENVENIDA10", "usos": 234},
      {"codigo": "VERANO20", "usos": 189}
    ],
    "descuento_promedio": 14.5,
    "ahorro_total_clientes": 2450000
  }
}
```

**Componente Frontend:** `GestionCupones.vue`

Características:
- 📊 Dashboard con métricas clave
- 🎫 Tabla CRUD de cupones
- ➕ Modal para crear cupón
- ✏️ Modal para editar cupón
- 📈 Gráficos de uso
- 🔍 Búsqueda y filtros
- 📥 Exportar a CSV/Excel

**Integración con Agente:** El agente de cupones (puerto 5003) se integra para funcionalidades avanzadas. Ver [documentación del agente](agentes-Ollama/agente-cupones/README.md).


#### Admin

**GET /api/users**
```
Salida (200):
[
  {
    "id_usuario": 1,
    "nombre": "Juan Pérez",
    "email": "juan@example.com",
    "tipo": "cliente",
    "fecha_registro": "2024-04-21"
  },
  ...
]

Requisito:
└─ Usuario tipo "admin"
```

**GET /api/orders**
```
Salida (200):
[
  {
    "id_pedido": 42,
    "usuario_id": 1,
    "fecha": "2024-04-21",
    "total": 800.00,
    "estado": "completado"
  },
  ...
]
```

**GET /api/health**
```
Salida (200):
{
  "success": true
}

Uso:
└─ Health check / ping
```

---

## Base de Datos

### Esquema SQL Server

#### Tabla: **Usuarios**
```sql
CREATE TABLE Usuarios (
    id_usuario INT IDENTITY(1,1) PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    password_user VARCHAR(255) NOT NULL,  -- PBKDF2 salted hash
    Tipo VARCHAR(50)                       -- 'cliente' o 'admin'
);
```

**Campos:**
| Campo | Tipo | Requisitos | Notas |
|-------|------|-----------|-------|
| `id_usuario` | INT | PK, AUTO | Auto-incrementado |
| `Nombre` | VARCHAR(100) | NOT NULL | e.g., "Juan Pérez" |
| `Email` | VARCHAR(100) | UNIQUE, NOT NULL | Validado en registro |
| `telefono` | VARCHAR(20) | NULL | Opcional |
| `password_user` | VARCHAR(255) | NOT NULL | Hash PBKDF2 (100k iteraciones) |
| `Tipo` | VARCHAR(50) | NULL | "cliente" o "admin" |

---

#### Tabla: **Productos**
```sql
CREATE TABLE Productos (
    id_producto INT IDENTITY(1,1) PRIMARY KEY,
    Detalle VARCHAR(255),          -- Descripción
    Color VARCHAR(50),
    talle VARCHAR(20)              -- XS, S, M, L, XL, XXL
);
```

**Campos:**
| Campo | Tipo | Notas |
|-------|------|-------|
| `id_producto` | INT | PK, AUTO |
| `Detalle` | VARCHAR(255) | e.g., "Remera de algodón 100%" |
| `Color` | VARCHAR(50) | e.g., "Blanco", "Negro" |
| `talle` | VARCHAR(20) | e.g., "M", "L" |

---

#### Tabla: **Pedidos**
```sql
CREATE TABLE Pedidos (
    id_pedido INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario INT NOT NULL,
    CONSTRAINT FK_Pedidos_Usuarios 
    FOREIGN KEY (id_usuario) 
    REFERENCES Usuarios(id_usuario)
);
```

**Campos:**
| Campo | Tipo | Notas |
|-------|------|-------|
| `id_pedido` | INT | PK, AUTO |
| `id_usuario` | INT | FK hacia Usuarios |

---

#### Tabla: **Pedidos_detalle**
```sql
CREATE TABLE Pedidos_detalle (
    id_detalle INT IDENTITY(1,1) PRIMARY KEY,
    id_pedido INT NOT NULL,
    id_producto INT NOT NULL,
    detalle VARCHAR(255),         -- Nota: talle, color, cantidad
    imagen VARCHAR(255),          -- URL de imagen (Stability AI o upload)
    fecha DATETIME DEFAULT GETDATE(),
    estado VARCHAR(50),           -- 'pendiente', 'pagado', 'completado', 'cancelado'
    pago VARCHAR(50),             -- 'pendiente', 'aprobado'
    total DECIMAL(10,2),          -- Precio total del detalle
    
    CONSTRAINT FK_Detalle_Pedidos 
    FOREIGN KEY (id_pedido) 
    REFERENCES Pedidos(id_pedido),
    
    CONSTRAINT FK_Detalle_Productos 
    FOREIGN KEY (id_producto) 
    REFERENCES Productos(id_producto)
);
```

**Campos:**
| Campo | Tipo | Notas |
|-------|------|-------|
| `id_detalle` | INT | PK, AUTO |
| `id_pedido` | INT | FK hacia Pedidos |
| `id_producto` | INT | FK hacia Productos |
| `detalle` | VARCHAR(255) | Metadata del pedido |
| `imagen` | VARCHAR(255) | URL a imagen final |
| `fecha` | DATETIME | Auto-timestamp |
| `estado` | VARCHAR(50) | Ciclo de vida del pedido |
| `pago` | VARCHAR(50) | Estado del pago |
| `total` | DECIMAL(10,2) | Monto pagado |

---

### Relaciones

```
Usuarios (1) ──────────────── (N) Pedidos
                ↓
            id_usuario (FK)


Pedidos (1) ──────────────── (N) Pedidos_detalle
                ↓
            id_pedido (FK)


Productos (1) ──────────────── (N) Pedidos_detalle
                ↓
            id_producto (FK)
```

---

### Ciclo de Vida de un Pedido

```
Pedidos_detalle.estado:

PENDIENTE (entrada)
    ↓ [Usuario confirma diseño]
CREADO
    ↓ [Usuario inicia pago]
EN_PAGO
    ↓ [Mercado Pago procesa]
PAGADO
    ↓ [Producción inicia]
COMPLETADO o CANCELADO

Pedidos_detalle.pago:

PENDIENTE (entrada)
    ↓ [Usuario hace POST /create-payment]
EN_PROCESO
    ↓ [Webhook de Mercado Pago]
APROBADO/RECHAZADO
```

---

## Configuración e Instalación

### Requisitos del Sistema

**Hardware:**
- CPU: Dual-core mínimo (4 core recomendado para IA)
- RAM: 4 GB mínimo (8 GB recomendado)
- Disco: 10 GB (para modelos de IA)

**Softs (Windows):**
```
✓ Python 3.9+ (en PATH)
✓ Node.js 18+ (en PATH)
✓ PHP 8.0+ (opcional, legacy)
✓ SQL Server 2019+ (instalado y ejecutándose)
✓ OLLAMA (para agente IA de productos dinámicos)
✓ Git
✓ Visual Studio Code (recomendado)
```

---

## 🚀 Requisitos Completos para Ejecutar la Aplicación

### Lista de Verificación Pre-Ejecución

#### 1. Software Base Instalado

✅ **Python 3.9+**
```powershell
python --version
# Debe mostrar: Python 3.9.x o superior
```

✅ **Node.js 18+**
```powershell
node --version
npm --version
# node: v18.x.x o superior
# npm: v9.x.x o superior
```

✅ **SQL Server 2019+**
```powershell
# Verificar servicio corriendo
Get-Service MSSQL*
# Estado: Running
```

✅ **OLLAMA (para Agente IA)**
```powershell
ollama --version
# ollama version 0.5.x o superior

# Verificar que está corriendo
curl http://localhost:11434
# Respuesta: Ollama is running
```

---

#### 2. Base de Datos Configurada

✅ **Crear Base de Datos PrendeteRock**
```sql
-- Ejecutar en SQL Server Management Studio:
-- Archivo: database/estructura-BDD-Prendete-Rock.sql

-- Verifica que existan las tablas:
USE PrendeteRock;
SELECT * FROM INFORMATION_SCHEMA.TABLES;
-- Debe mostrar: Usuarios, Productos, Pedidos, Pedidos_detalle
```

✅ **Poblar Productos (85 productos)**
```sql
-- Los productos deben estar cargados en la tabla Productos
SELECT COUNT(*) FROM Productos;
-- Debe retornar: 85 (o la cantidad actual)
```

✅ **Usuarios de Prueba**
```sql
-- Crear usuarios de prueba con contraseñas hasheadas
-- Ver: database/insertar-usuarios-prueba-FINAL.sql
```

---

#### 3. Modelo de IA Descargado

✅ **Descargar modelo qwen2.5:1.5b**
```powershell
ollama pull qwen2.5:1.5b
# Descarga ~986 MB

# Verificar modelo instalado
ollama list
# Debe aparecer: qwen2.5:1.5b
```

---

#### 4. Dependencias del Proyecto Instaladas

✅ **Dependencias Python (FastAPI Backend)**
```powershell
cd database\source
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Verifica instalación
pip list | Select-String "fastapi|uvicorn|pyodbc"
```

✅ **Dependencias Python (Agente IA)**
```powershell
cd ..\..\agentes-Ollama
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install flask flask-cors requests pyodbc

# Verifica instalación
pip list | Select-String "flask|pyodbc"
```

✅ **Dependencias Node.js (Frontend)**
```powershell
cd ..\frontend
npm install

# Verifica node_modules
Test-Path node_modules\vue
# Debe retornar: True
```

---

#### 5. Configuración de Credenciales

✅ **Variables de Entorno (Opcional)**
```powershell
# Crear .env en database/source/ si usas claves API externas:
STABILITY_API_KEY=sk-xxxxx        # Para generación de imágenes
MERCADOPAGO_ACCESS_TOKEN=APP_xxx  # Para pagos
```

✅ **Configuración de BD en app.py**
```python
# database/source/app.py
# Verifica la cadena de conexión:
connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=.\\SQLEXPRESS01;"  # Tu servidor
    "DATABASE=PrendeteRock;"
    "Trusted_Connection=yes;"
)
```

✅ **Configuración de BD en agente_productos.py**
```python
# agentes-Ollama/agente_productos.py
# Verifica la cadena de conexión:
connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=.\\SQLEXPRESS01;"  # Mismo servidor
    "DATABASE=PrendeteRock;"
    "Trusted_Connection=yes;"
)
```

---

### Ejecución Completa del Sistema

#### Opción 1: Usar RUN.bat (⭐ RECOMENDADO)

```powershell
# Desde la raíz del proyecto
cd c:\projects\ai-print-studio
.\RUN.bat
```

**Verificaciones automáticas que hace RUN.bat:**
1. ✅ Python y Node.js instalados
2. ✅ Entornos virtuales creados
3. ✅ Dependencias instaladas
4. ✅ OLLAMA corriendo (puerto 11434)
5. ✅ Modelo qwen2.5:1.5b descargado
6. ✅ SQL Server accesible
7. ✅ Inicia todos los servidores

**Servidores iniciados:**
- 🟢 FastAPI Backend → http://127.0.0.1:8000
- 🟢 OLLAMA → http://localhost:11434
- 🟢 Agente IA → http://localhost:5001/productos-ia
- 🟢 Vue.js Frontend → http://localhost:5173
- 🟢 PHP Backend → http://localhost:8080 (si disponible)

**Navegador se abre automáticamente en:** http://localhost:5173

---

#### Opción 2: Ejecución Manual Paso a Paso

**Terminal 1: OLLAMA**
```powershell
# Si no está corriendo:
ollama serve
# Esperar mensaje: "Ollama is running"
```

**Terminal 2: Agente IA**
```powershell
cd agentes-Ollama
.\.venv\Scripts\Activate.ps1
python agente_productos.py

# Esperar mensaje:
# ⚠ MODO PRODUCCIÓN: Procesando TODOS los productos
# * Running on http://127.0.0.1:5001
```

**Terminal 3: FastAPI Backend**
```powershell
cd database\source
.\.venv\Scripts\Activate.ps1
python app.py

# Esperar mensaje:
# INFO: Uvicorn running on http://127.0.0.1:8000
```

**Terminal 4: Vue Frontend**
```powershell
cd frontend
npm run dev

# Esperar mensaje:
# VITE ready in XXX ms
# Local: http://localhost:5173
```

---

### Verificación Post-Inicio

#### Test 1: Backend FastAPI
```powershell
curl http://127.0.0.1:8000/api/health
# Respuesta esperada: {"success":true}
```

#### Test 2: Agente IA
```powershell
curl http://localhost:5001/productos-ia
# Respuesta esperada: JSON con array de productos
```

#### Test 3: Frontend
```powershell
# Abrir navegador en:
# http://localhost:5173
# Debe cargar la interfaz de AI Print Studio
```

#### Test 4: Circuito Completo (Automatizado)
```powershell
# Ejecutar script de testing
.\test-circuito.ps1

# Verifica:
# ✅ SQL Server conectado
# ✅ OLLAMA respondiendo
# ✅ Modelo qwen2.5:1.5b presente
# ✅ Agente IA retorna productos
# ✅ FastAPI respondiendo
```

---

### Flujo de Datos Completo

```
INICIO DE SESIÓN DEL USUARIO
        ↓
┌───────────────────────────────────────────────────────────┐
│  1. USUARIO ACCEDE AL FRONTEND                            │
│     http://localhost:5173                                 │
└───────────────────┬───────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────────────────┐
│  2. FRONTEND CARGA PRODUCTOS DINÁMICOS                    │
│     fetch('http://localhost:5001/productos-ia')           │
└───────────────────┬───────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────────────────┐
│  3. AGENTE IA CONSULTA BASE DE DATOS                      │
│     SELECT Detalle, Color, talle FROM Productos           │
│     Retorna: 85 productos                                 │
└───────────────────┬───────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────────────────┐
│  4. AGENTE CONSTRUYE PROMPT Y LLAMA OLLAMA                │
│     POST http://localhost:11434/api/generate              │
│     Model: qwen2.5:1.5b                                   │
│     Timeout: 60 segundos                                  │
└───────────────────┬───────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────────────────┐
│  5. OLLAMA PROCESA Y AGRUPA PRODUCTOS                     │
│     Agrupa por: producto, talles, colores                 │
│     Retorna: JSON estructurado                            │
└───────────────────┬───────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────────────────┐
│  6. AGENTE IA RETORNA AL FRONTEND                         │
│     [                                                      │
│       {                                                    │
│         "producto": "Buzo",                                │
│         "talles": ["S","M","L","XL","XXL"],                │
│         "colores": ["Blanca","Negra","Roja","Azul"]        │
│       }, ...                                               │
│     ]                                                      │
└───────────────────┬───────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────────────────┐
│  7. FRONTEND MUESTRA OPCIONES EN ProductSelector.vue      │
│     Usuario selecciona: producto, talle, color            │
└───────────────────┬───────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────────────────┐
│  8. USUARIO GENERA/SUBE IMAGEN                            │
│     POST /api/generate-image o upload manual              │
└───────────────────┬───────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────────────────┐
│  9. USUARIO CONFIRMA PEDIDO                               │
│     POST http://127.0.0.1:8000/api/create-order           │
│     FastAPI guarda en: Pedidos + Pedidos_detalle          │
└───────────────────┬───────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────────────────┐
│  10. USUARIO INICIA PAGO                                  │
│      POST http://127.0.0.1:8000/api/create-payment        │
│      Mercado Pago retorna URL de checkout                 │
└───────────────────┬───────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────────────────┐
│  11. USUARIO COMPLETA PAGO EN MERCADO PAGO                │
│      Webhook actualiza estado en BD                        │
└───────────────────┬───────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────────────────┐
│  12. FRONTEND MUESTRA PÁGINA DE ÉXITO                     │
│      /success - Pedido completado                          │
└───────────────────────────────────────────────────────────┘
```

---

### Troubleshooting de Ejecución

#### Problema: "OLLAMA no responde"
```powershell
# Verificar proceso
Get-Process ollama -ErrorAction SilentlyContinue

# Si no existe, iniciar:
ollama serve

# Esperar 20-30 segundos para que cargue completamente
```

#### Problema: "Agente IA no encuentra productos"
```sql
-- Verificar que hay productos en BD
USE PrendeteRock;
SELECT COUNT(*) FROM Productos;

-- Si retorna 0, cargar productos de prueba
```

#### Problema: "Frontend no carga productos"
```powershell
# Verificar endpoint del agente
curl http://localhost:5001/productos-ia

# Si falla, revisar logs del agente en su terminal
```

#### Problema: "FastAPI error de conexión a BD"
```python
# Verificar en app.py que la cadena de conexión coincida
# con tu instancia de SQL Server

# Verificar nombre de servidor:
# .\SQLEXPRESS01 (o tu nombre)
```

---

### Instalación Manual

#### 1. Clonar/Descargar Proyecto
```powershell
cd c:\projects
# (Ya existe el proyecto)
cd ai-print-studio
```

#### 2. Instalar Dependencias Frontend
```powershell
cd frontend
npm install
# Instala: vue, vite, @vitejs/plugin-vue
```

#### 3. Instalar Dependencias Backend FastAPI
```powershell
cd ..\database\source
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Instala: fastapi, uvicorn, pyodbc, pydantic, pillow, rembg
```

#### 4. Configurar Base de Datos
```powershell
# Abre SQL Server Management Studio
# Copia y ejecuta: database\estructura-BDD-Prendete-Rock.sql
# Esto crea la BD "PrendeteRock" con las 4 tablas
```

#### 5. Configurar Variables de Entorno
```bash
# backend_fastapi/.env (crear archivo)
DATABASE_URL=mssql+pyodbc://user:password@SERVER_NAME/PrendeteRock?driver=ODBC+Driver+17+for+SQL+Server
STABILITY_API_KEY=sk-xxxxxxxxxxxxx  # De https://platform.stability.ai
MERCADOPAGO_ACCESS_TOKEN=APP_xxxxx   # De https://developers.mercadopago.com

# frontend/.env (crear archivo)
VITE_API_URL=http://localhost:8000
```

---

## Scripts de Ejecución

### Scripts Disponibles

#### **RUN.bat** ⭐ (Script Maestro - RECOMENDADO)
```powershell
# Ejecuta la aplicación completa automáticamente:
# 1. Verifica e instala dependencias Python y Node.js
# 2. Crea entornos virtuales si no existen
# 3. Inicia FastAPI Backend en http://127.0.0.1:8000
# 4. Inicia Vue Frontend en http://localhost:5173
# 5. Inicia PHP Backend en http://localhost:8080 (si está disponible)
# 6. Abre el navegador automáticamente
```

**Características:**
- ✅ Un solo clic para iniciar todo
- ✅ Verifica y crea entornos virtuales
- ✅ Instala dependencias automáticamente
- ✅ Manejo de errores y mensajes claros
- ✅ Compatible con el agente de IA (OLLAMA)

**Uso:**
```powershell
.\RUN.bat
```

**Servidores que inicia:**
- **FastAPI Backend**: http://127.0.0.1:8000 (API principal)
- **OLLAMA**: http://localhost:11434 (Motor de IA)
- **Agente IA**: http://localhost:5001 (Productos dinámicos)
- **Vue.js Frontend**: http://localhost:5173 (Interfaz web)
- **PHP Backend**: http://localhost:8080 (Mercado Pago, si disponible)

**Verificaciones automáticas que realiza:**
1. ✅ Python instalado y venv configurado
2. ✅ Node.js instalado y dependencias
3. ✅ PHP disponible (opcional)
4. ✅ OLLAMA instalado y corriendo
5. ✅ Modelo qwen2.5:1.5b descargado
6. ✅ SQL Server accesible
7. ✅ Puertos libres (8000, 5001, 5173, 8080, 11434)

---

#### **stop.bat** (Detener Todos los Servidores)
```powershell
# Cierra todos los servidores iniciados por RUN.bat:
# - Cierra ventanas por título (FastAPI, Vue, PHP)
# - Termina procesos residuales (node.exe, python.exe, php.exe)
# - Limpia recursos del sistema
```

**Uso:**
```powershell
.\stop.bat
```

---

#### **start-all.bat** (Legacy - Ejecuta todo)
```powershell
# Abre 2 terminales:
# 1. Frontend en http://localhost:5173
# 2. Backend en http://localhost:8000
```

**Uso:**
```powershell
.\start-all.bat
```

---

#### **start-frontend.ps1** (Solo frontend)
```powershell
# Inicia Vite dev server
# http://localhost:5173
# Hot reload: cambios en .vue se cargan automáticamente
```

**Uso:**
```powershell
.\start-frontend.ps1
```

---

#### **start-backend.ps1** (Solo backend FastAPI)
```powershell
# Activa entorno Python
# Inicia Uvicorn en puerto 8000
# Recargar automático en cambios

# Swagger: http://localhost:8000/docs
```

**Uso:**
```powershell
.\start-backend.ps1
```

---

#### **install-dependencies.ps1** (Instala todo)
```powershell
# npm install en frontend
# pip install en backend
# Copia archivos de configuración si es necesario
```

**Uso:**
```powershell
.\install-dependencies.ps1
```

---

#### **diagnostico.ps1** (Verifica requisitos)
```powershell
# Verifica:
# ✓ Python instalado y versión
# ✓ Node.js instalado y versión
# ✓ SQL Server accesible
# ✓ Puertos disponibles (5173, 8000)
# ✓ Variables de entorno necesarias
```

**Uso:**
```powershell
.\diagnostico.ps1
```

---

#### **restart-fastapi.bat** (Reinicia backend)
```powershell
# Detiene proceso de FastAPI
# Reinicia Uvicorn
```

**Uso:**
```powershell
.\restart-fastapi.bat
```

---

## Módulos y Dependencias

### Frontend (npm)

```json
{
  "vue": "^3.4.0",          // Core framework
  "@vitejs/plugin-vue": "^5.0.0",  // Vite plugin
  "vite": "^5.0.0"          // Build tool
}
```

**¿Qué hace cada uno?**
- **vue**: Reactivity, components, lifecycle
- **vite**: Hot reload dev server, optimized builds
- **plugin-vue**: Compila .vue a JavaScript

---

### Backend FastAPI (pip)

```
fastapi==0.104.1                    // Web framework
uvicorn[standard]==0.24.0          // ASGI server
pyodbc==5.3.0                      // SQL Server driver
pydantic==2.5.0                    // Data validation
pillow>=10.0.0                     // Image processing
rembg==2.0.56                      // Background remover
python-multipart>=0.0.6            // File uploads
```

**¿Qué hace cada uno?**
- **fastapi**: Rutas, validación automática, documentación
- **uvicorn**: Servidor HTTP asincrónico
- **pyodbc**: Conector a SQL Server via ODBC
- **pydantic**: Validación de modelos (schemas)
- **pillow**: Redimensionar, procesar imágenes
- **rembg**: Remover fondo de imágenes con IA (U²-Net)
- **python-multipart**: Parsear FormData (uploads)

---

## Status del Proyecto

### ✅ Completado

- [x] **Estructura base Vue 3 + Vite**
- [x] **Autenticación (Registro/Login)** en FastAPI
- [x] **Generador de imágenes IA** (Stability AI)
- [x] **Cargador de imágenes** (upload local)
- [x] **Selector de productos** (dinámico con agente IA)
- [x] **Agente IA con OLLAMA** (catálogo dinámico desde BD)
- [x] **Integración BD → OLLAMA → Frontend** (circuito completo)
- [x] **Fallback automático** (si OLLAMA falla, usa Python)
- [x] **RUN.bat maestro** (inicio completo con un click)
- [x] **Preview del diseño** con controles de posición/zoom
- [x] **Integración Mercado Pago** (crear pagos)
- [x] **Almacenamiento en SQL Server** (pedidos y usuarios)
- [x] **Removedor de fondo** (rembg)
- [x] **Composable useApi** (reutilizable fetch)
- [x] **Scripts de testing** (test-circuito.ps1, verificar-sistema.py)

---

### 🚀 En Desarrollo

- [ ] **Webhook de Mercado Pago** (confirmar pagos automáticamente)
- [ ] **Dashboard de admin** (ver pedidos, usuarios, reportes)
- [ ] **Email transaccional** (confirmación de órdenes)
- [ ] **Historial de diseños** (mis diseños para usuarios)
- [ ] **Galería de ejemplos** (carousel con opciones guardadas)
- [ ] **Tests unitarios** (Jest para Vue, pytest para FastAPI)
- [ ] **Documentación Swagger 100%** (todos los endpoints)
- [ ] **Cache y optimización** (Redis para sesiones)

---

### 🐛 Bugs Conocidos

- [ ] **Timeout en generación de imágenes** > 30s (Stability AI lento)
- [ ] **CORS errors** si backend y frontend en dominios diferentes
- [ ] **Sesión expira** sin warning al usuario
- [ ] **Upload de imágenes** sin validación de tamaño máximo

---

### 📊 Velocidad Estimada

| Operación | Tiempo |
|-----------|--------|
| Generar imagen (IA) | 20-60 seg |
| Upload imagen local | < 2 seg |
| Crear pedido | < 1 seg |
| Crear pago (MP) | < 2 seg |
| Remover fondo | 5-15 seg |

---

### 📦 Tamaño del Proyecto

```
Frontend:      ~50 KB (Vue + CSS)
Backend:       ~200 KB (FastAPI app)
Dependencias:  ~2 GB (node_modules + venv)
Total:         ~2.2 GB
```

---

## Flujo de Desarrollo Típico

### Para el Frontend
```powershell
# Terminal 1: Dev server con hot reload
cd frontend
npm run dev
# Abre http://localhost:5173

# Edita App.vue, components/*, assets/*
# Cambios se reflejan en tiempo real (1 seg)

# Para producción:
npm run build  # Genera /dist listo para deploy
```

### Para el Backend
```powershell
# Terminal 2: Backend con auto-reload
cd database/source
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --reload --port 8000

# Abre http://localhost:8000/docs (Swagger)
# Edita app.py, db.py, conexion.py
# Cambios recargan automáticamente

# Para producción:
uvicorn app:app --port 8000 --workers 4
```

---

## Troubleshooting

### Frontend no carga
```
❌ Error: Cannot find module 'vue'
✅ Solución: npm install en carpeta frontend

❌ Error: CORS error en fetch
✅ Solución: Backend debe tener CORS habilitado
           o Frontend debe usar proxy (vite.config.js)
```

### Backend no conecta a BD
```
❌ Error: pyodbc.InterfaceError: [08001]
✅ Solución: 
  • Verificar SQL Server ejecutándose
  • Verificar credenciales en .env
  • Verificar nombre del servidor (SERVER\SQLEXPRESS)
```

### Generación de imágenes muy lenta
```
❌ Error: Timeout después de 30 segundos
✅ Solución:
  • Aumentar timeout en app.py
  • Usar modelos más rápidos en Stability AI
  • Aumentar memoria/CPU de máquina
```

---

## Líneas de Contacto / Equipo

```
Proyecto: AI Print Studio (Prendete Rock)
Propósito: Educativo + Producción
Estado: En desarrollo activo

Componentes Operativos:
✅ Frontend Vue 3 + Vite
✅ Backend FastAPI
✅ Agente IA (OLLAMA + Flask)
✅ SQL Server (85 productos)
✅ Integración Mercado Pago

Última actualización: 22 de abril 2026
Versión del sistema: 2.0 (con Agente IA integrado)
```

---

**Fin del Manual**

Este documento proporciona una visión completa de la arquitectura, componentes, flujos y tecnologías del proyecto. Para actualizaciones, consulta el README.md en la raíz del proyecto.
