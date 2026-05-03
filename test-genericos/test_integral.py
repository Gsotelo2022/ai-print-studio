"""
test_integral.py -- Test de integracion completo para AI Print Studio
======================================================================
Cubre el flujo completo de la aplicacion:
  * Login admin y cliente
  * Catalogo de productos
  * Crear pedido como cliente
  * Historial de pedidos del cliente
  * Administracion: listar, ver detalle, cambiar estado y pago
  * Dashboard y estadisticas
  * Cupones disponibles

Requisitos:
  * Servidor FastAPI corriendo en localhost:8001 (o TEST_BASE_URL)
  * PostgreSQL con la BD PrendeteRock inicializada y con usuarios de prueba
  * pip install requests psycopg2-binary

Ejecutar:
  python test-genericos/test_integral.py
"""
# -*- coding: utf-8 -*-
import sys
import os
import json
import traceback
import psycopg2
import requests
from datetime import datetime

# Configurar stdout para UTF-8 en Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_URL  = os.environ.get("TEST_BASE_URL", "http://localhost:8001")
PG_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "PrendeteRock",
    "user":     "postgres",
    "password": "Pasteldepapas123#",
}

# ─── Helpers ────────────────────────────────────────────────────────────────

GREEN  = "\033[32m"
RED    = "\033[31m"
YELLOW = "\033[33m"
CYAN   = "\033[36m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

results = []  # (nombre, ok, detalle)

def ok(name, detail=""):
    results.append((name, True, detail))
    print(f"  {GREEN}OK{RESET} {name}" + (f"  ->  {detail}" if detail else ""))

def fail(name, detail=""):
    results.append((name, False, detail))
    print(f"  {RED}FAIL{RESET} {name}" + (f"  ->  {detail}" if detail else ""))

def section(title):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")

