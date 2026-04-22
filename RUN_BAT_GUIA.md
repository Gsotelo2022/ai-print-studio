# ✅ SISTEMA DE INICIO RÁPIDO: RUN.bat

## 🎯 Qué es

`RUN.bat` es un **script único que inicia TODO lo necesario** para trabajar en tu web con un solo clic:

### Qué hace automáticamente:

1. **Verifica e Instala Dependencias**
   - Python (FastAPI, uvicorn, pyodbc)
   - Node.js (Vue.js, Vite)
   - PHP/Composer (Mercado Pago, opcional)

2. **Inicia 3 Servidores (en paralelo)**
   - ✅ FastAPI Backend (127.0.0.1:8000)
   - ✅ Vue.js Frontend (localhost:5173)
   - ✅ PHP Backend (localhost:8080, si PHP disponible)

3. **Abre automáticamente el navegador**
   - En http://localhost:5173

4. **Muestra instrucciones claras**
   - Status de cada servidor
   - Credenciales de prueba
   - Qué hacer después

---

## 🚀 Cómo Usarlo

### Opción 1: Doble Clic (MÁS FÁCIL)
```
Navega a: c:\projects\ai-print-studio\
Doble-clic en: RUN.bat
```

### Opción 2: Desde PowerShell
```powershell
cd c:\projects\ai-print-studio
.\RUN.bat
```

### Opción 3: Desde CMD
```cmd
cd c:\projects\ai-print-studio
RUN.bat
```

---

## 📊 Qué ves cuando se ejecuta

```
═════════════════════════════════════════════════════════
   INICIANDO APLICACIÓN COMPLETA
   Prendete Rock - AI Print Studio
   [Un clic para todo]
═════════════════════════════════════════════════════════

[1] Verificando dependencias Python...
    ✓ Dependencias Python OK

[2] Verificando dependencias Node.js...
    ✓ Dependencias Node.js OK

[3] Verificando PHP y Composer...
    ✓ PHP detectado

[4] Configuración del Proyecto:
    BASE DE DATOS:
    ├─ Servidor: SQLEXPRESS01
    ├─ BD: PrendeteRock
    └─ Pool: SQL Server (Windows Auth)
    
    SERVIDORES A INICIAR:
    ├─ FastAPI Backend ........... http://127.0.0.1:8000
    ├─ Vue.js Frontend ........... http://localhost:5173
    └─ PHP Backend ............... http://localhost:8080

[5] Iniciando servidores...
    [►] Iniciando FastAPI Backend...
    [►] Iniciando Vue.js Frontend...
    [►] Iniciando PHP Backend...

✅ APLICACIÓN INICIADA

  Se abrieron 2-3 ventanas automáticamente:

  ① FastAPI Backend
     http://127.0.0.1:8000
     ✓ Login, Registro, Pedidos
     ✓ Generación de imágenes con IA
     ✓ Procesamiento de órdenes

  ② Vue.js Frontend (ABRE AQUÍ)
     http://localhost:5173
     ✓ Interfaz de usuario web
     ✓ Formularios y galería
     ✓ Carrito de compras

  ③ PHP Backend (si PHP está disponible)
     http://localhost:8080
     ✓ Integración Mercado Pago
     ✓ Procesamiento de pagos

  ⏳ Abriendo navegador en 5 segundos...
```

---

## 🪟 Ventanas que se Abren

Se abrirán **2-3 ventanas de consola** en paralelo:

| # | Servidor | Puerto | Color | Importante |
|---|----------|--------|-------|-----------|
| ① | FastAPI | 127.0.0.1:8000 | Rojo | ✅ NO CIERRES |
| ② | Vue.js | localhost:5173 | Azul | ✅ NO CIERRES |
| ③ | PHP | localhost:8080 | Verde | ⚠️ Opcional |

**NO CIERRES NINGUNA** hasta que termines de trabajar.

---

## 📝 Credenciales de Prueba

```
Cliente:
  Email:    cliente@test.com
  Password: password123

Admin:
  Email:    admin@test.com
  Password: password123
```

---

## ✨ Mejoras Implementadas

