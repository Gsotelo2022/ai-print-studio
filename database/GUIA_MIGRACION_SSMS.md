# 🎯 MIGRACIÓN MANUAL PASO A PASO (RECOMENDADO)

## ✅ Estado Actual de tu Base de Datos

```
PrendeteRock (localhost\SQLEXPRESS01) 
├── Usuarios (2 registros)
├── Productos (86 registros)  
├── Pedidos (13 registros)
└── Pedidos_detalle (13 registros)
```

## 🚀 EJECUTAR MIGRACIÓN EN SSMS (Paso a Paso)

### Paso 1: Abrir SQL Server Management Studio (SSMS)

1. Abre **SQL Server Management Studio**
2. Conéctate al servidor: `localhost\SQLEXPRESS01`
3. Expande "Databases" y verifica que **PrendeteRock** aparezca

### Paso 2: Ejecutar Backup (OBLIGATORIO)

1. En SSMS, abre un **New Query**
2. Abre el archivo: `c:\projects\ai-print-studio\database\01-backup-bd-actual.sql`
3. Copia TODO el contenido
4. Pégalo en la ventana de Query
5. **Presiona F5 o haz clic en "Execute"**

✅ Verás mensaje: "Backup completado exitosamente"
📁 Location: `C:\Backups\PrendeteRock_YYYYMMDD_HHMMSS.bak`

⚠️ **Si da error "Cannot open backup device":**
- Crea la carpeta `C:\Backups` manualmente
- Ejecuta SSMS como "Administrador"

---

### Paso 3: Crear Nueva Estructura

1. En SSMS, abre **otra** New Query  
2. Abre el archivo: `c:\projects\ai-print-studio\database\02-nueva-estructura-bd.sql`
3. Copia TODO el contenido
4. Pég alo en la ventana de Query
5. **Presiona F5 o haz clic en "Execute"**

⏱️ Tiempo: 1-2 minutos

✅ Resultado:
- Tablas antiguas renombradas a `*_OLD`
- 12 tablas nuevas creadas:
  - Productos
  - Producto_Atributos
  - Producto_Atributo_Valores
  - Producto_Atributos_Asignados
  - Producto_Variantes
  - Variante_Atributos
  - Pedidos
  - Pedidos_Items
  - Pagos
  - Archivos_Diseno
  - Pedidos_Historial
  - Stock_Movimientos

---

### Paso 4: Insertar Datos Iniciales

1. En SSMS, abre **otra** New Query
2. Abre el archivo: `c:\projects\ai-print-studio\database\03-datos-iniciales.sql`
3. Copia TODO el contenido
4. Pégalo en la ventana de Query
5. **Presiona F5 o haz clic en "Execute"**

⏱️ Tiempo: 30 segundos

✅ Resultado:
- 5 productos base creados (Remera, Taza, Buzo, Gorra, Bolsa)
- 3 atributos creados (Color, Talle, Material)
- ~20 variantes creadas con precios
- ~50 valores de atributos

---

### Paso 5: Migrar Datos Antiguos

1. En SSMS, abre **otra** New Query
2. Abre el archivo: `c:\projects\ai-print-studio\database\04-migrar-datos-antiguos.sql`
3. Copia TODO el contenido
4. Pégalo en la ventana de Query
5. **Presiona F5 o haz clic en "Execute"**

⏱️ Tiempo: 1-3 minutos (depende de tus datos)

✅ Resultado:
- 2 usuarios migrados a nueva estructura (sin cambios, compatible)
- 86 productos antiguos mapeados a variantes nuevas
- 13 pedidos migrados a estructura Pedidos + Pedidos_Items

---

### Paso 6: Verificar Migración

Ejecuta estas queries en SSMS para verificar:

```sql
-- Ver nuevas tablas
SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;

-- Ver productos migrados
SELECT * FROM Productos;

-- Ver variantes creadas
SELECT 
    p.nombre AS producto,
    pv.sku,
    pv.precio,
    pv.stock_actual
FROM Producto_Variantes pv
INNER JOIN Productos p ON pv.id_producto = p.id_producto;

-- Ver pedidos migrados
SELECT 
    ped.numero_orden,
    ped.total,
    ped.estado,
    u.Nombre AS cliente
FROM Pedidos ped
INNER JOIN Usuarios u ON ped.id_usuario = u.id_usuario;

-- Ver items de pedidos
SELECT *
FROM Pedidos_Items;

-- Verificar que usuarios se mantienen
SELECT * FROM Usuarios;
```

