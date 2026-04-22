# ==============================================
# CONFIGURACIÓN DEL AGENTE IA - MODO PRUEBA
# ==============================================
#
# El agente está configurado en MODO PRUEBA para
# procesar solo 10 productos y acelerar las pruebas
# con el modelo OLLAMA qwen2.5:1.5b
#
# ==============================================

## MODO ACTUAL: PRUEBA (10 productos)

**Ubicación:** `agentes-Ollama/agente_productos.py`
**Línea:** 14

```python
LIMITE_PRODUCTOS = 10  # MODO PRUEBA
```

## CAMBIAR A PRODUCCIÓN (TODOS los productos)

**Opción 1: Procesar TODOS (85 productos)**
```python
LIMITE_PRODUCTOS = None  # Sin límite
```

**Opción 2: Limitar a cantidad específica**
```python
LIMITE_PRODUCTOS = 20  # Solo 20 productos
LIMITE_PRODUCTOS = 50  # Solo 50 productos
```

## RENDIMIENTO ESPERADO

| Hardware  | Productos | OLLAMA Timeout | Tiempo esperado |
|-----------|-----------|----------------|-----------------|
| i3 16GB   | 10        | 60s            | 15-30s          |
| i3 16GB   | 50        | 120s           | 60-90s          |
| i3 16GB   | 85        | 180s           | 90-120s         |
| i5+ 16GB  | 85        | 60s            | 30-45s          |

## FALLBACK AUTOMÁTICO

Si OLLAMA no responde en el timeout configurado, el agente automáticamente:

1. **Detecta el timeout**
2. **Activa modo fallback** (sin IA)
3. **Agrupa productos usando Python puro**
4. **Retorna JSON idéntico al de OLLAMA**

**Resultado:** El frontend **SIEMPRE funciona**, con o sin OLLAMA.

## QUERY SQL ACTUAL

```sql
-- Modo prueba (10 productos)
SELECT TOP 10 Detalle, Color, talle FROM Productos

-- Modo producción (todos)
SELECT Detalle, Color, talle FROM Productos
```

## CIRCUITO COMPLETO

```
1. Frontend (App.vue)
   └─ cargarProductosDelAgente()
       ↓
2. HTTP GET → http://localhost:5001/productos-ia
       ↓
3. Agente IA (Python Flask)
   ├─ Consulta SQL Server (TOP 10 o todos)
   ├─ Arma prompt con JSON
   └─ Envía a OLLAMA
       ↓
4. OLLAMA (qwen2.5:1.5b)
   └─ Procesa, agrupa, ordena
       ↓
5. Retorna JSON:
   [
     {"producto":"Buzo","talles":["S","M","L"],"colores":["Blanca"]},
     {"producto":"Remera","talles":["S","M","L","XL"],"colores":["Negra"]}
   ]
       ↓
6. Frontend (ProductSelector.vue)
   └─ Dibuja selectores dinámicos
```

## TESTING

**Probar el circuito completo:**
```powershell
.\test-circuito.ps1
```

**Llamar directamente al agente:**
```powershell
curl http://localhost:5001/productos-ia
```

**Ver logs en tiempo real:**
```
Ventana "Agente IA - http://localhost:5001/productos-ia"
```

## DESPUÉS DE CAMBIAR LIMITE_PRODUCTOS

1. **Detener el agente:** CTRL+C en su ventana
2. **Reiniciar:**
   ```powershell
   cd c:\projects\ai-print-studio\agentes-Ollama
   .\.venv\Scripts\python.exe agente_productos.py
   ```

3. **O ejecutar RUN.bat completo** (reinicia todo)

## NOTAS

- **Timeout configurado:** 60 segundos (línea 58 de agente_productos.py)
- **Fallback activado:** Automático si OLLAMA falla
- **Modelo recomendado:** qwen2.5:1.5b (optimizado para i3/16GB)
- **Puerto agente:** 5001
- **Puerto OLLAMA:** 11434
