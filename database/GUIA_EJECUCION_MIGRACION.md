# 🚀 GUÍA DE EJECUCIÓN - MIGRACIÓN DE BASE DE DATOS

> **Proyecto:** AI Print Studio - Prendete Rock  
> **Fecha:** 22 de abril de 2026  
> **Objetivo:** Migrar de estructura simple a sistema profesional con variantes

---

## ⚠️ IMPORTANTE - LEER ANTES DE COMENZAR

### Requisitos Previos

- ✅ SQL Server Management Studio (SSMS) instalado
- ✅ Python 3.9+ instalado
- ✅ Acceso a la base de datos `PrendeteRock`
- ✅ Backup manual adicional (recomendado)
- ✅ Tiempo estimado: 1-2 horas

### Respaldo de Seguridad

**CRÍTICO:** Antes de ejecutar cualquier script, crear backup manual:

```sql
-- En SSMS, clic derecho en PrendeteRock → Tareas → Hacer copia de seguridad
-- O ejecutar:
BACKUP DATABASE PrendeteRock 
TO DISK = 'C:\SQLBackups\PrendeteRock_Manual_Antes_Migracion.bak';
```

---

## 📋 ORDEN DE EJECUCIÓN

### Paso 1: Backup Automático de Base de Datos

**Archivo:** `01-backup-bd-actual.sql`

**Descripción:** Crea un backup completo con timestamp

**Ejecución:**
```sql
-- Abrir SSMS
-- Conectar a tu servidor SQL
-- Abrir archivo: database/01-backup-bd-actual.sql
-- IMPORTANTE: Verificar la ruta de backup en línea 14
-- Por defecto: C:\SQLBackups\
-- Ajustar si es necesario
-- Ejecutar (F5)
```

**Resultado esperado:**
```
✅ BACKUP COMPLETADO EXITOSAMENTE
📁 Ubicación: C:\SQLBackups\PrendeteRock_PreMigracion_20260422_153045.bak
💾 Tamaño: XX MB
✅ VERIFICACIÓN DE BACKUP: OK
```

**⚠️ SI FALLA:**
- Crear directorio `C:\SQLBackups\` manualmente
- O cambiar la ruta en el script a una ubicación con permisos de escritura

---

### Paso 2: Crear Nueva Estructura de Base de Datos

**Archivo:** `02-nueva-estructura-bd.sql`

**Descripción:** Renombra tablas antiguas y crea nueva estructura optimizada

**Ejecución:**
```sql
-- En SSMS, abrir: database/02-nueva-estructura-bd.sql
-- Ejecutar (F5)
```

**Resultado esperado:**
```
🚀 INICIANDO CREACIÓN DE NUEVA ESTRUCTURA
📦 Renombrando tablas antiguas...
✅ Tablas antiguas respaldadas
👥 Creando tabla Usuarios...
✅ Tabla Usuarios creada
📦 Creando sistema de productos...
✅ Sistema de productos creado
🖼️  Creando tabla de archivos...
✅ Tabla Archivos_Diseno creada
🛒 Creando sistema de pedidos...
✅ Sistema de pedidos creado
💳 Creando tabla de pagos...
✅ Tabla Pagos creada
📊 Creando tablas de auditoría...
✅ Tablas de auditoría creadas
⚡ Creando triggers...
✅ Triggers creados
🎉 ¡NUEVA ESTRUCTURA CREADA EXITOSAMENTE!
```

**Resultado:**
- Tablas antiguas ahora se llaman: `Usuarios_OLD`, `Pedidos_OLD`, `Pedidos_detalle_OLD`, `Productos_OLD`
- Nuevas tablas creadas con estructura optimizada

---

### Paso 3: Cargar Datos Iniciales (Productos Base)

**Archivo:** `03-datos-iniciales.sql`

**Descripción:** Carga atributos, productos base y variantes

**Ejecución:**
```sql
-- En SSMS, abrir: database/03-datos-iniciales.sql
-- Ejecutar (F5)
```

**Resultado esperado:**
```
🚀 CARGANDO DATOS INICIALES
🎨 Creando atributos...
✅ Atributos creados: Color, Talle, Material
📦 Creando productos base...
✅ Productos base creados: Remera, Taza, Buzo, Gorra, Bolsa
🎯 Creando variantes...
✅ Variantes creadas: 19 SKUs activos

📊 RESUMEN DE DATOS INICIALES:
   ✅ 3 Atributos (Color, Talle, Material)
   ✅ 17 Valores de atributos
   ✅ 5 Productos base
   ✅ 19 Variantes (SKUs)
