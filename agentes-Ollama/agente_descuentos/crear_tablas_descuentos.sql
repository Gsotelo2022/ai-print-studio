-- ================================================
-- TABLAS PARA SISTEMA DE DESCUENTOS
-- Prendete Rock - Agente de Descuentos
-- ================================================

USE PrendeteRock;
GO

-- ================================================
-- TABLA: Descuentos (Promociones temporales)
-- ================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Descuentos')
BEGIN
    CREATE TABLE Descuentos (
        id_descuento INT IDENTITY(1,1) PRIMARY KEY,
        tipo VARCHAR(50) NOT NULL,              -- 'temporal', 'cantidad', 'categoria', 'especial'
        nombre VARCHAR(100) NOT NULL,
        descripcion TEXT,
        porcentaje DECIMAL(5,2) NOT NULL,       -- Porcentaje de descuento (ej: 15.00)
        fecha_inicio DATE,
        fecha_fin DATE,
        condicion_json TEXT,                     -- Condiciones adicionales en formato JSON
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE()
    );
    
    PRINT '✓ Tabla Descuentos creada';
END
ELSE
    PRINT '○ Tabla Descuentos ya existe';
GO

-- ================================================
-- TABLA: Cupones
-- ================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Cupones')
BEGIN
    CREATE TABLE Cupones (
        id_cupon INT IDENTITY(1,1) PRIMARY KEY,
        codigo VARCHAR(50) UNIQUE NOT NULL,
        descripcion VARCHAR(200),
        descuento_porcentaje DECIMAL(5,2) NOT NULL,
        usos_maximos INT NULL,                   -- NULL = ilimitado
        usos_actuales INT DEFAULT 0,
        fecha_expiracion DATE NULL,              -- NULL = sin expiración
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE()
    );
    
    PRINT '✓ Tabla Cupones creada';
END
ELSE
    PRINT '○ Tabla Cupones ya existe';
GO

-- ================================================
-- INSERTAR DATOS DE EJEMPLO
-- ================================================

-- Descuentos temporales (solo si no existen)
IF NOT EXISTS (SELECT * FROM Descuentos WHERE nombre = 'Black Friday 2024')
BEGIN
    INSERT INTO Descuentos (tipo, nombre, descripcion, porcentaje, fecha_inicio, fecha_fin, activo)
    VALUES 
        ('temporal', 'Black Friday 2024', 'Descuento especial Black Friday', 25.00, '2024-11-01', '2024-11-30', 1),
        ('temporal', 'Cyber Monday', 'Descuento Cyber Monday', 20.00, '2024-12-01', '2024-12-05', 1),
        ('temporal', 'Verano 2025', 'Descuento temporada verano', 15.00, '2025-01-01', '2025-03-31', 1);
    
    PRINT '✓ Descuentos temporales insertados';
END
ELSE
    PRINT '○ Descuentos temporales ya existen';
GO

-- Cupones de ejemplo (solo si no existen)
IF NOT EXISTS (SELECT * FROM Cupones WHERE codigo = 'PRIMERACOMPRA10')
BEGIN
    INSERT INTO Cupones (codigo, descripcion, descuento_porcentaje, usos_maximos, fecha_expiracion, activo)
    VALUES 
        ('PRIMERACOMPRA10', 'Descuento para primera compra', 10.00, NULL, NULL, 1),
        ('AMIGOS15', 'Descuento por referido de amigo', 15.00, 100, '2024-12-31', 1),
        ('VERANO2024', 'Cupón especial verano', 20.00, 50, '2024-03-31', 1),
        ('NAVIDAD2024', 'Cupón especial navidad', 18.00, NULL, '2024-12-26', 1),
        ('VIP25', 'Cupón exclusivo VIP', 25.00, 20, NULL, 1);
    
    PRINT '✓ Cupones insertados';
END
ELSE
    PRINT '○ Cupones ya existen';
GO

-- ================================================
-- ÍNDICES PARA OPTIMIZAR BÚSQUEDAS
-- ================================================

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Cupones_Codigo')
BEGIN
    CREATE INDEX IX_Cupones_Codigo ON Cupones(codigo);
    PRINT '✓ Índice IX_Cupones_Codigo creado';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Descuentos_Fechas')
BEGIN
    CREATE INDEX IX_Descuentos_Fechas ON Descuentos(fecha_inicio, fecha_fin, activo);
    PRINT '✓ Índice IX_Descuentos_Fechas creado';
END
GO

-- ================================================
-- VISTAS ÚTILES
-- ================================================

-- Vista: Descuentos activos
IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_DescuentosActivos')
    DROP VIEW vw_DescuentosActivos;
GO

CREATE VIEW vw_DescuentosActivos AS
SELECT 
    id_descuento,
    tipo,
    nombre,
    descripcion,
    porcentaje,
    fecha_inicio,
    fecha_fin,
    DATEDIFF(DAY, GETDATE(), fecha_fin) as dias_restantes
FROM Descuentos
WHERE activo = 1
AND GETDATE() BETWEEN fecha_inicio AND fecha_fin;
GO

PRINT '✓ Vista vw_DescuentosActivos creada';

-- Vista: Cupones disponibles
IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_CuponesDisponibles')
    DROP VIEW vw_CuponesDisponibles;
GO

CREATE VIEW vw_CuponesDisponibles AS
SELECT 
    id_cupon,
    codigo,
    descripcion,
    descuento_porcentaje,
    CASE 
        WHEN usos_maximos IS NULL THEN 'Ilimitado'
        ELSE CAST((usos_maximos - usos_actuales) AS VARCHAR) + ' restantes'
    END as disponibilidad,
    fecha_expiracion,
    CASE 
        WHEN fecha_expiracion IS NULL THEN 'Sin expiración'
        WHEN fecha_expiracion < GETDATE() THEN 'Expirado'
        ELSE 'Vigente'
    END as estado
FROM Cupones
WHERE activo = 1;
GO

PRINT '✓ Vista vw_CuponesDisponibles creada';

-- ================================================
-- VERIFICACIÓN FINAL
-- ================================================

PRINT '';
PRINT '================================================';
PRINT '   RESUMEN DE INSTALACIÓN';
PRINT '================================================';
PRINT 'Tablas creadas:';
SELECT name as Tabla FROM sys.tables WHERE name IN ('Descuentos', 'Cupones');

PRINT '';
PRINT 'Datos insertados:';
SELECT COUNT(*) as 'Total Descuentos' FROM Descuentos;
SELECT COUNT(*) as 'Total Cupones' FROM Cupones;

PRINT '';
PRINT '✓ Sistema de descuentos instalado correctamente';
PRINT '================================================';
GO
