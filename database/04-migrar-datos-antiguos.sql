-- ============================================================
-- SCRIPT 4: MIGRACIÓN DE DATOS ANTIGUOS
-- ============================================================
-- Descripción: Migrar usuarios, pedidos y datos de la BD antigua
-- Fecha: 22 de abril de 2026
-- ============================================================

USE PrendeteRock;
GO

PRINT '🔄 INICIANDO MIGRACIÓN DE DATOS ANTIGUOS';
PRINT '';

-- ============================================================
-- PASO 1: MIGRAR USUARIOS
-- ============================================================
PRINT '👥 Migrando usuarios...';

SET IDENTITY_INSERT Usuarios ON;

INSERT INTO Usuarios (
    id_usuario, 
    Nombre, 
    Email, 
    telefono, 
    password_user, 
    Tipo, 
    fecha_registro
)
SELECT 
    id_usuario,
    Nombre,
    Email,
    telefono,
    password_user,
    Tipo,
    fecha_registro
FROM Usuarios_OLD
WHERE id_usuario NOT IN (SELECT id_usuario FROM Usuarios);

SET IDENTITY_INSERT Usuarios OFF;

DECLARE @usuariosMigrados INT = @@ROWCOUNT;
PRINT '✅ ' + CAST(@usuariosMigrados AS VARCHAR) + ' usuarios migrados';

-- ============================================================
-- PASO 2: CREAR DIRECTORIO DE UPLOADS
-- ============================================================
PRINT '📁 Preparando directorio de uploads...';
PRINT '   NOTA: Crear manualmente: C:\projects\ai-print-studio\uploads\';
PRINT '   O ejecutar script Python: migrar-imagenes.py';

-- ============================================================
-- PASO 3: MAPEAR PRODUCTOS ANTIGUOS → VARIANTES NUEVAS
-- ============================================================
PRINT '🗺️  Creando mapeo de productos antiguos → variantes nuevas...';

-- Tabla temporal para mapear id_producto antiguo → id_variante nueva
CREATE TABLE #MapeoProductos (
    id_producto_old INT,
    id_variante_new INT,
    nombre_producto VARCHAR(100),
    sku VARCHAR(50)
);

-- Remera → Mapeamos al SKU más genérico (Negro M por defecto)
INSERT INTO #MapeoProductos 
SELECT DISTINCT
    p.id_producto,
    (SELECT TOP 1 id_variante FROM Producto_Variantes WHERE sku = 'REM-NEG-M'),
    'Remera Básica',
    'REM-NEG-M'
FROM Productos_OLD p
WHERE p.Detalle LIKE '%Remera%' OR p.Detalle LIKE '%Camiseta%';

-- Taza → TAZ-BLA
INSERT INTO #MapeoProductos 
SELECT DISTINCT
    p.id_producto,
    (SELECT TOP 1 id_variante FROM Producto_Variantes WHERE sku = 'TAZ-BLA'),
    'Taza Personalizada',
    'TAZ-BLA'
