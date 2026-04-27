-- ============================================================
-- POBLAR BASE DE DATOS CON DATOS INICIALES
-- ============================================================
USE PrendeteRock;
GO

PRINT 'Insertando datos iniciales...';
PRINT '';

-- ============================================================
-- USUARIOS
-- ============================================================
PRINT 'Creando usuarios...';

INSERT INTO Usuarios (Nombre, Email, telefono, password_user, Tipo) VALUES
('Administrador', 'admin@prendeterock.com', '1234567890', '$2b$10$abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRST', 'admin'),
('Cliente Demo', 'cliente@demo.com', '0987654321', '$2b$10$abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRST', 'cliente');

PRINT '✓ 2 usuarios creados';

-- ============================================================
-- ATRIBUTOS
-- ============================================================
PRINT 'Creando atributos...';

INSERT INTO Producto_Atributos (nombre, tipo, orden) VALUES
('Color', 'select', 1),
('Talle', 'select', 2),
('Material', 'select', 3);

DECLARE @idColor INT = (SELECT id_atributo FROM Producto_Atributos WHERE nombre = 'Color');
DECLARE @idTalle INT = (SELECT id_atributo FROM Producto_Atributos WHERE nombre = 'Talle');
DECLARE @idMaterial INT = (SELECT id_atributo FROM Producto_Atributos WHERE nombre = 'Material');

-- Colores
INSERT INTO Producto_Atributo_Valores (id_atributo, valor, codigo_color, orden) VALUES
(@idColor, 'Negro', '#000000', 1),
(@idColor, 'Blanco', '#FFFFFF', 2),
(@idColor, 'Rojo', '#FF0000', 3),
(@idColor, 'Azul', '#0000FF', 4),
(@idColor, 'Verde', '#00FF00', 5),
(@idColor, 'Amarillo', '#FFFF00', 6),
(@idColor, 'Naranja', '#FFA500', 7),
(@idColor, 'Rosa', '#FFC0CB', 8),
(@idColor, 'Gris', '#808080', 9),
(@idColor, 'Violeta', '#8B00FF', 10);

-- Talles
INSERT INTO Producto_Atributo_Valores (id_atributo, valor, orden) VALUES
(@idTalle, 'XS', 1),
(@idTalle, 'S', 2),
(@idTalle, 'M', 3),
(@idTalle, 'L', 4),
(@idTalle, 'XL', 5),
(@idTalle, 'XXL', 6);

-- Materiales
INSERT INTO Producto_Atributo_Valores (id_atributo, valor, orden) VALUES
(@idMaterial, 'Algodón 100%', 1),
(@idMaterial, 'Poliéster', 2),
(@idMaterial, 'Mezcla', 3);

PRINT '✓ Atributos y valores creados';

-- ============================================================
-- PRODUCTOS
-- ============================================================
PRINT 'Creando productos...';

INSERT INTO Productos (nombre, descripcion, categoria, activo, orden_visualizacion) VALUES
('Remera', 'Remera de algodón personalizable con tu diseño', 'Indumentaria', 1, 1),
('Taza', 'Taza de cerámica 350ml personalizable', 'Hogar', 1, 2),
('Buzo', 'Buzo con capucha personalizable', 'Indumentaria', 1, 3),
('Gorra', 'Gorra ajustable personalizable', 'Accesorios', 1, 4),
('Bolsa', 'Bolsa de tela ecológica personalizable', 'Accesorios', 1, 5);

DECLARE @idRemera INT = (SELECT id_producto FROM Productos WHERE nombre = 'Remera');
DECLARE @idTaza INT = (SELECT id_producto FROM Productos WHERE nombre = 'Taza');
DECLARE @idBuzo INT = (SELECT id_producto FROM Productos WHERE nombre = 'Buzo');
DECLARE @idGorra INT = (SELECT id_producto FROM Productos WHERE nombre = 'Gorra');
DECLARE @idBolsa INT = (SELECT id_producto FROM Productos WHERE nombre = 'Bolsa');

PRINT '✓ 5 productos base creados';

-- ============================================================
-- ASIGNAR ATRIBUTOS A PRODUCTOS
-- ============================================================
PRINT 'Asignando atributos a productos...';

-- Remera: Color + Talle
INSERT INTO Producto_Atributos_Asignados (id_producto, id_atributo, requerido) VALUES
(@idRemera, @idColor, 1),
(@idRemera, @idTalle, 1);

-- Buzo: Color + Talle
INSERT INTO Producto_Atributos_Asignados (id_producto, id_atributo, requerido) VALUES
(@idBuzo, @idColor, 1),
(@idBuzo, @idTalle, 1);