```

**Resultado:**
- Catálogo de productos configurado
- 19 variantes listas para usar (Remera Negro M, Remera Blanco L, etc.)

---

### Paso 4: Migrar Datos Antiguos

**Archivo:** `04-migrar-datos-antiguos.sql`

**Descripción:** Migra usuarios, pedidos y items de la BD antigua a la nueva

**Ejecución:**
```sql
-- En SSMS, abrir: database/04-migrar-datos-antiguos.sql
-- Ejecutar (F5)
```

**Resultado esperado:**
```
🔄 INICIANDO MIGRACIÓN DE DATOS ANTIGUOS
👥 Migrando usuarios...
✅ X usuarios migrados
🗺️  Creando mapeo de productos antiguos → variantes nuevas...
✅ Mapeo de productos creado
🛒 Migrando pedidos...
✅ X pedidos migrados
📦 Migrando items de pedidos...
✅ X items migrados (imágenes pendientes)
💳 Creando registros de pagos...
✅ X registros de pago creados

📊 RESUMEN DE MIGRACIÓN:
   👥 Usuarios: X
   🛒 Pedidos: X
   📦 Items: X
   💳 Pagos: X
```

**Verificación:**
```sql
-- Consultar usuarios migrados
SELECT Tipo, COUNT(*) FROM Usuarios GROUP BY Tipo;

-- Consultar pedidos migrados
SELECT estado, COUNT(*), SUM(total) FROM Pedidos GROUP BY estado;
```

---

### Paso 5: Migrar Imágenes de Base64 a Archivos

**Archivo:** `migrar-imagenes.py`

**Descripción:** Extrae imágenes base64 de la BD antigua y las guarda como archivos

**Requisitos:**
```bash
# Instalar dependencias (si no están)
pip install pyodbc pillow
```

**Ejecución:**
```powershell
# Desde raíz del proyecto
cd C:\projects\ai-print-studio
python database\migrar-imagenes.py
```

**Resultado esperado:**
```
🚀 MIGRACIÓN DE IMÁGENES BASE64 → FILESYSTEM
============================================================
📁 Directorio de destino: C:\projects\ai-print-studio\uploads\designs
📁 Directorio de miniaturas: C:\projects\ai-print-studio\uploads\thumbnails

✅ Conectado a base de datos
🔍 Buscando imágenes en Pedidos_detalle_OLD...
📊 Encontradas X imágenes para migrar

[1/X] Procesando detalle #1... ✅ OK (id_archivo: 1, 245678 bytes)
[2/X] Procesando detalle #2... ✅ OK (id_archivo: 2, 198234 bytes)
...

📊 RESUMEN DE MIGRACIÓN:
   ✅ Migradas exitosamente: X
   ❌ Errores: 0
   📁 Total archivos: X
   💾 Ubicación: C:\projects\ai-print-studio\uploads\designs

💡 ESPACIO LIBERADO DE BASE DE DATOS:
   📉 Base64 en BD: ~XX MB
   📁 Archivos en disco: ~XX MB
   💰 Ahorro: ~XX MB
```

---

## ✅ VERIFICACIÓN POST-MIGRACIÓN

### 1. Verificar Estructura de Tablas

```sql
-- Verificar que existen las nuevas tablas
SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;

-- Debería mostrar:
-- Archivos_Diseno
-- Pagos
-- Pedidos
-- Pedidos_Historial
-- Pedidos_Items
-- Producto_Atributo_Valores
-- Producto_Atributos
-- Producto_Atributos_Asignados
-- Producto_Variantes
-- Productos
-- Stock_Movimientos
-- Usuarios
-- Variante_Atributos
-- ... y las tablas _OLD
```

### 2. Verificar Datos Migrados

```sql
-- Usuarios
SELECT 'Usuarios' AS Tabla, COUNT(*) AS Registros FROM Usuarios
UNION ALL
SELECT 'Productos', COUNT(*) FROM Productos
UNION ALL
SELECT 'Producto_Variantes', COUNT(*) FROM Producto_Variantes
UNION ALL
SELECT 'Pedidos', COUNT(*) FROM Pedidos
UNION ALL
SELECT 'Pedidos_Items', COUNT(*) FROM Pedidos_Items
UNION ALL
SELECT 'Archivos_Diseno', COUNT(*) FROM Archivos_Diseno
UNION ALL
SELECT 'Pagos', COUNT(*) FROM Pagos;
```

### 3. Verificar Archivos de Imágenes

```powershell
# En PowerShell
cd C:\projects\ai-print-studio\uploads
dir -Recurse | Measure-Object -Property Length -Sum

