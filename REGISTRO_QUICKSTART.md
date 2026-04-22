# ⚡ INICIO RÁPIDO: Sistema de Registro

## 🚀 Inicia en 3 pasos

### 1️⃣ Abre PowerShell en la carpeta del proyecto
```powershell
cd c:\projects\ai-print-studio\database\source
```

### 2️⃣ Ejecuta el servidor FastAPI
```powershell
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

O si prefieres, usa el script:
```powershell
.\start-fastapi.ps1
```

Deberías ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 3️⃣ En otra terminal, prueba que funciona
```powershell
cd c:\projects\ai-print-studio\database\source
python test_register.py
```

✅ Deberías ver un mensaje de registro exitoso

---

## 📱 Usa desde el Frontend

1. Abre `http://localhost:5173` en tu navegador
2. Click en **"Registrarme"**
3. Completa los datos:
   - Nombre completo
   - Email (debe ser único)
   - Teléfono (opcional)
   - Contraseña (mín 6 caracteres)
4. Click en **"Registrarme"**

✅ Usuario creado en la BD

---

## 🧪 Prueba el Sistema Completo

```powershell
# Test básico
python test_register.py

# Test completo (incluye todas las validaciones)
python test_register_complete.py

# Test flujo completo (registro + login)
python test_auth_flow.py
```

---

## 🔗 Endpoints Disponibles

```
POST http://127.0.0.1:8000/api/register
POST http://127.0.0.1:8000/api/login
GET  http://127.0.0.1:8000/api/health
```

---

## 📌 Importantemantener ambas terminales abiertas:

- **Terminal 1**: Servidor FastAPI (no cierres)
- **Terminal 2**: Pruebas, frontend, desarrollo

---

## 🆘 Si algo no funciona

**Servidor FastAPI no está corriendo:**
```powershell
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

**Base de datos no conecta:**
- Verifica que SQL Server Express está activo
- Verifica que la BD `PrendeteRock` existe

**Email ya registrado:**
- Usa otro email (los anteriores de test ya fueron eliminados)

---

## 📂 Archivos Importantes

- `app.py` - API FastAPI (endpoints)
- `db.py` - Conexión a SQL Server
- `start-fastapi.bat` - Script para iniciar servidor
- `test_register*.py` - Tests para verificar
- `REGISTRO_USUARIOS.md` - Documentación completa

---

¡Todo listo! 🎉

El sistema de registro funciona perfectamente.
