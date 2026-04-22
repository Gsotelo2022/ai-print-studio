# Sistema de Registro de Usuarios - Guía Completa

## Estado Actual ✓

El sistema de registro de usuarios está **completamente funcional**:
- ✓ Base de datos SQL Server (PrendeteRock) 
- ✓ Tabla Usuarios con estructura correcta
- ✓ Hash de contraseñas (PBKDF2 SHA256)
- ✓ API REST en FastAPI en puerto 8000
- ✓ Validación de emails duplicados

## Estructura de la BD

```
Tabla: Usuarios (SQL Server - PrendeteRock)
├── id_usuario (INT, Identity, PK)
├── Nombre (VARCHAR NOT NULL)
├── Email (VARCHAR NOT NULL, UNIQUE) 
├── telefono (VARCHAR, Nullable)
├── password_user (VARCHAR NOT NULL) - Almacena hash PBKDF2
└── Tipo (VARCHAR, Nullable) - Default: "cliente"
```

## Cómo Usar

### 1. Iniciar el Servidor FastAPI

**Opción A: Script Batch (Recomendado)**
```batch
cd c:\projects\ai-print-studio\database\source
start-fastapi.bat
```

**Opción B: PowerShell**
```powershell
cd c:\projects\ai-print-studio\database\source
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

**Opción C: Python directo**
```
cd c:\projects\ai-print-studio\database\source
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

El servidor estará disponible en: **http://127.0.0.1:8000**

### 2. Probar el Registro

**Test Básico:**
```bash
cd c:\projects\ai-print-studio\database\source
python test_register.py
```

**Test Completo (incluye validaciones):**
```bash
cd c:\projects\ai-print-studio\database\source
python test_register_complete.py
```

## Endpoints Disponibles

### POST /api/register
Registra un nuevo usuario

**Request:**
```json
{
  "fullname": "Juan Perez",
  "email": "juan@example.com",
  "phone": "+541123456789",
  "password": "Password123"
}
```

**Response (Exitoso):**
```json
{
  "success": true,
  "data": {
    "id_usuario": 7,
    "Nombre": "Juan Perez",
    "Email": "juan@example.com"
  }
}
```

**Response (Email duplicado):**
```json
{
  "success": false,
  "error": "El email ya está registrado"
}
```

### POST /api/login
Autentica un usuario

**Request:**
```json
{
  "email": "juan@example.com",
  "password": "Password123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id_usuario": 7,
    "Nombre": "Juan Perez",
    "Email": "juan@example.com",
    "Tipo": "cliente"
  }
}
```

## Validaciones Implementadas

✓ **Email Duplicado**: No permite registrar el mismo email dos veces (Constraint UNIQUE)
✓ **Campos Requeridos**: fullname, email, password son obligatorios
✓ **Contrasela Segura**: Se hashea con PBKDF2-SHA256 + salt aleatorio
✓ **Tipos de Datos**: Validación de tipos con Pydantic

## Archivos Importantes

```
database/source/
├── app.py              ← Código de la API FastAPI
├── db.py               ← Conexión a SQL Server
├── test_register.py    ← Test simple
├── test_register_complete.py ← Test con validaciones
├── start-fastapi.bat   ← Script para iniciar servidor
├── start-fastapi.ps1   ← Script PowerShell
└── requirements.txt    ← Dependencias Python
```

## Solución de Problemas

### Error: "No se puede establecer una conexión"
**Causa**: El servidor FastAPI no está corriendo
**Solución**: 
```bash
cd c:\projects\ai-print-studio\database\source
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

### Error: "Connection refused" desde BD
**Causa**: SQL Server no está corriendo
**Solución**: Verificar que SQL Server Express está activo
```powershell
# En PowerShell (como Administrador):
Get-Service "MSSQL*"
```

### Error: "Base de datos no existe"
**Causa**: La BD PrendeteRock no fue creada
**Solución**: 
```bash
# Ejecutar el script SQL:
cd c:\projects\ai-print-studio\database
sqlcmd -S .\SQLEXPRESS01 -i estructura-BDD-Prendete-Rock.sql
```

## Logs y Debugging

Cuando el servidor FastAPI está corriendo, verás logs como:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [1234]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Para más detalles de debugging, revisa la consola donde corre el servidor.

---

**Última actualización**: 21 de abril de 2026