def get(url, token=None, params=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return requests.get(f"{BASE_URL}{url}", headers=headers, params=params, timeout=15)

def post(url, payload, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.post(f"{BASE_URL}{url}", data=json.dumps(payload), headers=headers, timeout=15)

def put(url, payload, token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    return requests.put(f"{BASE_URL}{url}", data=json.dumps(payload), headers=headers, timeout=15)


# ─── 0. Obtener credenciales desde la BD ────────────────────────────────────

def obtener_usuarios_prueba():
    """Devuelve (admin_email, admin_password, cliente_email, cliente_password)"""
    conn = psycopg2.connect(**PG_CONFIG)
    cur  = conn.cursor()

    # Admin: id=1  —  si el hash bcrypt proviene del test_postgresql.py usamos la contraseña conocida
    cur.execute("SELECT email FROM usuarios WHERE tipo='admin' ORDER BY id_usuario LIMIT 1")
    row = cur.fetchone()
    admin_email = row[0] if row else None

    cur.execute("SELECT email FROM usuarios WHERE tipo='cliente' ORDER BY id_usuario LIMIT 1")
    row = cur.fetchone()
    cliente_email = row[0] if row else None

    cur.close()
    conn.close()
    return admin_email, "Admin1234!", cliente_email, "Cliente1234!"


# ─── 1. Servidor activo ──────────────────────────────────────────────────────

section("1 · SERVIDOR")
try:
    r = requests.get(f"{BASE_URL}/docs", timeout=5)
    ok(f"Servidor responde en {BASE_URL}", f"HTTP {r.status_code}")
except Exception as e:
    fail("Servidor responde en localhost:8000", str(e))
    print(f"\n{RED}AVISO: El servidor no esta disponible en {BASE_URL}. Abortando tests.{RESET}")
    sys.exit(1)


# ─── 2. Obtener credenciales ─────────────────────────────────────────────────

section("2 · CREDENCIALES DESDE BD")
try:
    ADMIN_EMAIL, ADMIN_PASS, CLIENTE_EMAIL, CLIENTE_PASS = obtener_usuarios_prueba()
    ok("Leer emails de usuarios de prueba desde PostgreSQL", f"admin={ADMIN_EMAIL}, cliente={CLIENTE_EMAIL}")
except Exception as e:
    fail("Leer emails de usuarios de prueba", str(e))
    sys.exit(1)

if not ADMIN_EMAIL or not CLIENTE_EMAIL:
    fail("Se requieren al menos 1 admin y 1 cliente en BD")
    sys.exit(1)


# ─── 3. Login ────────────────────────────────────────────────────────────────

section("3 · AUTENTICACIÓN")
ADMIN_TOKEN   = None
CLIENTE_TOKEN = None
CLIENTE_ID    = None

try:
    r = post("/api/login", {"email": ADMIN_EMAIL, "password": ADMIN_PASS})
    assert r.status_code == 200, f"HTTP {r.status_code}: {r.text}"
    data = r.json()
    assert data.get("success"), data
    ADMIN_TOKEN = data["data"]["token"]
    ok("Login admin", f"user_id={data['data']['user_id']}, tipo={data['data']['tipo']}")
except Exception as e:
    fail("Login admin", str(e))

try:
    r = post("/api/login", {"email": CLIENTE_EMAIL, "password": CLIENTE_PASS})
    assert r.status_code == 200, f"HTTP {r.status_code}: {r.text}"
    data = r.json()
    assert data.get("success"), data
    CLIENTE_TOKEN = data["data"]["token"]
    CLIENTE_ID    = data["data"]["user_id"]
    ok("Login cliente", f"user_id={CLIENTE_ID}, tipo={data['data']['tipo']}")
except Exception as e:
    fail("Login cliente", str(e))

# Login incorrecto → 401
try:
    r = post("/api/login", {"email": ADMIN_EMAIL, "password": "WrongPass999!"})
    assert r.status_code == 401, f"Esperado 401, obtenido {r.status_code}"
    ok("Login con contraseña incorrecta retorna 401")
except Exception as e:
    fail("Login con contraseña incorrecta retorna 401", str(e))


# ─── 4. Catálogo de productos ────────────────────────────────────────────────

section("4 · PRODUCTOS")
ID_VARIANTE = None

try:
    r = get("/api/productos")
    assert r.status_code == 200, f"HTTP {r.status_code}"
    data = r.json()
    assert data.get("success"), data
    productos = data["data"]
    ok("GET /api/productos", f"{len(productos)} producto(s)")

    if productos:
        primer_prod = productos[0]
        variantes = primer_prod.get("variantes", [])
        if variantes and variantes[0].get("stock", 0) > 0:
            ID_VARIANTE = variantes[0]["id_variante"]
            ok("Variante disponible encontrada", f"id_variante={ID_VARIANTE}, precio={variantes[0]['precio']}")
        else:
            print(f"  {YELLOW}⚠  No hay variantes con stock — el test de pedido será omitido{RESET}")
except Exception as e:
    fail("GET /api/productos", str(e))

# Detalle variante (si existe)
if ID_VARIANTE:
    try:
        r = get(f"/api/variante/{ID_VARIANTE}")
        assert r.status_code == 200, f"HTTP {r.status_code}"
        d = r.json()["data"]
        ok(f"GET /api/variante/{ID_VARIANTE}", f"sku={d.get('sku')}, precio={d.get('precio')}")
    except Exception as e:
        fail(f"GET /api/variante/{ID_VARIANTE}", str(e))


# ─── 5. Crear pedido como cliente ────────────────────────────────────────────

section("5 · CREAR PEDIDO (cliente)")
ID_PEDIDO = None

if CLIENTE_TOKEN and CLIENTE_ID and ID_VARIANTE:
    payload_order = {
        "user_id":          CLIENTE_ID,
        "items":            [{"id_variante": ID_VARIANTE, "cantidad": 1}],
        "direccion_envio":  "Av. Corrientes 1234",
        "ciudad":           "Buenos Aires",
        "telefono_contacto":"011-1234-5678",
        "notas_cliente":    "Test integral automatizado",
    }
    try:
        r = post("/api/create-order", payload_order, token=CLIENTE_TOKEN)
        assert r.status_code == 200, f"HTTP {r.status_code}: {r.text[:300]}"
        data = r.json()
        assert data.get("success"), data
        ID_PEDIDO = data["data"]["order_id"]
        ok("POST /api/create-order", f"id_pedido={ID_PEDIDO}, total={data['data']['total']}, numero={data['data']['numero_orden']}")
    except Exception as e:
        fail("POST /api/create-order", str(e))
else:
    print(f"  {YELLOW}⚠  Skipped: no hay variante con stock o cliente no autenticado{RESET}")

# Sin autenticación → 401/403
try:
    r = post("/api/create-order", {"user_id": 1, "items": []})
    assert r.status_code in (401, 403), f"Esperado 401/403, obtenido {r.status_code}"
    ok("POST /api/create-order sin token retorna 401/403")
except Exception as e:
    fail("POST /api/create-order sin token retorna 401/403", str(e))


# ─── 6. Historial del cliente ─────────────────────────────────────────────────

section("6 · MIS PEDIDOS (cliente)")
if CLIENTE_TOKEN and CLIENTE_ID:
    try:
        r = get(f"/api/mis-pedidos/{CLIENTE_ID}", token=CLIENTE_TOKEN)
        assert r.status_code == 200, f"HTTP {r.status_code}: {r.text[:300]}"
        data = r.json()
        assert data.get("success"), data
        pedidos = data["data"]
        ok(f"GET /api/mis-pedidos/{CLIENTE_ID}", f"{len(pedidos)} pedido(s)")
        if ID_PEDIDO:
            ids = [p["id_pedido"] for p in pedidos]
            assert ID_PEDIDO in ids, f"Pedido {ID_PEDIDO} no aparece en el historial"
            ok("Pedido recién creado aparece en el historial")
    except Exception as e:
        fail(f"GET /api/mis-pedidos/{CLIENTE_ID}", str(e))
else:
    print(f"  {YELLOW}⚠  Skipped{RESET}")


# ─── 7. Admin — listar pedidos ────────────────────────────────────────────────

section("7 · ADMIN — PEDIDOS")
if ADMIN_TOKEN:
    try:
        r = get("/api/admin/pedidos", token=ADMIN_TOKEN, params={"page": 1, "limit": 10})
        assert r.status_code == 200, f"HTTP {r.status_code}: {r.text[:300]}"
        data = r.json()
        assert data.get("success"), data
        pag = data.get("paginacion", {})
        ok("GET /api/admin/pedidos", f"total_registros={pag.get('total_registros')}, paginas={pag.get('total_paginas')}")
    except Exception as e:
        fail("GET /api/admin/pedidos", str(e))

    # Filtros
    for filtro in ["pendientes", "pagados", "no-pagados"]:
        try:
            r = get("/api/admin/pedidos", token=ADMIN_TOKEN, params={"filtro": filtro, "page": 1, "limit": 5})
            assert r.status_code == 200, f"HTTP {r.status_code}"
            ok(f"GET /api/admin/pedidos?filtro={filtro}")
        except Exception as e:
            fail(f"GET /api/admin/pedidos?filtro={filtro}", str(e))

    # Acceso sin token
    try:
        r = get("/api/admin/pedidos")
        assert r.status_code in (401, 403), f"Esperado 401/403, obtenido {r.status_code}"
        ok("GET /api/admin/pedidos sin token retorna 401/403")
    except Exception as e:
        fail("GET /api/admin/pedidos sin token retorna 401/403", str(e))

    # Acceso con token de cliente (no admin)
    if CLIENTE_TOKEN:
        try:
            r = get("/api/admin/pedidos", token=CLIENTE_TOKEN)
            assert r.status_code in (401, 403), f"Esperado 401/403, obtenido {r.status_code}"
            ok("GET /api/admin/pedidos con token cliente retorna 401/403")
        except Exception as e:
            fail("GET /api/admin/pedidos con token cliente retorna 401/403", str(e))

else:
    print(f"  {YELLOW}⚠  Skipped{RESET}")


# ─── 8. Admin — detalle de pedido ────────────────────────────────────────────

section("8 · ADMIN — DETALLE PEDIDO")
if ADMIN_TOKEN and ID_PEDIDO:
    try:
        r = get(f"/api/admin/pedidos/{ID_PEDIDO}", token=ADMIN_TOKEN)
        assert r.status_code == 200, f"HTTP {r.status_code}: {r.text[:300]}"
        data = r.json()["data"]
        ok(f"GET /api/admin/pedidos/{ID_PEDIDO}", f"numero={data.get('numero_orden')}, estado={data.get('estado')}, items={len(data.get('items',[]))}")
    except Exception as e:
        fail(f"GET /api/admin/pedidos/{ID_PEDIDO}", str(e))

    # 404 en pedido inexistente
    try:
        r = get("/api/admin/pedidos/9999999", token=ADMIN_TOKEN)
        assert r.status_code == 404, f"Esperado 404, obtenido {r.status_code}"
        ok("GET /api/admin/pedidos/9999999 retorna 404")
    except Exception as e:
        fail("GET /api/admin/pedidos/9999999 retorna 404", str(e))
else:
    print(f"  {YELLOW}⚠  Skipped (requiere pedido creado){RESET}")


# ─── 9. Admin — cambiar estado pedido ─────────────────────────────────────────

section("9 · ADMIN — CAMBIAR ESTADO PEDIDO")
if ADMIN_TOKEN and ID_PEDIDO:
    for nuevo_estado in ["en_proceso", "enviado", "completado"]:
        try:
            r = put(f"/api/admin/pedidos/{ID_PEDIDO}/estado", {"estado": nuevo_estado}, token=ADMIN_TOKEN)
            assert r.status_code == 200, f"HTTP {r.status_code}: {r.text[:300]}"
            data = r.json()
            assert data.get("success"), data
            ok(f"PUT /api/admin/pedidos/{ID_PEDIDO}/estado → {nuevo_estado}")
        except Exception as e:
            fail(f"PUT estado → {nuevo_estado}", str(e))
else:
    print(f"  {YELLOW}⚠  Skipped{RESET}")


# ─── 10. Admin — cambiar estado de pago ───────────────────────────────────────

section("10 · ADMIN — CAMBIAR ESTADO DE PAGO")
if ADMIN_TOKEN and ID_PEDIDO:
    try:
        r = put(f"/api/admin/pedidos/{ID_PEDIDO}/pago", {
            "estado_pago": "aprobado",
            "metodo_pago": "transferencia",
            "referencia_externa": "TEST-REF-001",
        }, token=ADMIN_TOKEN)
        assert r.status_code == 200, f"HTTP {r.status_code}: {r.text[:300]}"
        ok(f"PUT /api/admin/pedidos/{ID_PEDIDO}/pago → aprobado")
    except Exception as e:
        fail(f"PUT /api/admin/pedidos/{ID_PEDIDO}/pago", str(e))

    # Verificar que se actualizó
    try:
        r = get(f"/api/admin/pedidos/{ID_PEDIDO}", token=ADMIN_TOKEN)
        data = r.json()["data"]
        assert data["estado_pago"] == "aprobado", f"estado_pago={data['estado_pago']}"
        ok("Verificación: estado_pago actualizado a 'aprobado'")
    except Exception as e:
        fail("Verificación estado_pago", str(e))
else:
    print(f"  {YELLOW}⚠  Skipped{RESET}")


# ─── 11. Admin — clientes ──────────────────────────────────────────────────────

section("11 · ADMIN — CLIENTES")
if ADMIN_TOKEN:
    try:
        r = get("/api/admin/clientes", token=ADMIN_TOKEN, params={"page": 1, "limit": 10})
        assert r.status_code == 200, f"HTTP {r.status_code}: {r.text[:300]}"
        data = r.json()
        assert data.get("success"), data
        pag = data.get("paginacion", {})
        ok("GET /api/admin/clientes", f"total={pag.get('total_registros')}, devueltos={len(data['data'])}")
    except Exception as e:
        fail("GET /api/admin/clientes", str(e))

    # Buscar por nombre
    try:
        r = get("/api/admin/clientes", token=ADMIN_TOKEN, params={"buscar": "cliente", "page": 1, "limit": 5})
        assert r.status_code == 200, f"HTTP {r.status_code}"
        ok("GET /api/admin/clientes?buscar=cliente")
    except Exception as e:
        fail("GET /api/admin/clientes?buscar=cliente", str(e))
else:
    print(f"  {YELLOW}⚠  Skipped{RESET}")


# ─── 12. Admin — dashboard stats ───────────────────────────────────────────────

section("12 · ADMIN — DASHBOARD STATS")
if ADMIN_TOKEN:
    try:
        r = get("/api/admin/dashboard-stats", token=ADMIN_TOKEN)
        assert r.status_code == 200, f"HTTP {r.status_code}: {r.text[:300]}"
        data = r.json()
        assert data.get("success"), data
        stats = data.get("stats", {})
        ok("GET /api/admin/dashboard-stats",
           f"usuarios={stats.get('total_usuarios')}, semana={stats.get('usuarios_semana')}")
    except Exception as e:
        fail("GET /api/admin/dashboard-stats", str(e))
else:
    print(f"  {YELLOW}⚠  Skipped{RESET}")


# ─── 13. Admin — usuarios ──────────────────────────────────────────────────────

section("13 · ADMIN — USUARIOS")
if ADMIN_TOKEN:
    try:
        r = get("/api/users", token=ADMIN_TOKEN)
        assert r.status_code == 200, f"HTTP {r.status_code}: {r.text[:300]}"
        data = r.json()
        ok("GET /api/users", f"{len(data['data'])} usuario(s)")
    except Exception as e:
        fail("GET /api/users", str(e))
else:
    print(f"  {YELLOW}⚠  Skipped{RESET}")


# ─── 14. Admin — productos ─────────────────────────────────────────────────────

section("14 · ADMIN — PRODUCTOS")
if ADMIN_TOKEN:
    try:
        r = get("/api/admin/productos", token=ADMIN_TOKEN)
        assert r.status_code == 200, f"HTTP {r.status_code}: {r.text[:300]}"
        data = r.json()
        ok("GET /api/admin/productos", f"{len(data['data'])} producto(s) activo(s)")
    except Exception as e:
        fail("GET /api/admin/productos", str(e))
else:
    print(f"  {YELLOW}⚠  Skipped{RESET}")


# ─── 15. Cupones disponibles ───────────────────────────────────────────────────

section("15 · CUPONES")
if CLIENTE_TOKEN and CLIENTE_ID:
    try:
        r = get(f"/api/cupones/disponibles/{CLIENTE_ID}", token=CLIENTE_TOKEN)
        assert r.status_code == 200, f"HTTP {r.status_code}: {r.text[:300]}"
        data = r.json()
        assert data.get("success"), data
        cupones = data["data"].get("cupones", [])
        ok(f"GET /api/cupones/disponibles/{CLIENTE_ID}", f"{len(cupones)} cupón(es) disponible(s)")
    except Exception as e:
        fail(f"GET /api/cupones/disponibles/{CLIENTE_ID}", str(e))
else:
    print(f"  {YELLOW}⚠  Skipped{RESET}")


# ─── 16. Registro de nuevo usuario ─────────────────────────────────────────────

section("16 · REGISTRO")
ts = datetime.now().strftime("%H%M%S")
try:
    r = post("/api/register", {
        "fullname": f"Usuario Test {ts}",
        "email":    f"test_{ts}@prueba.com",
        "phone":    "011-9999-0000",
        "password": "TestPass1234!",
    })
    assert r.status_code == 200, f"HTTP {r.status_code}: {r.text[:300]}"
    data = r.json()
    assert data.get("success"), data
    assert "token" in data["data"], "No se recibió token al registrar"
    ok("POST /api/register nuevo usuario", f"user_id={data['data']['user_id']}")
except Exception as e:
    fail("POST /api/register nuevo usuario", str(e))

# Email duplicado → 409
try:
    r = post("/api/register", {
        "fullname": "Duplicado",
        "email":    CLIENTE_EMAIL,
        "password": "Dup1234!",
    })
    assert r.status_code == 409, f"Esperado 409, obtenido {r.status_code}"
    ok("POST /api/register email duplicado retorna 409")
except Exception as e:
    fail("POST /api/register email duplicado retorna 409", str(e))


# ─── Resumen final ─────────────────────────────────────────────────────────────

section("RESUMEN FINAL")
total   = len(results)
passed  = sum(1 for _, ok_, _ in results if ok_)
failed  = total - passed

print(f"\n  {'Test':<55} {'Estado':>10}")
print(f"  {'─'*55} {'─'*10}")
for name, ok_, detail in results:
    estado = f"{GREEN}PASS{RESET}" if ok_ else f"{RED}FAIL{RESET}"
    detalle_corto = (detail[:35] + "…") if len(detail) > 38 else detail
    print(f"  {name:<55} {estado}  {YELLOW}{detalle_corto}{RESET}")

print(f"\n{BOLD}  Total: {total}  |  {GREEN}PASS: {passed}{RESET}{BOLD}  |  {RED}FAIL: {failed}{RESET}")

if failed == 0:
    print(f"\n{GREEN}{BOLD}  TODOS LOS TESTS PASARON.{RESET}\n")
else:
    print(f"\n{RED}{BOLD}  {failed} test(s) fallaron.{RESET}\n")

sys.exit(0 if failed == 0 else 1)
