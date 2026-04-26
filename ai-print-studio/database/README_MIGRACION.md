# 🚀 EJECUCIÓN DE MIGRACIÓN DE BASE DE DATOS

## ✅ Pre-requisitos

Antes de ejecutar la migración, asegúrate de:

1. **SQL Server está corriendo** (Windows Service o SQL Server Express)
2. **Base de datos PrendeteRock existe**
3. **Python está instalado** (3.8 o superior)
4. **Módulo pyodbc instalado**: `pip install pyodbc`
5. **Cerrar todas las conexiones** a la base de datos (detener backend, cerrar SSMS, etc.)

## 🎯 Método 1: Ejecución Automática (RECOMENDADO)

### Windows:

1. Abre el explorador de archivos
2. Navega a `c:\projects\ai-print-studio\database\`
3. **Doble clic en `EJECUTAR-MIGRACION.bat`**
4. Sigue las instrucciones en pantalla

El script hará:
- ✅ Backup automático de la BD
- ✅ Crear nueva estructura
- ✅ Insertar productos iniciales
- ✅ Migrar datos existentes
- ✅ Migrar imágenes a archivos

## 🎯 Método 2: Ejecución Manual

### Si prefieres ejecutar paso por paso:

```powershell
# 1. Ir a la carpeta
cd c:\projects\ai-print-studio\database

# 2. Activar entorno virtual (si usas uno)
..\source\.venv\Scripts\activate

# 3. Instalar dependencias
pip install pyodbc pillow

# 4. Ejecutar migración
python ejecutar-migracion.py
```

## 📊 Proceso de Migración

El script ejecutará estos 5 pasos:

### Paso 1: Backup 💾
- Crea backup completo de PrendeteRock
- Ubicación: `C:\Backups\PrendeteRock_YYYYMMDD_HHMMSS.bak`
- **Si falla:** Revisa permisos de la carpeta C:\Backups

### Paso 2: Nueva Estructura 🏗️
- Crea 12 tablas nuevas
- Crea índices y constraints
- Crea triggers para stock y auditoría
- **Tiempo estimado:** 2-3 minutos

### Paso 3: Datos Iniciales 📦
- Inserta 5 productos base (Remera, Taza, Buzo, Gorra, Bolsa)
- Crea atributos (Color, Talle, Material)
- Crea ~20 variantes con precios
- **Tiempo estimado:** 1 minuto

### Paso 4: Migrar Datos Antiguos 🔄
- Migra usuarios existentes
- Migra pedidos a nueva estructura
- Mapea productos antiguos → variantes nuevas
- **Tiempo estimado:** 2-5 minutos (depende de cuántos datos tienes)

### Paso 5: Migrar Imágenes 🖼️
- Extrae imágenes base64 de la BD
- Las guarda como archivos .png
- Genera thumbnails
- Actualiza referencias
- **Tiempo estimado:** 1-3 minutos

## ⚠️ Problemas Comunes

### Error: "No se puede conectar a SQL Server"

**Solución:**
1. Verifica que SQL Server esté corriendo:
   - Abre "Servicios" de Windows
   - Busca "SQL Server (SQLEXPRESS)" o "SQL Server (MSSQLSERVER)"
   - Si está detenido, inícialo

2. Revisa el nombre del servidor:
   - Abre SSMS
   - Mira cómo te conectas (ej: `localhost`, `.\SQLEXPRESS`, etc.)
   - Edita `ejecutar-migracion.py` línea 60 con tu servidor

### Error: "pyodbc no instalado"

**Solución:**
```bash
pip install pyodbc
```

Si falla, instala el driver de SQL Server:
https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

### Error: "Cannot open backup device"

**Solución:**
1. Crea la carpeta manualmente: `C:\Backups`
2. Dale permisos completos a SQL Server
3. O edita el script `01-backup-bd-actual.sql` y cambia la ruta

### Error: "Database is in use"

**Solución:**
1. Cierra todas las aplicaciones que usen PrendeteRock
2. Cierra SQL Server Management Studio
3. Detén el backend FastAPI si está corriendo
4. Ejecuta este comando en SSMS:
   ```sql
   USE master;
   ALTER DATABASE PrendeteRock SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
   -- Ejecuta la migración
   ALTER DATABASE PrendeteRock SET MULTI_USER;
   ```

## 🔍 Verificar que la Migración fue Exitosa

Después de ejecutar, verifica:

### 1. En SQL Server Management Studio:

```sql
-- Ver nuevas tablas
SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;

-- Ver productos
SELECT * FROM Productos;

-- Ver variantes
SELECT p.nombre, pv.sku, pv.precio, pv.stock_actual
FROM Producto_Variantes pv
INNER JOIN Productos p ON pv.id_producto = p.id_producto;

-- Ver pedidos migrados
SELECT * FROM Pedidos;
SELECT * FROM Pedidos_Items;
```

### 2. En el Backend:

```bash
cd c:\projects\ai-print-studio\database\source
python app_v2.py
```

Abre el navegador en: `http://localhost:8000/api/productos`

Deberías ver JSON con los productos y sus variantes.

### 3. Probar API:

```bash
python test_api_v2.py
```

Debería mostrar "✅ Todos los tests pasaron"

## 📁 Estructura Resultante

Después de la migración tendrás:

```
PrendeteRock (BD)
├── Usuarios (sin cambios)
│
├── PRODUCTOS (NUEVO)
│   ├── Productos (5 productos base)
│   ├── Producto_Atributos (Color, Talle, Material)
│   ├── Producto_Atributo_Valores (~50 valores)
│   ├── Producto_Atributos_Asignados
│   ├── Producto_Variantes (~20 SKUs)
│   └── Variante_Atributos
│
├── PEDIDOS (MEJORADO)
│   ├── Pedidos (encabezado con totales)
│   ├── Pedidos_Items (detalle multi-item)
│   ├── Pedidos_Historial (auditoría)
│   └── Pagos (transacciones)
│
├── ARCHIVOS
│   └── Archivos_Diseno (metadatos de imágenes)
│
└── STOCK
    └── Stock_Movimientos (trazabilidad)
```

## 🔄 Rollback (En caso de problemas)

Si algo sale mal, puedes restaurar el backup:

```sql
USE master;

-- Desconectar usuarios
ALTER DATABASE PrendeteRock SET SINGLE_USER WITH ROLLBACK IMMEDIATE;

-- Restaurar backup
RESTORE DATABASE PrendeteRock 
FROM DISK = 'C:\Backups\PrendeteRock_YYYYMMDD_HHMMSS.bak'
WITH REPLACE;

-- Reconectar usuarios
ALTER DATABASE PrendeteRock SET MULTI_USER;
```

Reemplaza `YYYYMMDD_HHMMSS` con la fecha del backup creado.

## 📞 Soporte

Si encuentras errores durante la migración:

1. **Revisa el log en pantalla** - indica qué paso falló
2. **Busca el error específico** en la sección "Problemas Comunes"
3. **No ejecutes el script múltiples veces** sin antes limpiar
4. **Restaura el backup** si es necesario

## ✅ Siguiente Paso

Una vez completada la migración exitosamente:

1. **Actualizar el backend** para usar los nuevos endpoints
2. **Actualizar el frontend** para consumir la nueva API
3. **Probar el flujo completo** de creación de pedidos
4. **Configurar el panel de administración** con las nuevas métricas

Ver: `README_BACKEND_V2.md` para detalles de la nueva API.

---

**¡Buena suerte con la migración! 🚀**
