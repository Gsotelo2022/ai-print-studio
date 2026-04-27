-- ============================================================
-- SCRIPT 3: DATOS INICIALES (Atributos y Productos Base)
-- ============================================================
-- Descripción: Poblar catálogo de productos con sistema de variantes
-- Fecha: 22 de abril de 2026
-- ============================================================

USE PrendeteRock;
GO

PRINT '🚀 CARGANDO DATOS INICIALES';
PRINT '';

-- ============================================================
-- PASO 1: CREAR ATRIBUTOS CONFIGURABLES
-- ============================================================
PRINT '🎨 Creando atributos...';

-- Atributo: Color
INSERT INTO Producto_Atributos (nombre, tipo, descripcion, orden) 
VALUES ('Color', 'select', 'Color del producto', 1);

DECLARE @idColor INT = SCOPE_IDENTITY();

-- Valores de Color
INSERT INTO Producto_Atributo_Valores (id_atributo, valor, codigo_color, orden) VALUES
(@idColor, 'Negro', '#000000', 1),
(@idColor, 'Blanco', '#FFFFFF', 2),
(@idColor, 'Rojo', '#FF0000', 3),
(@idColor, 'Azul', '#0000FF', 4),
(@idColor, 'Verde', '#00FF00', 5),
(@idColor, 'Amarillo', '#FFFF00', 6),
(@idColor, 'Gris', '#808080', 7);

-- Atributo: Talle
INSERT INTO Producto_Atributos (nombre, tipo, descripcion, orden) 
VALUES ('Talle', 'select', 'Talle del producto', 2);

DECLARE @idTalle INT = SCOPE_IDENTITY();

-- Valores de Talle
INSERT INTO Producto_Atributo_Valores (id_atributo, valor, orden) VALUES
(@idTalle, 'XS', 1),
(@idTalle, 'S', 2),
(@idTalle, 'M', 3),
(@idTalle, 'L', 4),
(@idTalle, 'XL', 5),
(@idTalle, 'XXL', 6);

-- Atributo: Material (opcional)
INSERT INTO Producto_Atributos (nombre, tipo, descripcion, orden) 
VALUES ('Material', 'select', 'Material del producto', 3);

DECLARE @idMaterial INT = SCOPE_IDENTITY();

-- Valores de Material
INSERT INTO Producto_Atributo_Valores (id_atributo, valor, orden) VALUES
(@idMaterial, 'Algodón 100%', 1),
(@idMaterial, 'Poliéster', 2),
(@idMaterial, 'Mezcla', 3),
(@idMaterial, 'Cerámica', 4);

PRINT '✅ Atributos creados: Color, Talle, Material';

-- ============================================================
-- PASO 2: CREAR PRODUCTOS BASE
-- ============================================================
PRINT '📦 Creando productos base...';

-- Producto 1: Remera
INSERT INTO Productos (nombre, descripcion, categoria, imagen_mockup, area_impresion_ancho, area_impresion_alto, orden_visualizacion)
VALUES (
    'Remera Básica',
    'Remera de algodón 100% ideal para personalizar con tus diseños',
    'Indumentaria',
    '/assets/mockups/remera.png',
    800,
    1000,
    1
);

DECLARE @idRemera INT = SCOPE_IDENTITY();

-- Asignar atributos a Remera (Color + Talle)
INSERT INTO Producto_Atributos_Asignados (id_producto, id_atributo, requerido) VALUES
(@idRemera, @idColor, 1),
(@idRemera, @idTalle, 1);

-- Producto 2: Taza
INSERT INTO Productos (nombre, descripcion, categoria, imagen_mockup, area_impresion_ancho, area_impresion_alto, orden_visualizacion)
VALUES (
    'Taza Personalizada',
    'Taza de cerámica de 300ml apta para microondas',
    'Hogar',
    '/assets/mockups/taza.png',
    600,
    400,
    2
);

DECLARE @idTaza INT = SCOPE_IDENTITY();

-- Asignar atributos a Taza (solo Color)
INSERT INTO Producto_Atributos_Asignados (id_producto, id_atributo, requerido) VALUES
(@idTaza, @idColor, 1);

-- Producto 3: Buzo/Sudadera
INSERT INTO Productos (nombre, descripcion, categoria, imagen_mockup, area_impresion_ancho, area_impresion_alto, orden_visualizacion)
VALUES (
    'Buzo con Capucha',
    'Buzo canguro con capucha, 70% algodón 30% poliéster',
    'Indumentaria',
    '/assets/mockups/buzo.png',
    900,
    1100,
    3
);