-- Taza: Solo Color
INSERT INTO Producto_Atributos_Asignados (id_producto, id_atributo, requerido) VALUES
(@idTaza, @idColor, 1);

-- Gorra: Solo Color
INSERT INTO Producto_Atributos_Asignados (id_producto, id_atributo, requerido) VALUES
(@idGorra, @idColor, 1);

-- Bolsa: Solo Color
INSERT INTO Producto_Atributos_Asignados (id_producto, id_atributo, requerido) VALUES
(@idBolsa, @idColor, 1);

PRINT '✓ Atributos asignados';

-- ============================================================
-- CREAR VARIANTES
-- ============================================================
PRINT 'Creando variantes...';

-- IDs de valores de atributos
DECLARE @colorNegro INT = (SELECT id_valor FROM Producto_Atributo_Valores WHERE valor = 'Negro' AND id_atributo = @idColor);
DECLARE @colorBlanco INT = (SELECT id_valor FROM Producto_Atributo_Valores WHERE valor = 'Blanco' AND id_atributo = @idColor);
DECLARE @colorRojo INT = (SELECT id_valor FROM Producto_Atributo_Valores WHERE valor = 'Rojo' AND id_atributo = @idColor);
DECLARE @colorAzul INT = (SELECT id_valor FROM Producto_Atributo_Valores WHERE valor = 'Azul' AND id_atributo = @idColor);

DECLARE @talleS INT = (SELECT id_valor FROM Producto_Atributo_Valores WHERE valor = 'S' AND id_atributo = @idTalle);
DECLARE @talleM INT = (SELECT id_valor FROM Producto_Atributo_Valores WHERE valor = 'M' AND id_atributo = @idTalle);
DECLARE @talleL INT = (SELECT id_valor FROM Producto_Atributo_Valores WHERE valor = 'L' AND id_atributo = @idTalle);
DECLARE @talleXL INT = (SELECT id_valor FROM Producto_Atributo_Valores WHERE valor = 'XL' AND id_atributo = @idTalle);

-- VARIANTES DE REMERA (16 variantes: 4 colores × 4 talles)
-- Negro
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idRemera, 'REM-NEG-S', 12000, 100);
DECLARE @v1 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@v1, @idColor, @colorNegro), (@v1, @idTalle, @talleS);

INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idRemera, 'REM-NEG-M', 12000, 100);
DECLARE @v2 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@v2, @idColor, @colorNegro), (@v2, @idTalle, @talleM);

INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idRemera, 'REM-NEG-L', 12000, 100);
DECLARE @v3 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@v3, @idColor, @colorNegro), (@v3, @idTalle, @talleL);

INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idRemera, 'REM-NEG-XL', 12000, 100);
DECLARE @v4 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@v4, @idColor, @colorNegro), (@v4, @idTalle, @talleXL);

-- Blanco
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idRemera, 'REM-BLA-S', 12000, 100);
DECLARE @v5 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@v5, @idColor, @colorBlanco), (@v5, @idTalle, @talleS);

INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idRemera, 'REM-BLA-M', 12000, 100);
DECLARE @v6 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@v6, @idColor, @colorBlanco), (@v6, @idTalle, @talleM);

INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idRemera, 'REM-BLA-L', 12000, 100);
DECLARE @v7 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@v7, @idColor, @colorBlanco), (@v7, @idTalle, @talleL);

INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idRemera, 'REM-BLA-XL', 12000, 100);
DECLARE @v8 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@v8, @idColor, @colorBlanco), (@v8, @idTalle, @talleXL);

-- Rojo
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idRemera, 'REM-ROJ-S', 12000, 100);
DECLARE @v9 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@v9, @idColor, @colorRojo), (@v9, @idTalle, @talleS);

INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idRemera, 'REM-ROJ-M', 12000, 100);
DECLARE @v10 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@v10, @idColor, @colorRojo), (@v10, @idTalle, @talleM);

INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idRemera, 'REM-ROJ-L', 12000, 100);
DECLARE @v11 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@v11, @idColor, @colorRojo), (@v11, @idTalle, @talleL);

INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idRemera, 'REM-ROJ-XL', 12000, 100);
DECLARE @v12 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@v12, @idColor, @colorRojo), (@v12, @idTalle, @talleXL);

-- Azul
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idRemera, 'REM-AZU-S', 12000, 100);
DECLARE @v13 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@v13, @idColor, @colorAzul), (@v13, @idTalle, @talleS);

INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idRemera, 'REM-AZU-M', 12000, 100);
DECLARE @v14 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@v14, @idColor, @colorAzul), (@v14, @idTalle, @talleM);

INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idRemera, 'REM-AZU-L', 12000, 100);
DECLARE @v15 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@v15, @idColor, @colorAzul), (@v15, @idTalle, @talleL);

INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idRemera, 'REM-AZU-XL', 12000, 100);
DECLARE @v16 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@v16, @idColor, @colorAzul), (@v16, @idTalle, @talleXL);

PRINT '✓ 16 variantes de Remera creadas';

-- VARIANTES DE TAZA (4 colores)
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idTaza, 'TAZ-NEG', 8000, 200);
DECLARE @t1 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@t1, @idColor, @colorNegro);

INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idTaza, 'TAZ-BLA', 8000, 200);
DECLARE @t2 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@t2, @idColor, @colorBlanco);

INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idTaza, 'TAZ-ROJ', 8000, 200);
DECLARE @t3 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@t3, @idColor, @colorRojo);

INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idTaza, 'TAZ-AZU', 8000, 200);
DECLARE @t4 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@t4, @idColor, @colorAzul);

PRINT '✓ 4 variantes de Taza creadas';

-- VARIANTES DE BUZO (4 colores × 4 talles = 16)
-- Negro
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idBuzo, 'BUZ-NEG-M', 25000, 50);
DECLARE @b1 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@b1, @idColor, @colorNegro), (@b1, @idTalle, @talleM);

INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idBuzo, 'BUZ-NEG-L', 25000, 50);
DECLARE @b2 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@b2, @idColor, @colorNegro), (@b2, @idTalle, @talleL);

-- Blanco
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idBuzo, 'BUZ-BLA-M', 25000, 50);
DECLARE @b3 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@b3, @idColor, @colorBlanco), (@b3, @idTalle, @talleM);

INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idBuzo, 'BUZ-BLA-L', 25000, 50);
DECLARE @b4 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@b4, @idColor, @colorBlanco), (@b4, @idTalle, @talleL);

PRINT '✓ 4 variantes de Buzo creadas';

-- VARIANTES DE GORRA (4 colores)
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idGorra, 'GOR-NEG', 15000, 150);
DECLARE @g1 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@g1, @idColor, @colorNegro);

INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idGorra, 'GOR-BLA', 15000, 150);
DECLARE @g2 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@g2, @idColor, @colorBlanco);

INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idGorra, 'GOR-ROJ', 15000, 150);
DECLARE @g3 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@g3, @idColor, @colorRojo);

INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idGorra, 'GOR-AZU', 15000, 150);
DECLARE @g4 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@g4, @idColor, @colorAzul);

PRINT '✓ 4 variantes de Gorra creadas';

-- VARIANTES DE BOLSA (4 colores)
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idBolsa, 'BOL-NEG', 10000, 180);
DECLARE @bo1 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@bo1, @idColor, @colorNegro);

INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idBolsa, 'BOL-BLA', 10000, 180);
DECLARE @bo2 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@bo2, @idColor, @colorBlanco);

INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idBolsa, 'BOL-ROJ', 10000, 180);
DECLARE @bo3 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@bo3, @idColor, @colorRojo);

INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual) VALUES (@idBolsa, 'BOL-AZU', 10000, 180);
DECLARE @bo4 INT = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES (@bo4, @idColor, @colorAzul);

PRINT '✓ 4 variantes de Bolsa creadas';

PRINT '';
PRINT '========================================================';
PRINT '✅ BASE DE DATOS POBLADA EXITOSAMENTE';
PRINT '========================================================';
PRINT '';
PRINT 'Resumen:';
SELECT 'Usuarios' AS Tabla, COUNT(*) AS Registros FROM Usuarios
UNION ALL
SELECT 'Atributos', COUNT(*) FROM Producto_Atributos
UNION ALL
SELECT 'Valores Atributos', COUNT(*) FROM Producto_Atributo_Valores
UNION ALL
SELECT 'Productos', COUNT(*) FROM Productos
UNION ALL
SELECT 'Variantes', COUNT(*) FROM Producto_Variantes
UNION ALL
SELECT 'Variante_Atributos', COUNT(*) FROM Variante_Atributos;

PRINT '';
PRINT 'Catálogo disponible:';
SELECT 
    p.nombre AS Producto,
    COUNT(pv.id_variante) AS Variantes,
    MIN(pv.precio) AS Precio_Min,
    MAX(pv.precio) AS Precio_Max,
    SUM(pv.stock_actual) AS Stock_Total
FROM Productos p
LEFT JOIN Producto_Variantes pv ON p.id_producto = pv.id_producto
GROUP BY p.nombre, p.orden_visualizacion
ORDER BY p.orden_visualizacion;

GO
