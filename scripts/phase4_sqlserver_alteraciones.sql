-- ================================================================
-- Phase 4 — Alteraciones SQL Server
-- AI Print Studio / Prendete Rock
--
-- Ejecutar sobre la base de datos PrendeteRock UNA SOLA VEZ.
-- Compatible con SQL Server 2016+
-- ================================================================

USE PrendeteRock;
GO

PRINT '=================================================';
PRINT ' PHASE 4 — ALTERACIONES SQL SERVER';
PRINT '=================================================';


-- ================================================================
-- 1. Agregar columna imagen_ruta a Pedidos_detalle
--    Reemplaza el almacenamiento Base64 en la columna imagen
--    por una ruta relativa al archivo en disco.
-- ================================================================

IF NOT EXISTS (
    SELECT 1
    FROM   sys.columns
    WHERE  object_id = OBJECT_ID('Pedidos_detalle')
      AND  name      = 'imagen_ruta'
)
BEGIN
    ALTER TABLE Pedidos_detalle
        ADD imagen_ruta VARCHAR(500) NULL;

    PRINT '✔ Columna imagen_ruta agregada a Pedidos_detalle';
END
ELSE
    PRINT '→ Columna imagen_ruta ya existe (sin cambios)';
GO


-- ================================================================
-- 2. Columna cuenta_bloqueada en Usuarios
--    Necesaria para el endpoint de edición de clientes.
-- ================================================================

IF NOT EXISTS (
    SELECT 1
    FROM   sys.columns
    WHERE  object_id = OBJECT_ID('Usuarios')
      AND  name      = 'cuenta_bloqueada'
)
BEGIN
    ALTER TABLE Usuarios
        ADD cuenta_bloqueada BIT NOT NULL DEFAULT 0;

    PRINT '✔ Columna cuenta_bloqueada agregada a Usuarios';
END
ELSE
    PRINT '→ Columna cuenta_bloqueada ya existe (sin cambios)';
GO


-- ================================================================
-- 3. ÍNDICE COMPUESTO: Pedidos(id_usuario, fecha_pedido DESC)
--    Acelera la consulta /api/mis-pedidos/{id_usuario},
--    que filtra por usuario y ordena por fecha descendente.
-- ================================================================

IF NOT EXISTS (
    SELECT 1
    FROM   sys.indexes
    WHERE  object_id = OBJECT_ID('Pedidos')
      AND  name      = 'IX_Pedidos_Usuario_Fecha'
)
BEGIN
    CREATE NONCLUSTERED INDEX IX_Pedidos_Usuario_Fecha
        ON Pedidos (id_usuario ASC, fecha_pedido DESC);

    PRINT '✔ Índice IX_Pedidos_Usuario_Fecha creado en Pedidos';
END
ELSE
    PRINT '→ Índice IX_Pedidos_Usuario_Fecha ya existe (sin cambios)';
GO


-- ================================================================
-- 4. ÍNDICE COMPUESTO: Pedidos(estado, estado_pago, fecha_pedido)
--    Acelera los filtros del panel de admin (/admin/pedidos?filtro=...)
-- ================================================================

IF NOT EXISTS (
    SELECT 1
    FROM   sys.indexes
    WHERE  object_id = OBJECT_ID('Pedidos')
      AND  name      = 'IX_Pedidos_Estado_Pago_Fecha'
)
BEGIN
    CREATE NONCLUSTERED INDEX IX_Pedidos_Estado_Pago_Fecha
        ON Pedidos (estado ASC, estado_pago ASC, fecha_pedido DESC);

    PRINT '✔ Índice IX_Pedidos_Estado_Pago_Fecha creado en Pedidos';
END
ELSE
    PRINT '→ Índice IX_Pedidos_Estado_Pago_Fecha ya existe (sin cambios)';
GO


-- ================================================================
-- 5. Verificación final
-- ================================================================

PRINT '';
PRINT 'Columnas de Pedidos_detalle:';
SELECT name, max_length, is_nullable
FROM   sys.columns
WHERE  object_id = OBJECT_ID('Pedidos_detalle')
ORDER  BY column_id;

PRINT '';
PRINT 'Índices en Pedidos:';
SELECT i.name, i.type_desc
FROM   sys.indexes i
WHERE  i.object_id = OBJECT_ID('Pedidos')
  AND  i.name IS NOT NULL;

PRINT '';
PRINT '✅ Phase 4 — SQL Server: alteraciones aplicadas correctamente';
GO