DECLARE @idBuzo INT = SCOPE_IDENTITY();

-- Asignar atributos a Buzo
INSERT INTO Producto_Atributos_Asignados (id_producto, id_atributo, requerido) VALUES
(@idBuzo, @idColor, 1),
(@idBuzo, @idTalle, 1);

-- Producto 4: Gorra
INSERT INTO Productos (nombre, descripcion, categoria, imagen_mockup, area_impresion_ancho, area_impresion_alto, orden_visualizacion)
VALUES (
    'Gorra Trucker',
    'Gorra tipo trucker con malla trasera',
    'Accesorios',
    '/assets/mockups/gorra.png',
    400,
    200,
    4
);

DECLARE @idGorra INT = SCOPE_IDENTITY();

-- Asignar atributos a Gorra (solo Color)
INSERT INTO Producto_Atributos_Asignados (id_producto, id_atributo, requerido) VALUES
(@idGorra, @idColor, 1);

-- Producto 5: Bolso Tote
INSERT INTO Productos (nombre, descripcion, categoria, imagen_mockup, area_impresion_ancho, area_impresion_alto, orden_visualizacion)
VALUES (
    'Bolsa Tote',
    'Bolsa de tela 100% algodón ecológica',
    'Accesorios',
    '/assets/mockups/bolsa.png',
    700,
    800,
    5
);

DECLARE @idBolsa INT = SCOPE_IDENTITY();

-- Asignar atributos a Bolsa
INSERT INTO Producto_Atributos_Asignados (id_producto, id_atributo, requerido) VALUES
(@idBolsa, @idColor, 1);

PRINT '✅ Productos base creados: Remera, Taza, Buzo, Gorra, Bolsa';

-- ============================================================
-- PASO 3: CREAR VARIANTES (combinaciones de atributos)
-- ============================================================
PRINT '🎯 Creando variantes...';

-- Obtener IDs de valores
DECLARE @valorNegro INT = (SELECT id_valor FROM Producto_Atributo_Valores WHERE id_atributo = @idColor AND valor = 'Negro');
DECLARE @valorBlanco INT = (SELECT id_valor FROM Producto_Atributo_Valores WHERE id_atributo = @idColor AND valor = 'Blanco');
DECLARE @valorRojo INT = (SELECT id_valor FROM Producto_Atributo_Valores WHERE id_atributo = @idColor AND valor = 'Rojo');
DECLARE @valorAzul INT = (SELECT id_valor FROM Producto_Atributo_Valores WHERE id_atributo = @idColor AND valor = 'Azul');

DECLARE @talleM INT = (SELECT id_valor FROM Producto_Atributo_Valores WHERE id_atributo = @idTalle AND valor = 'M');
DECLARE @talleL INT = (SELECT id_valor FROM Producto_Atributo_Valores WHERE id_atributo = @idTalle AND valor = 'L');
DECLARE @talleXL INT = (SELECT id_valor FROM Producto_Atributo_Valores WHERE id_atributo = @idTalle AND valor = 'XL');

-- ============================================================
-- VARIANTES DE REMERA (Negro y Blanco, talles M, L, XL)
-- ============================================================
DECLARE @idVariante INT;

-- Remera Negra M
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual, costo_produccion) 
VALUES (@idRemera, 'REM-NEG-M', 12000, 50, 6000);
SET @idVariante = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES
(@idVariante, @idColor, @valorNegro),
(@idVariante, @idTalle, @talleM);

-- Remera Negra L
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual, costo_produccion) 
VALUES (@idRemera, 'REM-NEG-L', 12000, 45, 6000);
SET @idVariante = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES
(@idVariante, @idColor, @valorNegro),
(@idVariante, @idTalle, @talleL);

-- Remera Negra XL
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual, costo_produccion) 
VALUES (@idRemera, 'REM-NEG-XL', 12000, 40, 6000);
SET @idVariante = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES
(@idVariante, @idColor, @valorNegro),
(@idVariante, @idTalle, @talleXL);

-- Remera Blanca M
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual, costo_produccion) 
VALUES (@idRemera, 'REM-BLA-M', 12000, 55, 6000);
SET @idVariante = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES
(@idVariante, @idColor, @valorBlanco),
(@idVariante, @idTalle, @talleM);

