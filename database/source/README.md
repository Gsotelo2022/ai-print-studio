Backend Python - FastAPI + SQL Server

## Setup (Windows):

### 1. Crear y activar un virtualenv
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias
```powershell
python -m pip install -r requirements.txt
```

### 3. Ejecutar el servidor
```powershell
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

El servidor estará disponible en `http://127.0.0.1:8000`

## Endpoints disponibles

- `GET /api/health` - Health check
- `POST /api/register` - Registrar nuevo usuario
  - Payload: `{fullname, email, phone (opcional), password}`
- `POST /api/login` - Autenticar usuario
  - Payload: `{email, password}`

## Configuración de BD

La conexión a SQL Server usa:
- Driver: ODBC Driver 17 for SQL Server
- Server: localhost\SQLEXPRESS01
- Database: PrendeteRock
- Auth: Windows (Trusted_Connection)
