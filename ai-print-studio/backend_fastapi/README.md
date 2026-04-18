FastAPI backend para Prendete-Rock

Instalación y ejecución local (no requiere XAMPP):

1) Crear un virtualenv e instalar dependencias:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

2) Copiar `.env.example` a `.env` y ajustar variables (DB_SERVER, DB_NAME, DB_UID, DB_PWD).

3) Ejecutar el servidor:

```bash
uvicorn main:app --reload --port 8000
```

Endpoints:
- GET  /api/users      -> lista usuarios
- POST /api/register   -> registra usuario (JSON: fullname,email,phone,password)
- POST /api/login      -> login (JSON: email,password)

Notas:
- Requiere driver ODBC para SQL Server instalado (ODBC Driver 17 o similar).
- Si usás Trusted Connection en Windows, dejá DB_UID/DB_PWD vacíos y setea TRUSTED_CONNECTION=yes