-- Remera Blanca L
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual, costo_produccion) 
VALUES (@idRemera, 'REM-BLA-L', 12000, 50, 6000);
SET @idVariante = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES
(@idVariante, @idColor, @valorBlanco),
(@idVariante, @idTalle, @talleL);

-- Remera Blanca XL
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual, costo_produccion) 
VALUES (@idRemera, 'REM-BLA-XL', 12000, 45, 6000);
SET @idVariante = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES
(@idVariante, @idColor, @valorBlanco),
(@idVariante, @idTalle, @talleXL);

-- ============================================================
-- VARIANTES DE TAZA (colores simples, sin talle)
-- ============================================================

-- Taza Blanca
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual, costo_produccion) 
VALUES (@idTaza, 'TAZ-BLA', 8000, 80, 4000);
SET @idVariante = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES
(@idVariante, @idColor, @valorBlanco);

-- Taza Negra
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual, costo_produccion) 
VALUES (@idTaza, 'TAZ-NEG', 8000, 70, 4000);
SET @idVariante = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES
(@idVariante, @idColor, @valorNegro);

-- Taza Roja
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual, costo_produccion) 
VALUES (@idTaza, 'TAZ-ROJO', 8000, 60, 4000);
SET @idVariante = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES
(@idVariante, @idColor, @valorRojo);

-- ============================================================
-- VARIANTES DE BUZO
-- ============================================================

-- Buzo Negro L
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual, costo_produccion) 
VALUES (@idBuzo, 'BUZ-NEG-L', 18000, 30, 9000);
SET @idVariante = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES
(@idVariante, @idColor, @valorNegro),
(@idVariante, @idTalle, @talleL);

-- Buzo Negro XL
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual, costo_produccion) 
VALUES (@idBuzo, 'BUZ-NEG-XL', 18000, 25, 9000);
SET @idVariante = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES
(@idVariante, @idColor, @valorNegro),
(@idVariante, @idTalle, @talleXL);

-- Buzo Azul L
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual, costo_produccion) 
VALUES (@idBuzo, 'BUZ-AZU-L', 18000, 28, 9000);
SET @idVariante = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES
(@idVariante, @idColor, @valorAzul),
(@idVariante, @idTalle, @talleL);

-- ============================================================
-- VARIANTES DE GORRA
-- ============================================================

-- Gorra Negra
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual, costo_produccion) 
VALUES (@idGorra, 'GOR-NEG', 10000, 40, 5000);
SET @idVariante = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES
(@idVariante, @idColor, @valorNegro);

-- Gorra Blanca
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual, costo_produccion) 
VALUES (@idGorra, 'GOR-BLA', 10000, 35, 5000);
SET @idVariante = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES
(@idVariante, @idColor, @valorBlanco);

-- ============================================================
-- VARIANTES DE BOLSA
-- ============================================================

-- Bolsa Blanca
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual, costo_produccion) 
VALUES (@idBolsa, 'BOL-BLA', 6000, 60, 3000);
SET @idVariante = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES
(@idVariante, @idColor, @valorBlanco);

-- Bolsa Negra
INSERT INTO Producto_Variantes (id_producto, sku, precio, stock_actual, costo_produccion) 
VALUES (@idBolsa, 'BOL-NEG', 6000, 55, 3000);
SET @idVariante = SCOPE_IDENTITY();
INSERT INTO Variante_Atributos (id_variante, id_atributo, id_valor) VALUES
(@idVariante, @idColor, @valorNegro);

PRINT '✅ Variantes creadas: 19 SKUs activos';

-- ============================================================
-- RESUMEN DE DATOS CARGADOS
-- ============================================================
PRINT '';
PRINT '📊 RESUMEN DE DATOS INICIALES:';
PRINT '   ✅ 3 Atributos (Color, Talle, Material)';
PRINT '   ✅ 17 Valores de atributos';
PRINT '   ✅ 5 Productos base';
PRINT '   ✅ 19 Variantes (SKUs)';
PRINT '';
PRINT '🎯 SIGUIENTE PASO: Ejecutar script 04-migrar-datos-antiguos.sql';
PRINT '   Para migrar usuarios y pedidos de la BD antigua';

GO
