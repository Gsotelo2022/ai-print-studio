# Estructura del sistema

Este documento describe la arquitectura y el flujo de funcionamiento del sistema AI Print Studio, tanto para el cliente (usuarios finales) como para el administrador (panel de gestión).

---

## 1. Arquitectura general

- **Frontend:** SPA desarrollada en Vue.js (ubicada en `/frontend`).
- **Backend:** API REST construida con FastAPI (ubicada en `/database/source/app_v2.py`).
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

4. **Migraciones y mantenimiento:**
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

**Actualizado:** 23/04/2026