---

## 🔄 SI ALGO SALE MAL (Rollback)

Si algo no funciona correctamente:

```sql
USE master;

-- Desconectar todos los usuarios
ALTER DATABASE PrendeteRock SET SINGLE_USER WITH ROLLBACK IMMEDIATE;

-- Restaurar backup (ajusta la fecha/hora del backup)
RESTORE DATABASE PrendeteRock 
FROM DISK = 'C:\Backups\PrendeteRock_20260422_180556.bak'
WITH REPLACE;

-- Reconectar usuarios
ALTER DATABASE PrendeteRock SET MULTI_USER;
```

---

## ✅ DESPUÉS DE LA MIGRACIÓN

### 1. Probar la Conexión desde Python

```bash
cd c:\projects\ai-print-studio\database
python ver-tablas.py
```

Deberías ver ~15 tablas ahora.

### 2. Iniciar el Backend V2

```bash
cd c:\projects\ai-print-studio\database\source
python app_v2.py
```

### 3. Probar la API

Abre el navegador:
```
http://localhost:8000/api/productos
```

Deberías ver JSON con los productos y sus variantes.

---

## 📊 ESTRUCTURA RESULTANTE

Después de ejecutar los 4 scripts tendrás:

```
PrendeteRock
│
├── Usuarios (2 registros - migrados)
│
├── PRODUCTOS (NUEVO)
│   ├── Productos (5 nuevos+ adaptación de 86 antiguos)
│   ├── Producto_Atributos (3: Color, Talle, Material)
│   ├── Producto_Atributo_Valores (~50 valores)
│   ├── Producto_Atributos_Asignados
│   ├── Producto_Variantes (~40-50 SKUs)
│   └── Variante_Atributos
│
├── PEDIDOS (MEJORADO)
│   ├── Pedidos (13 migrados)
│   ├── Pedidos_Items (13 ítems)
│   ├── Pedidos_Historial (auditoría)
│   └── Pagos
│
├── ARCHIVOS
│   └── Archivos_Diseno (para diseños)
│
├── STOCK
│   └── Stock_Movimientos (trazabilidad)
│
└── TABLAS ANTIGUAS (respaldo)
    ├── Usuarios_OLD
    ├── Productos_OLD (86 registros)
    ├── Pedidos_OLD (13 registros)
    └── Pedidos_detalle_OLD (13 registros)
```

---

## ⚡ OPCIÓN RÁPIDA: Script .bat

Si prefieres, puedes ejecutar los scripts desde la terminal:

```batch
-- IMPORTANTE: Ejecuta estos comandos UNO POR UNO en SSMS
--            No los ejecutes todos juntos

-- 1. Backup
sqlcmd -S localhost\SQLEXPRESS01 -d PrendeteRock -i "01-backup-bd-actual.sql"

-- 2. Nueva estructura
sqlcmd -S localhost\SQLEXPRESS01 -d PrendeteRock -i "02-nueva-estructura-bd.sql"

-- 3. Datos iniciales
sqlcmd -S localhost\SQLEXPRESS01 -d PrendeteRock -i "03-datos-iniciales.sql"

-- 4. Migrar datos
sqlcmd -S localhost\SQLEXPRESS01 -d PrendeteRock -i "04-migrar-datos-antiguos.sql"
```

Pero **RECOMIENDO SSMS** porque verás los mensajes de error claramente.

---

## 📞 ¿Necesitas Ayuda?

### Error Común 1: "Cannot open backup device"
**Solución:** Crea la carpeta `C:\Backups` y dale permisos completos

### Error Común 2: "There is already an object named"
**Solución:** Las tablas ya existen. Puedes:
- Eliminarlas manualmente en SSMS
- O modificar el script para usar `DROP TABLE IF EXISTS`

### Error Común 3: "Cannot rename table because it is referenced by a constraint"
**Solución:** Las tablas antiguas tienen foreign keys. El script las elimina primero.

---

**¡Listo! Una vez ejecutados los 4 scripts, tu base de datos estará actualizada! 🚀**

La migración preserva TODOS tus datos existentes:
✅ 2 usuarios
✅ 86 productos (convertidos a variantes)
✅ 13 pedidos (migrados a nueva estructura)
