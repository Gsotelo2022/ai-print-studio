# 🤖 Sistema Modular de Agentes IA

Sistema de múltiples agentes especializados que trabajan en conjunto para proporcionar capacidades de IA al sistema.

## 📋 Agentes Disponibles

### 1. **Agente de Productos** (Puerto 5001)
- **Archivo**: `agente_productos.py`
- **Función**: Genera catálogo dinámico de productos desde la BD
- **Modelo**: qwen2.5:1.5b
- **Endpoints**:
  - `GET /productos-ia` → Lista de productos con variantes
  - `GET /health` → Estado del agente

### 2. **Agente de Precios** (Puerto 5002)
- **Archivo**: `agente_precios.py`
- **Función**: Actualiza precios mediante lenguaje natural
- **Modelo**: qwen2.5:1.5b
- **Endpoints**:
  - `POST /api/cambiar-precio` → "cambiar remera a 12000"
  - `GET /api/health` → Estado del agente

### 3. **Agente de Business Intelligence** (Puerto 5003)
- **Archivo**: `agente_bi.py`
- **Función**: Analiza datos y responde consultas sobre el negocio
- **Modelo**: qwen2.5:1.5b (upgradeable a 3b)
- **Endpoints**:
  - `POST /api/consultar` → Consultas en lenguaje natural
  - `GET /api/health` → Estado del agente

## 🚀 Uso

### Iniciar todos los agentes
```bash
# Desde la carpeta raíz del proyecto
RUN.bat

# O manualmente desde agentes-Ollama/
cd agentes-Ollama
start-all-agentes.bat
```

### Detener todos los agentes
```bash
# Desde la carpeta raíz
stop.bat
```

### Iniciar un agente individual
```bash
cd agentes-Ollama
call .venv\Scripts\activate.bat
python agente_productos.py   # Puerto 5001
python agente_precios.py     # Puerto 5002
python agente_bi.py          # Puerto 5003
```

## 🔧 Requisitos

1. **OLLAMA instalado y corriendo**
   ```bash
   ollama serve
   ```

2. **Modelo descargado**
   ```bash
   ollama pull qwen2.5:1.5b
   ```

3. **Entorno virtual configurado**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install flask flask-cors requests pyodbc
   ```

4. **SQL Server con base de datos PrendeteRock**

## 📊 Ejemplos de Uso

### Agente de BI (Dashboard)
```javascript
// Desde el frontend
fetch('http://localhost:5003/api/consultar', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    consulta: "¿Cuánto vendí hoy?" 
  })
})
.then(r => r.json())
.then(data => {
  console.log(data.respuesta); // "Vendiste $45,000 en 8 pedidos"
  console.log(data.datos);     // Array con los datos
})
```

### Agente de Precios
```javascript
fetch('http://localhost:5002/api/cambiar-precio', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    consulta: "cambiar remera a 15000" 
  })
})
```

### Agente de Productos
```javascript
fetch('http://localhost:5001/productos-ia')
  .then(r => r.json())
  .then(productos => {
    console.log(productos);
    // [{ id_producto: 1, producto: "Remera", talles: ["S","M","L"], ... }]
  })
```

## 🏗️ Arquitectura

```
RUN.bat
  └── start-all-agentes.bat
       ├── agente_productos.py  (5001)
       ├── agente_precios.py    (5002)
       └── agente_bi.py         (5003)
           ├── OLLAMA (11434)
           └── SQL Server (PrendeteRock)
```

## ⚡ Performance

| Modelo | RAM Uso | Velocidad | Calidad SQL |
|--------|---------|-----------|-------------|
| qwen2.5:1.5b | ~2GB | Muy rápido | Buena |
| qwen2.5:3b | ~4GB | Medio | Excelente |

**Recomendación actual**: `qwen2.5:1.5b` para i3 + 16GB RAM

## 🔄 Upgrade del modelo (opcional)

Si el agente BI genera SQL con errores, upgradear a 3b:

```bash
ollama pull qwen2.5:3b
```

Luego editar en `agente_bi.py`:
```python
MODEL = "qwen2.5:3b"  # Cambiar de 1.5b a 3b
```

## 📝 Logs y Debug

Cada agente muestra logs en su ventana de terminal:
- ✅ `[OLLAMA] ✓ Respuesta recibida` → OK
- ❌ `[OLLAMA] ❌ Error` → Revisar conexión
- `[SQL] Ejecutando: SELECT...` → Query generada

## 🐛 Troubleshooting

### "Error: No se puede conectar a OLLAMA"
```bash
# Verificar que OLLAMA esté corriendo
ollama serve
```

### "Error conectando a BD"
- Verificar SQL Server: `DESKTOP-6FHC0B7\SQLEXPRESS`
- Verificar base de datos: `PrendeteRock`
- Driver: `ODBC Driver 17 for SQL Server`

### "Agente no responde"
```bash
# Verificar que el puerto esté escuchando
netstat -an | findstr :5003
```

## 📚 Consultas de Ejemplo para el Agente BI

- "¿Cuánto vendí hoy?"
- "¿Cuál es el producto más vendido?"
- "Pedidos pendientes de pago"
- "Clientes nuevos esta semana"
- "Top 5 productos"
- "¿Qué pidió el cliente juan@email.com?"
- "Ventas totales del mes"

## 🎯 Próximas Mejoras

- [ ] Agregar cache de queries frecuentes
- [ ] Implementar streaming de respuestas
- [ ] Agregar gráficos automáticos
- [ ] Sistema de alertas (stock bajo, pedidos sin pagar)
- [ ] Exportar reportes a PDF/Excel

---

**Última actualización**: Abril 2026
