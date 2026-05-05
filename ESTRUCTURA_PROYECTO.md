# AI Print Studio - Estructura del Proyecto

**Versión:** 2.1.0  
**Fecha:** Mayo 2026  
**Documento:** Estructura Técnica del Sistema

---

## 📋 Índice

1. [Arquitectura General](#arquitectura-general)
2. [Estructura de Directorios](#estructura-de-directorios)
3. [Stack Tecnológico](#stack-tecnológico)
4. [Servicios y Puertos](#servicios-y-puertos)
5. [Base de Datos](#base-de-datos)
6. [APIs y Endpoints](#apis-y-endpoints)
7. [Agentes IA](#agentes-ia)
8. [Dependencias](#dependencias)

---

## 🏗️ Arquitectura General

AI Print Studio es una plataforma web multi-servicio que combina:

```
┌─────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA DEL SISTEMA                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐      ┌──────────────┐      ┌────────────┐ │
│  │   Frontend  │◄────►│   Backend    │◄────►│  Base de   │ │
│  │   Vue.js    │      │   FastAPI    │      │   Datos    │ │
│  │  (Port 5173)│      │  (Port 8000) │      │ SQLite/PG  │ │
│  └─────────────┘      └──────────────┘      └────────────┘ │
│         │                     │                              │
│         │              ┌──────┴──────┐                       │
│         └─────────────►│   Backend   │                       │
│                        │   Node.js   │                       │
│                        │  (Port 3000)│                       │
│                        └─────────────┘                       │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              MICROSERVICIOS IA (Agentes)              │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │                                                         │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐      │  │
│  │  │  Agente    │  │  Agente    │  │  Agente    │      │  │
│  │  │  Prompts   │  │  Pedidos   │  │  Cupones   │      │  │
│  │  │ (Port 5004)│  │ (Port 5003)│  │ (Port 5001)│      │  │
│  │  └────────────┘  └────────────┘  └────────────┘      │  │
│  │         │               │               │              │  │
│  │         └───────────────┴───────────────┘              │  │
│  │                         │                               │  │
│  │                   ┌─────▼──────┐                       │  │
│  │                   │   Ollama   │                       │  │
│  │                   │ qwen2.5    │                       │  │
│  │                   │(Port 11434)│                       │  │
│  │                   └────────────┘                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              SERVICIOS EXTERNOS                        │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │  • Replicate API - Flux Schnell (Generación imágenes)│  │
│  │  • Remove.bg (Eliminación de fondos)                  │  │
│  │  • Mercado Pago (Procesamiento de pagos)              │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Componentes Principales

1. **Frontend**: Interfaz de usuario en Vue.js con Vite
2. **Backend Principal**: API REST en FastAPI (Python) 
3. **Backend Secundario**: Servidor Node.js para generación de imágenes
4. **Agentes IA**: Microservicios inteligentes con Ollama
5. **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)

---

## 📁 Estructura de Directorios

```
ai-print-studio/
│
├── 📄 Readme.md                      # Manual de usuario completo
├── 📄 RUN.bat                        # Script inicio rápido
├── 📄 stop.bat                       # Script detención servicios
│
├── 📁 agentes-Ollama/                # Microservicios IA
│   ├── setup_agente.bat              # Configuración inicial
│   ├── start-all-agentes.bat         # Inicio todos los agentes
│   │
│   ├── 📁 agente-cupones/            # Gestión descuentos
│   │   ├── agente_descuentos.py      # Lógica principal
│   │   ├── api_descuentos.py         # API FastAPI
│   │   ├── requirements.txt          # Dependencias Python
│   │   ├── start-agente-descuentos.bat
│   │   └── README.md
│   │
│   ├── 📁 agente-pedidos/            # Chatbot soporte cliente
│   │   ├── agente_pedidos.py         # Flask + TF-IDF + Ollama
│   │   ├── faq_sql_ollama.xlsx       # Base conocimiento FAQ
│   │   ├── requirements.txt
│   │   └── start-agente-pedidos.bat
│   │
│   └── 📁 agente-prompts/            # Optimización prompts IA
│       ├── agente_prompts.py         # Flask + Ollama
│       ├── requirements.txt
│       └── start-agente-prompts.bat
│
├── 📁 backend/                       # Backend principal
│   ├── 📄 server.js                  # Node.js (Port 3000)
│   ├── 📄 generateImage.js           # Generación imágenes IA
│   ├── 📄 package.json               # Dependencias Node
│   │
│   ├── 📁 api_python/                # API FastAPI principal
│   │   ├── app_v2.py                 # Aplicación principal
│   │   ├── db.py                     # Conexión base de datos
│   │   ├── requirements.txt          # Dependencias Python
│   │   │
│   │   ├── 📁 api/
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py       # Auth, JWT, validaciones
│   │   │   │
│   │   │   ├── 📁 routers/           # Endpoints API
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py           # Login, registro, JWT
│   │   │   │   ├── productos.py      # CRUD productos
│   │   │   │   ├── cupones.py        # Validación cupones
│   │   │   │   ├── pedidos.py        # Gestión pedidos
│   │   │   │   ├── disenos.py        # Galería diseños
│   │   │   │   └── admin.py          # Panel administrador
│   │   │
│   │   └── 📁 logs/                  # Logs aplicación
│   │
│   ├── 📁 config/                    # Archivos configuración
│   ├── 📁 db/
│   │   └── Base-de-datos.sql         # Script inicial DB
│   ├── 📁 helpers/                   # Funciones auxiliares
│   ├── 📁 models/
│   │   └── schema.sql                # Esquema base de datos
│   └── 📁 uploads/                   # Archivos subidos
│       ├── designs/                  # Diseños clientes
       ├── imagenes/                 # Imágenes generadas con IA y productos
│       └── thumbnails/               # Miniaturas
│
├── 📁 frontend/                      # Aplicación Vue.js
│   ├── 📄 index.html                 # HTML principal
│   ├── 📄 package.json               # Dependencias Node/Vue
│   ├── 📄 vite.config.js             # Configuración Vite
│   │
│   ├── 📁 mockups/                   # Mockups productos
│   │
│   └── 📁 src/
│       ├── App.vue                   # Componente raíz
│       ├── main.js                   # Entry point
│       │
│       ├── 📁 assets/
│       │   └── styles.css            # Estilos globales
│       │
│       ├── 📁 components/            # Componentes Vue (27 archivos)
│       │   ├── AdminDashboard.vue    # Panel administrador
│       │   ├── BackgroundRemover.vue # Quitar fondo imágenes
│       │   ├── ChatBot.vue           # Chat con agente
│       │   ├── CheckoutPanel.vue     # Finalizar pedido
│       │   ├── ConfiguracionView.vue # Configuración admin
│       │   ├── CreateUser.vue        # Registro usuario
│       │   ├── CuponesDisponibles.vue # Lista cupones
│       │   ├── DashboardView.vue     # Dashboard cliente
│       │   ├── EditClienteModal.vue  # Editar cliente
│       │   ├── GenerateImage.vue     # Generar con IA
│       │   ├── GestionClientes.vue   # Admin clientes
│       │   ├── GestionCupones.vue    # Admin cupones
│       │   ├── GestionPedidos.vue    # Admin pedidos
│       │   ├── GestionProductos.vue  # Admin productos
│       │   ├── HeroShowcase.vue      # Landing page
│       │   ├── ImageUploader.vue     # Subir imágenes
│       │   ├── Login.vue             # Login
│       │   ├── MisDisenosGaleria.vue # Galería cliente
│       │   ├── MisPedidos.vue        # Historial pedidos
│       │   ├── OrderSummary.vue      # Resumen pedido
│       │   ├── PreviewPanel.vue      # Preview producto
│       │   ├── ProductSelector.vue   # Selector productos
│       │   ├── PromptGenerator.vue   # Generador prompts
│       │   └── UsersList.vue         # Lista usuarios
│       │
│       ├── 📁 composables/           # Composables Vue
│       │   ├── useApi.js             # Cliente HTTP
│       │   └── useToast.js           # Notificaciones
│       │
│       └── 📁 pages/
│           └── Success.vue           # Página éxito pago
│
└── 📁 scripts/                       # Scripts utilidad
    ├── descargar-modelo-ia.bat       # Descarga modelo Ollama
    └── fix_passwords.py              # Reparar contraseñas DB

```

---

## 💻 Stack Tecnológico

### Frontend
- **Framework**: Vue.js 3.4.0
- **Build Tool**: Vite 5.0.0
- **State Management**: Pinia 2.3.1
- **Routing**: Vue Router 4.6.4
- **Estilo**: CSS vanilla (styles.css)

### Backend Principal (Python)
- **Framework**: FastAPI 0.104.1
- **Servidor ASGI**: Uvicorn 0.24.0
- **Validación**: Pydantic 2.5.0
- **Base de Datos**: 
  - SQLite (desarrollo)
  - PostgreSQL (producción) - psycopg2-binary 2.9.9
- **Autenticación**: JWT - python-jose 3.3.0
- **Procesamiento Imágenes**: 
  - Pillow 10.0.0
  - Rembg 2.0.56 (eliminación fondos)
- **HTTP Client**: httpx 0.27.0
- **Pagos**: mercadopago 2.0.0

### Backend Secundario (Node.js)
- **Runtime**: Node.js
- **Framework**: Express 5.2.1
- **IA Imágenes**: Replicate 1.4.0 (Flux Schnell)
- **HTTP Client**: node-fetch 3.3.2
- **CORS**: cors 2.8.6

### Agentes IA
- **Motor IA**: Ollama (qwen2.5:1.5b)
- **Frameworks**:
  - Flask (agente-prompts, agente-pedidos)
  - FastAPI (agente-cupones)
- **ML/NLP**:
  - scikit-learn (TF-IDF, similitud coseno)
  - pandas (procesamiento FAQ)
- **Base de Datos**: PostgreSQL (descuentos)

### Herramientas
- **Control de versiones**: Git
- **Variables de entorno**: python-dotenv
- **Linting/Format**: (no especificado en proyecto)

---

## 🌐 Servicios y Puertos

| Servicio | Puerto | Tecnología | Descripción |
|----------|--------|------------|-------------|
| **Frontend Vue** | 5173 | Vite Dev Server | Interfaz usuario |
| **Backend Node.js** | 3000 | Express | Generación imágenes IA |
| **API FastAPI** | 8000 | Uvicorn | Backend principal REST API |
| **Agente Cupones** | 5001 | FastAPI | Cálculo descuentos |
| **Agente Pedidos** | 5003 | Flask | Chatbot soporte |
| **Agente Prompts** | 5004 | Flask | Optimización prompts |
| **Ollama** | 11434 | Ollama Server | Motor IA local |
| **PostgreSQL** | 5432 | PostgreSQL | Base datos producción |

### URLs de Acceso

```
Frontend:        http://localhost:5173
API Principal:   http://localhost:8000
API Docs:        http://localhost:8000/docs
Backend Node:    http://localhost:3000
Agente Cupones:  http://localhost:5001
Agente Pedidos:  http://localhost:5003
Agente Prompts:  http://localhost:5004
```

---

## 🗄️ Base de Datos

### Esquema Principal

**Tablas:**

1. **usuarios**
   - id_usuario (PK)
   - nombre
   - email (único)
   - password (hash)
   - tipo_usuario (cliente/admin)
   - fecha_registro
   - activo

2. **productos**
   - id_producto (PK)
   - nombre
   - tipo (remera/buzo/taza/etc)
   - precio_base
   - variantes (JSON)
   - mockup_url
   - activo

3. **pedidos**
   - id_pedido (PK)
   - id_cliente (FK)
   - id_producto (FK)
   - cantidad
   - precio_unitario
   - subtotal
   - descuento_aplicado
   - total_final
   - estado (pendiente/proceso/listo/entregado)
   - estado_pago (pendiente/pagado/reembolsado)
   - diseno_url
   - fecha_pedido
   - fecha_actualizacion

4. **cupones**
   - id_cupon (PK)
   - codigo (único)
   - porcentaje_descuento
   - fecha_inicio
   - fecha_vencimiento
   - usos_maximos
   - usos_actuales
   - activo

5. **disenos**
   - id_diseno (PK)
   - id_cliente (FK)
   - url_imagen
   - origen (subida/generada_ia)
   - prompt (si es IA)
   - fecha_creacion

6. **cupones_usados**
   - id (PK)
   - id_cupon (FK)
   - id_pedido (FK)
   - id_cliente (FK)
   - fecha_uso

7. **descuentos_temporales**
   - id (PK)
   - nombre
   - porcentaje
   - fecha_inicio
   - fecha_fin
   - activo

### Archivos Base de Datos

- **Desarrollo**: `backend/db/prendeterock.db` (SQLite)
- **Producción**: PostgreSQL (configurar en .env)
- **Scripts**:
  - `backend/db/Base-de-datos.sql` - Datos iniciales
  - `backend/models/schema.sql` - Esquema completo

---

## 🔌 APIs y Endpoints

### API Principal (FastAPI - Port 8000)

#### Autenticación (`/api/auth`)
```
POST   /api/auth/register        # Registro nuevo usuario
POST   /api/auth/login           # Login (retorna JWT)
GET    /api/auth/me              # Obtener usuario actual
PUT    /api/auth/profile         # Actualizar perfil
```

#### Productos (`/api/productos`)
```
GET    /api/productos            # Lista todos productos activos
GET    /api/productos/{id}       # Detalle producto
POST   /api/productos            # Crear producto (admin)
PUT    /api/productos/{id}       # Actualizar producto (admin)
DELETE /api/productos/{id}       # Desactivar producto (admin)
```

#### Pedidos (`/api/pedidos`)
```
GET    /api/pedidos              # Lista pedidos del usuario
GET    /api/pedidos/{id}         # Detalle pedido
POST   /api/pedidos              # Crear pedido
PUT    /api/pedidos/{id}         # Actualizar estado (admin)
DELETE /api/pedidos/{id}         # Cancelar pedido
POST   /api/pedidos/checkout     # Iniciar pago MercadoPago
```

#### Cupones (`/api/cupones`)
```
GET    /api/cupones              # Lista cupones (admin)
POST   /api/cupones              # Crear cupón (admin)
POST   /api/cupones/validar      # Validar código cupón
PUT    /api/cupones/{id}         # Actualizar cupón (admin)
```

#### Diseños (`/api/disenos`)
```
GET    /api/disenos              # Galería diseños del usuario
POST   /api/disenos/upload       # Subir imagen
POST   /api/disenos/generate     # Generar con IA
DELETE /api/disenos/{id}         # Eliminar diseño
POST   /api/disenos/remove-bg    # Quitar fondo
```

#### Admin (`/api/admin`)
```
GET    /api/admin/dashboard      # Métricas dashboard
GET    /api/admin/clientes       # Lista clientes
GET    /api/admin/pedidos        # Todos los pedidos
GET    /api/admin/estadisticas   # Estadísticas ventas
PUT    /api/admin/cliente/{id}   # Actualizar cliente
```

### Backend Node.js (Port 3000)

```
POST   /generar-imagen           # Generar imagen con Replicate (Flux Schnell)
GET    /health                   # Health check
```

### Agente Prompts (Port 5004)

```
POST   /optimizar-prompt         # Optimizar descripción para generación de imágenes IA
GET    /health                   # Health check
```

### Agente Pedidos (Port 5003)

```
POST   /chat                     # Consultar chatbot
GET    /faq/count                # Cantidad FAQs cargadas
GET    /health                   # Health check
```

### Agente Cupones (Port 5001)

```
POST   /calcular-descuento       # Calcular descuento total pedido
POST   /validar-cupon            # Validar código específico
GET    /descuentos-disponibles   # Lista descuentos activos
GET    /health                   # Health check
```

---

## 🤖 Agentes IA

### 1. Agente de Prompts (Port 5004)

**Propósito**: Convertir descripciones en español a prompts optimizados para generadores de imágenes IA.

**Tecnología**:
- Flask
- Ollama (qwen2.5:1.5b)
- Limpieza y optimización de prompts

**Flujo**:
```
Usuario escribe descripción (ES)
    ↓
Agente traduce y optimiza con Ollama
    ↓
Retorna prompt en inglés con keywords
    ↓
Frontend envía a Replicate API (Flux Schnell)
```

**Ejemplo**:
```
Input:  "un gato naranja en el espacio"
Output: "orange cat floating in space, digital art, 
         high quality, detailed, sharp focus, 
         vibrant colors, cosmic background"
```

### 2. Agente de Pedidos (Port 5003)

**Propósito**: Chatbot de soporte al cliente con sistema híbrido FAQ + IA.

**Tecnología**:
- Flask
- pandas + scikit-learn (TF-IDF)
- Ollama (qwen2.5:1.5b)
- Excel FAQ (faq_sql_ollama.xlsx)

**Flujo**:
```
Consulta del cliente
    ↓
Búsqueda en FAQ con TF-IDF
    ↓
¿Similitud > 0.3?
    ├─ Sí → Responder con FAQ
    └─ No → Consultar Ollama con contexto
```

**Categorías FAQ**:
- Precios
- Estado pedidos
- Envíos
- Materiales productos
- Devoluciones

### 3. Agente de Cupones (Port 5001)

**Propósito**: Calcular y combinar descuentos automáticamente.

**Tecnología**:
- FastAPI
- PostgreSQL
- Lógica de negocio compleja

**Tipos de Descuentos**:
1. **Por cantidad**: Automático según unidades
2. **Por historial**: Cliente frecuente
3. **Cupones manuales**: Códigos promocionales
4. **Temporales**: Promociones por fecha

**Límites**:
- Descuento máximo combinado: **35%**
- Los descuentos se acumulan respetando el tope

**Flujo**:
```
Cliente ingresa pedido + cupón
    ↓
Agente consulta PostgreSQL
    ↓
Calcula descuento_cantidad
Calcula descuento_historial
Valida cupón (fecha, usos)
Consulta descuentos_temporales
    ↓
Combina todos (max 35%)
    ↓
Retorna descuento total
```

---

## 📦 Dependencias

### Frontend (package.json)

```json
{
  "dependencies": {
    "pinia": "^2.3.1",
    "vue": "^3.4.0",
    "vue-router": "^4.6.4"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```

### Backend Python (requirements.txt)

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
rembg==2.0.56
pillow>=10.0.0
python-multipart>=0.0.6
mercadopago>=2.0.0
python-dotenv>=1.0.0
httpx>=0.27.0
python-jose[cryptography]>=3.3.0
psycopg2-binary>=2.9.9
requests>=2.31.0
```

### Backend Node.js (package.json)

```json
{
  "dependencies": {
    "cors": "^2.8.6",
    "dotenv": "^17.4.2",
    "express": "^5.2.1",
    "node-fetch": "^3.3.2",
    "replicate": "^1.4.0"
  }
}
```

### Agentes IA (requirements.txt)

**Agente Prompts:**
```
flask>=3.0.0
flask-cors>=4.0.0
requests>=2.31.0
```

**Agente Pedidos:**
```
flask>=3.0.0
flask-cors>=4.0.0
pyodbc>=5.0.0
pandas>=2.0.0
openpyxl>=3.1.0
scikit-learn>=1.3.0
numpy>=1.24.0
requests>=2.31.0
```

**Agente Cupones:**
```
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
psycopg2-binary>=2.9.9
python-dotenv>=1.0.0
```

---

## 🔐 Variables de Entorno

Archivo `.env` (ubicar en raíz del proyecto):

```env
# Base de Datos PostgreSQL (Producción)
PG_HOST=127.0.0.1
PG_PORT=5432
PG_DB=PrendeteRock
PG_USER=postgres
PG_PASSWORD=tu_password

# JWT Autenticación
JWT_SECRET=tu_secret_key_muy_segura_aqui

# APIs Externas
REPLICATE_API_TOKEN=tu_replicate_api_token
REMOVE_BG_API_KEY=tu_removebg_api_key
MERCADOPAGO_ACCESS_TOKEN=tu_mercadopago_token

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:1.5b

# Paths
UPLOAD_DIR=./uploads
```

---

## 🚀 Scripts de Inicio

### RUN.bat
Inicia todo el sistema automáticamente:
- Ollama serve
- API FastAPI (backend Python)
- Backend Node.js
- Frontend Vue.js
- Abre navegador en http://localhost:5173

### start-all-agentes.bat
Inicia los microservicios IA:
- Agente Cupones (Port 5001)
- Agente Prompts (Port 5004)
- (Agente Pedidos se inicia separado)

### stop.bat
Detiene todos los servicios.

---

## 📝 Notas Técnicas

### Autenticación
- JWT con expiración de 24 horas
- Tokens almacenados en localStorage (frontend)
- Middleware de validación en FastAPI

### Almacenamiento Imágenes
- Diseños subidos por clientes: `backend/uploads/designs/`
- Imágenes generadas con IA: `backend/uploads/imagenes/`
- Thumbnails: `backend/uploads/thumbnails/`

### Logs
- Backend Python: `backend/api_python/logs/`
- Agentes: consola (no persistente)

### Base de Datos
- SQLite en desarrollo (no requiere instalación)
- PostgreSQL en producción (mejor rendimiento)
- Migraciones: scripts SQL manuales

---

## 🔄 Flujo de Datos Típico

### Generación de Imagen con IA

```
1. Cliente describe imagen (español)
2. Frontend → Agente Prompts (5004)
3. Agente Prompts → Ollama (optimiza prompt)
4. Frontend → Backend Node.js (3000) con prompt optimizado
5. Backend Node.js → Replicate API (Flux Schnell genera imagen)
6. Imagen guardada en backend/uploads/imagenes/
7. Frontend muestra imagen al cliente
```

### Crear Pedido con Descuento

```
1. Cliente selecciona producto + cantidad + cupón
2. Frontend → Agente Cupones (5001) con datos pedido
3. Agente Cupones → PostgreSQL (consulta historial)
4. Agente calcula descuento combinado (max 35%)
5. Frontend muestra precio final
6. Cliente confirma
7. Frontend → API FastAPI (8000) crea pedido
8. API FastAPI → Base de datos guarda pedido
9. API FastAPI → MercadoPago (genera link pago)
10. Cliente redirigido a MercadoPago
```

---

**Documento generado automáticamente**  
**AI Print Studio v2.1.0 - Mayo 2026**