# Debería mostrar:
# Count: X archivos
# Sum: XXXXX bytes
```

### 4. Consulta de Prueba Completa

```sql
-- Pedido completo con todos sus detalles
SELECT 
    p.numero_orden,
    u.Nombre AS Cliente,
    p.fecha_pedido,
    p.estado,
    p.estado_pago,
    p.total,
    prod.nombre AS Producto,
    pv.sku AS Variante,
    pi.cantidad,
    pi.precio_unitario,
    CASE WHEN pi.archivo_diseno IS NOT NULL THEN 'Sí' ELSE 'No' END AS ConDiseño
FROM Pedidos p
INNER JOIN Usuarios u ON p.id_usuario = u.id_usuario
INNER JOIN Pedidos_Items pi ON p.id_pedido = pi.id_pedido
INNER JOIN Producto_Variantes pv ON pi.id_variante = pv.id_variante
INNER JOIN Productos prod ON pv.id_producto = prod.id_producto
ORDER BY p.fecha_pedido DESC;
```

---

## 🔧 SIGUIENTE PASO: ACTUALIZAR BACKEND

Una vez verificada la migración, el siguiente paso es actualizar el backend FastAPI para usar la nueva estructura.

**Archivos a modificar:**
- `database/source/app.py` - Endpoints actualizados
- `database/source/db.py` - Ya compatible

**Plan:**
1. Crear nuevos endpoints para productos con variantes
2. Actualizar endpoint de crear pedido
3. Actualizar endpoints de admin
4. Agregar endpoint de upload de imágenes

---

## ⚠️ TROUBLESHOOTING

### Error: "Cannot drop table because it is being referenced"

**Solución:**
```sql
-- El script maneja esto automáticamente, pero si falla:
-- Ejecutar uno por uno:
ALTER TABLE Pedidos_detalle_OLD DROP CONSTRAINT FK_Detalle_Pedidos;
ALTER TABLE Pedidos_detalle_OLD DROP CONSTRAINT FK_Detalle_Productos;
ALTER TABLE Pedidos_OLD DROP CONSTRAINT FK_Pedidos_Usuarios;

-- Luego renombrar:
EXEC sp_rename 'Pedidos_detalle', 'Pedidos_detalle_OLD';
EXEC sp_rename 'Pedidos', 'Pedidos_OLD';
EXEC sp_rename 'Productos', 'Productos_OLD';
EXEC sp_rename 'Usuarios', 'Usuarios_OLD';
```

### Error: "Access denied" al crear backup

**Solución:**
```sql
-- Cambiar ruta a tu directorio de usuario
DECLARE @BackupPath VARCHAR(500) = 'C:\Users\TuUsuario\Backups\';
-- Crear el directorio primero en Windows
```

### Error Python: "No module named 'PIL'"

**Solución:**
```bash
pip install --upgrade pillow
```

### Error Python: "Connection error"

**Solución:**
- Verificar que SQL Server acepta conexiones TCP/IP
- Verificar credenciales en `database/source/db.py`
- Ejecutar SQL Server Configuration Manager → Enable TCP/IP

---

## 📞 SOPORTE

Si encuentras problemas durante la migración:

1. **No ejecutar más scripts** - Detener el proceso
2. **Revisar mensajes de error** - Copiar el mensaje completo
3. **Restaurar backup** si es necesario:
   ```sql
   USE master;
   ALTER DATABASE PrendeteRock SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
   RESTORE DATABASE PrendeteRock FROM DISK = 'C:\SQLBackups\PrendeteRock_PreMigracion_XXXXXX.bak';
   ALTER DATABASE PrendeteRock SET MULTI_USER;
   ```

---

## ✅ CHECKLIST FINAL

Antes de considerar la migración completa:

- [ ] Backup creado y verificado
- [ ] Nueva estructura creada sin errores
- [ ] Datos iniciales cargados (19 variantes)
- [ ] Usuarios migrados correctamente
- [ ] Pedidos migrados correctamente
- [ ] Imágenes extraídas y guardadas como archivos
- [ ] Archivos_Diseno tiene registros
- [ ] Consultas de verificación ejecutadas
- [ ] Backend actualizado (siguiente fase)
- [ ] Frontend actualizado (siguiente fase)
- [ ] Testing completo (siguiente fase)

---

**¡Buena suerte con la migración! 🚀**
