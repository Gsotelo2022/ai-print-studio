# AI Print Studio

> Diseña y compra estampados personalizados con inteligencia artificial.

Proyecto web moderno: **Vue 3 + FastAPI (Python) + PostgreSQL + Ollama**.

---

## 🚀 Inicio Rápido

### Scripts Disponibles

| Script | Descripción |
|--------|-------------|
| **`RUN.bat`** | ✅ Inicia toda la aplicación (Backend + Frontend + IA) |
| **`stop.bat`** | 🛑 Detiene todos los servidores |

### Ejecutar la aplicación completa

```bash
# Desde la raíz del proyecto
RUN.bat
```

Esto iniciará automáticamente:
- 🔹 **FastAPI Backend** en `http://127.0.0.1:8000` (con virtual environment)
- 🔹 **Vue.js Frontend** en `http://localhost:5173`
- 🔹 **Ollama IA** para generación de imágenes (si está instalado)
- 🔹 **Node Backend** en `http://127.0.0.1:3000` (para generación de imágenes)

### Detener la aplicación

```bash
# Desde la raíz del proyecto
stop.bat
```

---

## Estructura del Proyecto

```
ai-print-studio/
│
├── backend/
│   ├── api_python/                  ← API REST con FastAPI (BACKEND ACTIVO)
│   │   ├── app_v2.py                ← Aplicación principal FastAPI
│   │   ├── db.py                    ← Conexión a PostgreSQL
│   │   ├── api/
│   │   │   ├── routers/             ← Endpoints organizados por módulo
│   │   │   │   ├── auth.py          ← Registro y login
│   │   │   │   ├── productos.py     ← Catálogo de productos
│   │   │   │   ├── pedidos.py       ← Crear pedidos y pagos
│   │   │   │   ├── disenos.py       ← Subir y listar diseños
│   │   │   │   ├── cupones.py       ← Descuentos
│   │   │   │   └── admin.py         ← Panel administrativo
│   │   │   └── dependencies.py      ← Funciones auxiliares
│   │   └── requirements.txt         ← Dependencias Python
│   │
│   ├── server.js                    ← Node server para generación de imágenes
│   └── uploads/                     ← Archivos subidos
│
├── frontend/                        ← App Vue 3 con Vite
│   ├── index.html                   ← HTML base
│   ├── package.json                 ← Dependencias npm
│   ├── vite.config.js               ← Config Vite
│   └── src/
│       ├── main.js                  ← Inicializa Vue
│       ├── App.vue                  ← Componente raíz (orquestador)
│       ├── composables/
│       │   └── useApi.js            ← Composable para llamadas API
│       ├── components/
│       │   ├── Login.vue            ← Autenticación
│       │   ├── CreateUser.vue       ← Registro de usuarios
│       │   ├── GenerateImage.vue    ← Generar imagen con IA
│       │   ├── ImageUploader.vue    ← Subir imagen propia
│       │   ├── BackgroundRemover.vue← Remover fondo de imagen
│       │   ├── ProductSelector.vue  ← Seleccionar producto
│       │   ├── PreviewPanel.vue     ← Vista previa del producto
│       │   ├── CheckoutPanel.vue    ← Pago con MercadoPago
│       │   ├── MisDisenosGaleria.vue← Galería de diseños del usuario
│       │   ├── MisPedidos.vue       ← Historial de pedidos
│       │   └── AdminDashboard.vue   ← Panel de administración
│       └── assets/
│           └── styles.css           ← Estilos globales (modo nocturno)
│
├── agentes-Ollama/                  ← Agentes IA con Ollama
│   ├── agente-productos/            ← Gestión de catálogo
│   ├── agente-precios/              ← Cálculo de precios
│   └── agente-cupones/              ← Generación de descuentos
│
└── README.md                        ← Este archivo
```

---

## Flujo Completo