### Versión anterior (problemas):
- ❌ Rutas hardcodeadas
- ❌ No autodetectaba .venv
- ❌ Mensajes confusos
- ❌ No abría navegador automáticamente
- ❌ Orden incorrecto de servidores

### Nueva versión (mejorada):
- ✅ Detecta automáticamente rutas
- ✅ Busca .venv en múltiples ubicaciones
- ✅ Mensajes claros y en español
- ✅ Abre navegador automáticamente en http://localhost:5173
- ✅ Inicia servidores en orden correcto
- ✅ Valida dependencias antes de iniciar
- ✅ Manejo inteligente de PHP opcional
- ✅ Interfaz visual mejorada con emojis y tablas

---

## 🔍 Verificaciones que Hace

1. **Python Environment**
   - Busca .venv
   - Si no existe, usa versión global
   - Instala paquetes si faltan

2. **Node.js Dependencies**
   - Verifica node_modules
   - Ejecuta npm install si es primera vez
   - Detecta cambios en package.json

3. **PHP/Composer**
   - Verifica que PHP esté instalado
   - Si no, muestra advertencia pero continúa
   - Instala vendor si es primera vez

4. **Directorios**
   - Verifica que existan los directorios necesarios
   - Se posiciona en directorios correctos
   - Usa rutas relativas y absolutas inteligentemente

---

## 🛑 Cómo Detener

**Opción 1**: Cierra todas las ventanas de consola

**Opción 2**: En cada ventana, presiona:
```
Ctrl + C
```

**Opción 3**: Si se traba, abre Task Manager:
```
Ctrl + Shift + Esc
→ Busca "python", "node", "php"
→ Click derecho → Terminar tarea
```

---

## ⚠️ Si Algo Falla

### "No se puede conectar al servidor"
- Espera 10 segundos, los servidores están iniciando lentamente

### "Error en base de datos"
- Verifica que **SQL Server Express está corriendo**
- En Windows Services, busca "MSSQL SQLEXPRESS01"

### "npm no reconocido"
- Instala Node.js desde: https://nodejs.org/
- Reinicia PowerShell después de instalar
- Intenta de nuevo

### "Python no reconocido"
- Instala Python desde: https://python.org/
- Marca la opción "Add Python to PATH" durante instalación
- Reinicia PowerShell

### "PHP no se encuentra"
- Es OPCIONAL para desarrollo
- Solo afecta a Mercado Pago
- Descarga desde: https://php.net/ si necesitas

---

## 📂 Archivos Relacionados

```
c:\projects\ai-print-studio\
├── RUN.bat                  ← El script maestro (TÚ HACES CLIC AQUÍ)
├── LEEME.txt                ← Instrucciones rápidas
├── REGISTRO_QUICKSTART.md   ← Guía de 3 pasos
├── REGISTRO_SOLUCION.md     ← Detalles técnicos
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│
├── backend/
│   └── composer.json
│
└── database/
    └── source/
        ├── app.py           ← FastAPI
        ├── db.py            ← Conexión BD
        └── requirements.txt
```

---

## 🎯 Flujo completo

```
TÚ HACES CLIC EN RUN.bat
        ↓
Script verifica dependencias
        ↓
Instala lo que falta
        ↓
Inicia FastAPI Backend
        ↓
Inicia Vue Frontend
        ↓
Inicia PHP (si disponible)
        ↓
Abre navegador automáticamente
        ↓
¡LISTO! Comenzá a desarrollar
```

---

## 🚀 Próximos Pasos

1. **Haz clic en RUN.bat**
2. **Espera a que se abra el navegador** (~10 segundos)
3. **Ve a http://localhost:5173** (debería estar ya abierto)
4. **Prueba el registro** con un email nuevo
5. **Haz login** con el email que registraste
6. **¡Disfruta desarrollando!**

---

## 📞 Soporte

Si necesitas help:

1. Revisa [REGISTRO_USUARIOS.md](database/source/REGISTRO_USUARIOS.md)
2. Revisa [LEEME.txt](LEEME.txt)
3. Verifica los logs en las ventanas de consola
4. Confirma que SQL Server está corriendo

---

**Última actualización**: 21 de abril de 2026  
**Status**: ✅ Funcionando
