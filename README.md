# AI Print Studio

> Diseña y compra estampados personalizados con inteligencia artificial.

Proyecto educativo para aprender arquitectura web moderna: **Vue 3 + PHP + SQL Server**.

---

## Estructura del Proyecto

```
ai-print-studio/
│
├── backend/                         ← API REST en PHP
│   ├── config/
│   │   ├── app.php                  ← Claves API (Stability AI, MercadoPago)
│   │   └── database.php             ← Conexión PDO a SQL Server
│   ├── helpers/
│   │   └── response.php             ← Funciones JSON (éxito, error, validación)
│   ├── api/
│   │   ├── generate-image.php       ← POST: genera imagen con Stability AI
│   │   ├── create-order.php         ← POST: guarda pedido en SQL Server
│   │   └── create-payment.php       ← POST: crea pago en MercadoPago
│   └── uploads/                     ← Imágenes generadas (auto-creado)
│
├── frontend/                        ← App Vue 3 con Vite
│   ├── index.html                   ← HTML base (punto de entrada)
│   ├── package.json                 ← Dependencias npm
│   ├── vite.config.js               ← Config Vite + proxy al backend
│   └── src/
│       ├── main.js                  ← Inicializa Vue y monta la app
│       ├── App.vue                  ← Componente raíz (orquestador)
│       ├── composables/
│       │   └── useApi.js            ← Hook reutilizable para llamadas fetch
│       ├── components/
│       │   ├── PromptGenerator.vue  ← Paso 1: escribe prompt y genera imagen
│       │   ├── ProductSelector.vue  ← Paso 2: elige producto y variantes
│       │   ├── PreviewPanel.vue     ← Paso 3: preview + confirma pedido
│       │   └── CheckoutPanel.vue    ← Paso 4: pago con MercadoPago
│       └── assets/
│           └── styles.css           ← Estilos globales de la app
│
├── database/
│   └── schema.sql                   ← CREATE TABLE pedidos
│
└── README.md                        ← Este archivo
```

---

## Flujo Completo (cómo se conecta todo)

```
USUARIO                 FRONTEND (Vue)          BACKEND (PHP)           APIs EXTERNAS
  │                         │                       │                       │
  │  1. Escribe prompt      │                       │                       │
  │ ──────────────────────► │                       │                       │
  │                         │  fetch POST           │                       │
  │                         │  /api/generate-image  │                       │
  │                         │ ────────────────────► │                       │
  │                         │                       │  cURL POST            │
  │                         │                       │ ────────────────────► │ Stability AI
  │                         │                       │ ◄──────────────────── │ (imagen)
  │                         │ ◄──────────────────── │                       │
  │  2. Ve imagen           │  { imagen_url }       │                       │
  │ ◄────────────────────── │                       │                       │
  │                         │                       │                       │
  │  3. Elige producto      │                       │                       │
  │ ──────────────────────► │                       │                       │
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