FROM Productos_OLD p
WHERE p.Detalle LIKE '%Taza%'
AND p.id_producto NOT IN (SELECT id_producto_old FROM #MapeoProductos);

-- Buzo → BUZ-NEG-L
INSERT INTO #MapeoProductos 
SELECT DISTINCT
    p.id_producto,
    (SELECT TOP 1 id_variante FROM Producto_Variantes WHERE sku = 'BUZ-NEG-L'),
    'Buzo con Capucha',
    'BUZ-NEG-L'
FROM Productos_OLD p
WHERE (p.Detalle LIKE '%Buzo%' OR p.Detalle LIKE '%Sudadera%')
AND p.id_producto NOT IN (SELECT id_producto_old FROM #MapeoProductos);

-- Gorra → GOR-NEG
INSERT INTO #MapeoProductos 
SELECT DISTINCT
    p.id_producto,
    (SELECT TOP 1 id_variante FROM Producto_Variantes WHERE sku = 'GOR-NEG'),
    'Gorra Trucker',
    'GOR-NEG'
FROM Productos_OLD p
WHERE p.Detalle LIKE '%Gorra%'
AND p.id_producto NOT IN (SELECT id_producto_old FROM #MapeoProductos);

-- Productos no mapeados → Default a Remera
INSERT INTO #MapeoProductos 
SELECT DISTINCT
    p.id_producto,
    (SELECT TOP 1 id_variante FROM Producto_Variantes WHERE sku = 'REM-NEG-M'),
    'Remera Básica',
    'REM-NEG-M'
FROM Productos_OLD p
WHERE p.id_producto NOT IN (SELECT id_producto_old FROM #MapeoProductos);

PRINT '✅ Mapeo de productos creado';
SELECT * FROM #MapeoProductos;

-- ============================================================
-- PASO 4: MIGRAR PEDIDOS (Header)
-- ============================================================
PRINT '🛒 Migrando pedidos...';

SET IDENTITY_INSERT Pedidos ON;

INSERT INTO Pedidos (
    id_pedido,
    numero_orden,
    id_usuario,
    total,
    estado,
    estado_pago,
    fecha_pedido
)
SELECT 
    p.id_pedido,
    'ORD-' + CONVERT(VARCHAR, YEAR(p.fecha_pedido)) + '-' + RIGHT('00000' + CONVERT(VARCHAR, p.id_pedido), 5),
    p.id_usuario,
    ISNULL((SELECT SUM(pd.total) FROM Pedidos_detalle_OLD pd WHERE pd.id_pedido = p.id_pedido), 0),
    CASE 
        WHEN p.estado = 'completado' THEN 'completado'
        WHEN p.estado = 'cancelado' THEN 'cancelado'
        ELSE 'pendiente'
    END,
    -- Inferir estado de pago desde Pedidos_detalle
    CASE 
        WHEN EXISTS (SELECT 1 FROM Pedidos_detalle_OLD pd WHERE pd.id_pedido = p.id_pedido AND pd.pago = 'aprobado') 
            THEN 'aprobado'
        WHEN EXISTS (SELECT 1 FROM Pedidos_detalle_OLD pd WHERE pd.id_pedido = p.id_pedido AND pd.pago = 'rechazado') 
            THEN 'rechazado'
        ELSE 'pendiente'
    END,
    p.fecha_pedido
FROM Pedidos_OLD p
WHERE p.id_pedido NOT IN (SELECT id_pedido FROM Pedidos);

SET IDENTITY_INSERT Pedidos OFF;

DECLARE @pedidosMigrados INT = @@ROWCOUNT;
PRINT '✅ ' + CAST(@pedidosMigrados AS VARCHAR) + ' pedidos migrados';

-- ============================================================
-- PASO 5: MIGRAR ITEMS DE PEDIDOS (sin imágenes aún)
-- ============================================================
PRINT '📦 Migrando items de pedidos...';

INSERT INTO Pedidos_Items (
    id_pedido,
    id_variante,
    cantidad,
    precio_unitario,
    tiene_diseno,
    estado
)
SELECT 
    pd.id_pedido,
    ISNULL(m.id_variante_new, (SELECT TOP 1 id_variante FROM Producto_Variantes WHERE sku = 'REM-NEG-M')),
    1, -- Cantidad default
    ISNULL(pd.total, 12000), -- Precio del item
    CASE WHEN pd.imagen IS NOT NULL AND LEN(pd.imagen) > 0 THEN 1 ELSE 0 END,
    CASE 
        WHEN pd.estado = 'completado' THEN 'completado'
        WHEN pd.estado = 'entregado' THEN 'completado'
        ELSE 'pendiente'
    END
FROM Pedidos_detalle_OLD pd
LEFT JOIN #MapeoProductos m ON pd.id_producto = m.id_producto_old
WHERE pd.id_pedido IN (SELECT id_pedido FROM Pedidos);

DECLARE @itemsMigrados INT = @@ROWCOUNT;
PRINT '✅ ' + CAST(@itemsMigrados AS VARCHAR) + ' items migrados (imágenes pendientes)';

-- ============================================================
-- PASO 6: MIGRAR PAGOS (crear registros en tabla Pagos)
-- ============================================================
PRINT '💳 Creando registros de pagos...';

INSERT INTO Pagos (
    id_pedido,
    metodo_pago,
    monto,
    estado,
    fecha_transaccion,
    fecha_aprobacion
)
SELECT 
    ped.id_pedido,
    'mercadopago', -- Método por defecto
    ped.total,
    ped.estado_pago,
    ped.fecha_pedido,
    CASE WHEN ped.estado_pago = 'aprobado' THEN ped.fecha_pedido ELSE NULL END
FROM Pedidos ped
WHERE ped.estado_pago IN ('aprobado', 'rechazado')
AND NOT EXISTS (SELECT 1 FROM Pagos WHERE id_pedido = ped.id_pedido);

DECLARE @pagosMigrados INT = @@ROWCOUNT;
PRINT '✅ ' + CAST(@pagosMigrados AS VARCHAR) + ' registros de pago creados';

-- ============================================================
-- PASO 7: ESTADÍSTICAS DE MIGRACIÓN
-- ============================================================
PRINT '';
PRINT '📊 RESUMEN DE MIGRACIÓN:';
PRINT '   👥 Usuarios: ' + CAST(@usuariosMigrados AS VARCHAR);
PRINT '   🛒 Pedidos: ' + CAST(@pedidosMigrados AS VARCHAR);
PRINT '   📦 Items: ' + CAST(@itemsMigrados AS VARCHAR);
PRINT '   💳 Pagos: ' + CAST(@pagosMigrados AS VARCHAR);
PRINT '';
PRINT '⚠️  PENDIENTE: Migrar imágenes de Base64 a filesystem';
PRINT '   Ejecutar script Python: python database/migrar-imagenes.py';
PRINT '';
PRINT '🎯 SIGUIENTE PASO: Verificar datos migrados';

-- Limpieza
DROP TABLE #MapeoProductos;

GO

-- ============================================================
-- CONSULTAS DE VERIFICACIÓN
-- ============================================================
PRINT '';
PRINT '🔍 VERIFICACIÓN DE DATOS MIGRADOS:';
PRINT '';

-- Usuarios
PRINT '👥 USUARIOS:';
SELECT Tipo, COUNT(*) AS Cantidad
FROM Usuarios
GROUP BY Tipo;

-- Productos y variantes
PRINT '';
PRINT '📦 PRODUCTOS Y VARIANTES:';
SELECT 
    p.nombre AS Producto,
    COUNT(pv.id_variante) AS Variantes,
    SUM(pv.stock_actual) AS Stock_Total
FROM Productos p
LEFT JOIN Producto_Variantes pv ON p.id_producto = pv.id_producto
GROUP BY p.nombre;

-- Pedidos por estado
PRINT '';
PRINT '🛒 PEDIDOS POR ESTADO:';
SELECT estado, COUNT(*) AS Cantidad, SUM(total) AS Total
FROM Pedidos
GROUP BY estado;

-- Pedidos por estado de pago
PRINT '';
PRINT '💳 PEDIDOS POR ESTADO DE PAGO:';
SELECT estado_pago, COUNT(*) AS Cantidad, SUM(total) AS Total
FROM Pedidos
GROUP BY estado_pago;

GO