```
USUARIO              FRONTEND (Vue)       BACKEND (FastAPI)      APIs/IA
  │                      │                      │                  │
  │  1. Login/Registro   │                      │                  │
  │ ───────────────────► │  POST /api/login     │                  │
  │                      │ ───────────────────► │                  │
  │                      │ ◄─────────────────── │ (JWT token)      │
  │                      │                      │                  │
  │  2. Crear diseño     │                      │                  │
  │ ───────────────────► │  POST /api/generate  │                  │
  │                      │ ───────────────────► │  cURL to Ollama  │
  │                      │                      │ ───────────────► │
  │                      │                      │ ◄─────────────── │ (imagen)
  │                      │ ◄─────────────────── │                  │
  │                      │                      │                  │
  │  3. Elegir producto  │                      │                  │
  │ ───────────────────► │  GET /api/productos  │                  │
  │                      │ ───────────────────► │                  │
  │                      │ ◄─────────────────── │ (catálogo)       │
  │                         │  fetch POST           │                       │
  │  4. Confirma            │  /api/create-order    │                       │
  │ ──────────────────────► │ ────────────────────► │                       │
  │                         │                       │  INSERT INTO pedidos  │
  │                         │                       │ ──────► SQL Server    │
  │                         │ ◄──────────────────── │                       │
  │  5. Click "Pagar"       │  { order_id }         │                       │
  │ ──────────────────────► │                       │                       │
  │                         │  fetch POST           │                       │
  │                         │  /api/create-payment  │                       │
  │                         │ ────────────────────► │                       │
  │                         │                       │  cURL POST            │
  │                         │                       │ ────────────────────► │ MercadoPago
  │                         │                       │ ◄──────────────────── │ (init_point)
  │                         │ ◄──────────────────── │                       │
  │  6. Redirige a MP       │  { payment_url }      │                       │
  │ ◄════════════════════════════════════════════► MercadoPago (pago)      │
  │  7. Vuelve a la app     │                       │                       │
  │ ──────────────────────► │  ?payment=success     │                       │
```

---

## Requisitos Previos

### Backend
- **PHP 8.0+** con extensiones: `pdo_sqlsrv`, `curl`, `json`
- **SQL Server** (local o remoto)
- Servidor web: Apache, Nginx o el built-in de PHP

### Frontend
- **Node.js 18+** y npm

### Cuentas API
- [Stability AI](https://platform.stability.ai/) - API key para generar imágenes
- [MercadoPago Developers](https://www.mercadopago.com.ar/developers) - Access token

---

## Instalación y Ejecución

### 1. Base de Datos
```sql
-- En SQL Server Management Studio o sqlcmd:
CREATE DATABASE ai_print_studio;
GO
USE ai_print_studio;
GO
-- Ejecutar el contenido de database/schema.sql
```

### 2. Backend PHP
```bash
# Configurar claves en backend/config/app.php
# Configurar conexión DB en backend/config/database.php

# Opción A: Servidor built-in de PHP (desarrollo)
cd backend
php -S localhost:8080

# Opción B: Configurar en Apache/Nginx apuntando a /backend/
```

### 3. Frontend Vue
```bash
cd frontend
npm install          # Instala Vue, Vite, etc.
npm run dev          # Inicia servidor de desarrollo en localhost:5173
```

### 4. Abrir en el navegador
```
http://localhost:5173
```

---

## Conceptos Clave para Aprender

| Concepto | Dónde se usa | Qué hace |
|----------|-------------|----------|
| **Composition API** | `<script setup>` en .vue | Forma moderna de escribir lógica en Vue 3 |
| **ref() / reactive()** | Componentes Vue | Variables que actualizan la UI automáticamente |
| **props** | Componentes hijos | Datos que un padre pasa a un hijo |
| **emit()** | Componentes hijos | Eventos que un hijo envía al padre |
| **composables** | useApi.js | Funciones reutilizables (como hooks en React) |
| **fetch()** | useApi.js | Peticiones HTTP desde el navegador |
| **cURL** | PHP endpoints | Peticiones HTTP desde el servidor |
| **PDO** | database.php | Acceso seguro a SQL Server desde PHP |
| **Prepared Statements** | create-order.php | Prevención de SQL injection |
| **CORS** | response.php | Permitir peticiones entre dominios distintos |
| **Proxy** | vite.config.js | Redirigir /api/ al backend PHP en desarrollo |
| **JSON** | Todo el proyecto | Formato universal de intercambio de datos |

---

## Tecnologías

- **Frontend:** Vue 3 (Composition API) + Vite
- **Backend:** PHP 8 (vanilla, sin framework)
- **Base de Datos:** SQL Server (PDO)
- **APIs:** Stability AI (imágenes), MercadoPago (pagos)
- **Comunicación:** fetch (frontend) ↔ JSON ↔ cURL (backend)
