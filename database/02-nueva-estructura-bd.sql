-- ============================================================
-- SCRIPT 2: NUEVA ESTRUCTURA DE BASE DE DATOS MEJORADA
-- ============================================================
-- Proyecto: AI Print Studio - Prendete Rock
-- Descripción: Estructura optimizada con sistema de variantes
-- Fecha: 22 de abril de 2026
-- ============================================================

USE PrendeteRock;
GO

PRINT '🚀 INICIANDO CREACIÓN DE NUEVA ESTRUCTURA';
PRINT '';

-- ============================================================
-- PASO 1: RENOMBRAR TABLAS ANTIGUAS (no eliminar aún)
-- ============================================================
PRINT '📦 Renombrando tablas antiguas...';

-- Verificar si las tablas old ya existen y eliminarlas
IF OBJECT_ID('Usuarios_OLD', 'U') IS NOT NULL DROP TABLE Usuarios_OLD;
IF OBJECT_ID('Pedidos_detalle_OLD', 'U') IS NOT NULL DROP TABLE Pedidos_detalle_OLD;
IF OBJECT_ID('Pedidos_OLD', 'U') IS NOT NULL DROP TABLE Pedidos_OLD;
IF OBJECT_ID('Productos_OLD', 'U') IS NOT NULL DROP TABLE Productos_OLD;

-- Renombrar tablas actuales (mantener como backup)
IF OBJECT_ID('Pedidos_detalle', 'U') IS NOT NULL
    EXEC sp_rename 'Pedidos_detalle', 'Pedidos_detalle_OLD';

IF OBJECT_ID('Pedidos', 'U') IS NOT NULL
    EXEC sp_rename 'Pedidos', 'Pedidos_OLD';

IF OBJECT_ID('Productos', 'U') IS NOT NULL
    EXEC sp_rename 'Productos', 'Productos_OLD';

IF OBJECT_ID('Usuarios', 'U') IS NOT NULL
    EXEC sp_rename 'Usuarios', 'Usuarios_OLD';

PRINT '✅ Tablas antiguas respaldadas';
PRINT '';

-- ============================================================
-- MÓDULO: USUARIOS
-- ============================================================
PRINT '👥 Creando tabla Usuarios...';

CREATE TABLE Usuarios (
    id_usuario INT IDENTITY(1,1) PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    password_user VARCHAR(255) NOT NULL,
    Tipo VARCHAR(50) DEFAULT 'cliente',
    fecha_registro DATETIME DEFAULT GETDATE(),
    
    -- Nuevos campos
    avatar_url VARCHAR(255) NULL,
    fecha_ultimo_login DATETIME NULL,
    intentos_login_fallidos INT DEFAULT 0,
    cuenta_bloqueada BIT DEFAULT 0,
    
    CONSTRAINT CK_Usuario_Tipo CHECK (Tipo IN ('cliente', 'admin'))
);

CREATE INDEX idx_usuarios_email ON Usuarios(Email);
CREATE INDEX idx_usuarios_tipo ON Usuarios(Tipo);

PRINT '✅ Tabla Usuarios creada';

-- ============================================================
-- MÓDULO: PRODUCTOS BASE
-- ============================================================
PRINT '📦 Creando sistema de productos...';

-- 1. PRODUCTOS BASE (catálogo general)
CREATE TABLE Productos (
    id_producto INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(500),
    categoria VARCHAR(50),
    imagen_mockup VARCHAR(255),
    area_impresion_ancho INT DEFAULT 800,
    area_impresion_alto INT DEFAULT 1000,
    activo BIT DEFAULT 1,
    orden_visualizacion INT DEFAULT 0,
    fecha_creacion DATETIME DEFAULT GETDATE(),
    fecha_modificacion DATETIME DEFAULT GETDATE()
);

CREATE INDEX idx_productos_activo ON Productos(activo) WHERE activo = 1;
CREATE INDEX idx_productos_categoria ON Productos(categoria);

-- 2. ATRIBUTOS CONFIGURABLES (Color, Talle, Material, etc.)
CREATE TABLE Producto_Atributos (
    id_atributo INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    tipo VARCHAR(20) NOT NULL DEFAULT 'select',
    descripcion VARCHAR(255),
    orden INT DEFAULT 0,
    
    CONSTRAINT CK_Atributo_Tipo CHECK (tipo IN ('select', 'radio', 'checkbox', 'text'))
);

-- 3. VALORES POSIBLES PARA CADA ATRIBUTO
CREATE TABLE Producto_Atributo_Valores (
    id_valor INT IDENTITY(1,1) PRIMARY KEY,
    id_atributo INT NOT NULL,
    valor VARCHAR(50) NOT NULL,
    codigo_color VARCHAR(7) NULL,
    orden INT DEFAULT 0,
    
    CONSTRAINT FK_AtributoValores_Atributo 
        FOREIGN KEY (id_atributo) REFERENCES Producto_Atributos(id_atributo) ON DELETE CASCADE
);

CREATE INDEX idx_atributo_valores_atributo ON Producto_Atributo_Valores(id_atributo);

-- 4. RELACIÓN: ¿QUÉ ATRIBUTOS TIENE CADA PRODUCTO?
CREATE TABLE Producto_Atributos_Asignados (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_producto INT NOT NULL,
    id_atributo INT NOT NULL,
    requerido BIT DEFAULT 1,
    
    CONSTRAINT FK_ProdAtrib_Producto 
        FOREIGN KEY (id_producto) REFERENCES Productos(id_producto) ON DELETE CASCADE,
    CONSTRAINT FK_ProdAtrib_Atributo 
        FOREIGN KEY (id_atributo) REFERENCES Producto_Atributos(id_atributo),
    CONSTRAINT UQ_Producto_Atributo UNIQUE (id_producto, id_atributo)
);

-- 5. VARIANTES (SKU: Stock Keeping Unit)
CREATE TABLE Producto_Variantes (
    id_variante INT IDENTITY(1,1) PRIMARY KEY,
    id_producto INT NOT NULL,
    sku VARCHAR(50) UNIQUE NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    costo_produccion DECIMAL(10,2) DEFAULT 0,
    stock_actual INT DEFAULT 0,
    stock_minimo INT DEFAULT 5,
    stock_maximo INT DEFAULT 100,
    activo BIT DEFAULT 1,
    peso_gramos INT DEFAULT 0,
    
    CONSTRAINT FK_Variante_Producto 
        FOREIGN KEY (id_producto) REFERENCES Productos(id_producto),
    CONSTRAINT CK_Stock_Positivo CHECK (stock_actual >= 0),
    CONSTRAINT CK_Precio_Positivo CHECK (precio > 0)
);

CREATE INDEX idx_variantes_producto ON Producto_Variantes(id_producto);
CREATE INDEX idx_variantes_sku ON Producto_Variantes(sku);
CREATE INDEX idx_variantes_activo ON Producto_Variantes(activo) WHERE activo = 1;

-- 6. VALORES ESPECÍFICOS DE CADA VARIANTE
CREATE TABLE Variante_Atributos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_variante INT NOT NULL,
    id_atributo INT NOT NULL,
    id_valor INT NOT NULL,
    
    CONSTRAINT FK_VarAtrib_Variante 
        FOREIGN KEY (id_variante) REFERENCES Producto_Variantes(id_variante) ON DELETE CASCADE,
    CONSTRAINT FK_VarAtrib_Atributo 
        FOREIGN KEY (id_atributo) REFERENCES Producto_Atributos(id_atributo),
    CONSTRAINT FK_VarAtrib_Valor 
        FOREIGN KEY (id_valor) REFERENCES Producto_Atributo_Valores(id_valor)
);

CREATE INDEX idx_variante_atributos_variante ON Variante_Atributos(id_variante);

PRINT '✅ Sistema de productos creado';

-- ============================================================
-- MÓDULO: ARCHIVOS E IMÁGENES
-- ============================================================
PRINT '🖼️  Creando tabla de archivos...';

CREATE TABLE Archivos_Diseno (
    id_archivo INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario INT NOT NULL,
    
    -- Información del archivo
    nombre_original VARCHAR(255),
    nombre_almacenado VARCHAR(255) UNIQUE NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    ruta_thumbnail VARCHAR(500) NULL,
    
    -- Metadata
    tipo_mime VARCHAR(100),
    tamano_bytes BIGINT,
    ancho_px INT,
    alto_px INT,
    
    -- Generación IA
    es_generado_ia BIT DEFAULT 0,
    prompt_usado TEXT NULL,
    modelo_ia VARCHAR(100) NULL,
    
    -- Control
    fecha_subida DATETIME DEFAULT GETDATE(),
    hash_md5 VARCHAR(32) NULL,
    
    CONSTRAINT FK_Archivos_Usuario 
        FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
);

CREATE INDEX idx_archivos_usuario ON Archivos_Diseno(id_usuario);
CREATE INDEX idx_archivos_hash ON Archivos_Diseno(hash_md5);
CREATE INDEX idx_archivos_fecha ON Archivos_Diseno(fecha_subida DESC);

PRINT '✅ Tabla Archivos_Diseno creada';

-- ============================================================
-- MÓDULO: PEDIDOS
-- ============================================================
PRINT '🛒 Creando sistema de pedidos...';

-- 7. PEDIDOS (encabezado)
CREATE TABLE Pedidos (
    id_pedido INT IDENTITY(1,1) PRIMARY KEY,
    numero_orden VARCHAR(20) UNIQUE NOT NULL,
    id_usuario INT NOT NULL,
    
    -- Montos
    subtotal DECIMAL(10,2) DEFAULT 0,
    descuento DECIMAL(10,2) DEFAULT 0,
    gastos_envio DECIMAL(10,2) DEFAULT 0,
    total DECIMAL(10,2) NOT NULL,
    
    -- Estados
    estado VARCHAR(50) DEFAULT 'pendiente',
    estado_pago VARCHAR(50) DEFAULT 'pendiente',
    
    -- Fechas
    fecha_pedido DATETIME DEFAULT GETDATE(),
    fecha_pago DATETIME NULL,
    fecha_produccion_iniciada DATETIME NULL,
    fecha_enviado DATETIME NULL,
    fecha_completado DATETIME NULL,
    fecha_cancelado DATETIME NULL,
    
    -- Datos de envío
    direccion_envio VARCHAR(500),
    ciudad VARCHAR(100),
    provincia VARCHAR(100),
    codigo_postal VARCHAR(20),
    telefono_contacto VARCHAR(50),
    
    -- Tracking
    empresa_envio VARCHAR(100),
    numero_tracking VARCHAR(255),
    
    -- Notas
    notas_cliente TEXT,
    notas_admin TEXT,
    
    CONSTRAINT FK_Pedidos_Usuarios 
        FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario),
    CONSTRAINT CK_Pedido_Total_Positivo CHECK (total >= 0),
    CONSTRAINT CK_Pedido_Estado CHECK (estado IN ('pendiente', 'pagado', 'produccion', 'empaque', 'enviado', 'completado', 'cancelado')),
    CONSTRAINT CK_Pedido_Estado_Pago CHECK (estado_pago IN ('pendiente', 'aprobado', 'rechazado', 'reembolsado'))
);

CREATE INDEX idx_pedidos_usuario ON Pedidos(id_usuario);
CREATE INDEX idx_pedidos_estado ON Pedidos(estado);
CREATE INDEX idx_pedidos_estado_pago ON Pedidos(estado_pago);
CREATE INDEX idx_pedidos_fecha ON Pedidos(fecha_pedido DESC);
CREATE INDEX idx_pedidos_numero ON Pedidos(numero_orden);

-- 8. ITEMS DEL PEDIDO (detalle/líneas)
CREATE TABLE Pedidos_Items (
    id_item INT IDENTITY(1,1) PRIMARY KEY,
    id_pedido INT NOT NULL,
    id_variante INT NOT NULL,
    
    -- Cantidades y precios (snapshot del momento de compra)
    cantidad INT NOT NULL DEFAULT 1,
    precio_unitario DECIMAL(10,2) NOT NULL,
    descuento_unitario DECIMAL(10,2) DEFAULT 0,
    subtotal AS (cantidad * (precio_unitario - descuento_unitario)) PERSISTED,
    
    -- Personalización/Diseño
    tiene_diseno BIT DEFAULT 0,
    archivo_diseno INT NULL,
    diseno_posicion_x INT DEFAULT 0,
    diseno_posicion_y INT DEFAULT 0,
    diseno_zoom DECIMAL(5,2) DEFAULT 1.0,
    diseno_rotacion INT DEFAULT 0,
    
    -- Estado de producción individual
    estado VARCHAR(50) DEFAULT 'pendiente',
    
    CONSTRAINT FK_PedidoItems_Pedido 
        FOREIGN KEY (id_pedido) REFERENCES Pedidos(id_pedido) ON DELETE CASCADE,
    CONSTRAINT FK_PedidoItems_Variante 
        FOREIGN KEY (id_variante) REFERENCES Producto_Variantes(id_variante),
    CONSTRAINT FK_PedidoItems_Archivo 
        FOREIGN KEY (archivo_diseno) REFERENCES Archivos_Diseno(id_archivo),
    CONSTRAINT CK_Item_Cantidad_Positiva CHECK (cantidad > 0),
    CONSTRAINT CK_Item_Estado CHECK (estado IN ('pendiente', 'imprimiendo', 'completado', 'error'))
);

CREATE INDEX idx_items_pedido ON Pedidos_Items(id_pedido);
CREATE INDEX idx_items_variante ON Pedidos_Items(id_variante);
CREATE INDEX idx_items_estado ON Pedidos_Items(estado);

PRINT '✅ Sistema de pedidos creado';

-- ============================================================
-- MÓDULO: PAGOS
-- ============================================================
PRINT '💳 Creando tabla de pagos...';

CREATE TABLE Pagos (
    id_pago INT IDENTITY(1,1) PRIMARY KEY,
    id_pedido INT NOT NULL,
    
    -- Información del pago
    metodo_pago VARCHAR(50) NOT NULL,
    referencia_externa VARCHAR(255),
    monto DECIMAL(10,2) NOT NULL,
    moneda VARCHAR(3) DEFAULT 'ARS',
    
    -- Estado
    estado VARCHAR(50) DEFAULT 'pendiente',
    motivo_rechazo VARCHAR(255),
    
    -- Fechas
    fecha_transaccion DATETIME DEFAULT GETDATE(),
    fecha_aprobacion DATETIME NULL,
    
    -- Metadata (JSON con info de la pasarela)
    datos_adicionales TEXT,
    
    CONSTRAINT FK_Pagos_Pedidos 
        FOREIGN KEY (id_pedido) REFERENCES Pedidos(id_pedido),
    CONSTRAINT CK_Pago_Estado CHECK (estado IN ('pendiente', 'procesando', 'aprobado', 'rechazado', 'reembolsado'))
);

CREATE INDEX idx_pagos_pedido ON Pagos(id_pedido);
CREATE INDEX idx_pagos_estado ON Pagos(estado);
CREATE INDEX idx_pagos_fecha ON Pagos(fecha_transaccion DESC);

PRINT '✅ Tabla Pagos creada';

-- ============================================================
-- MÓDULO: AUDITORÍA Y REPORTES
-- ============================================================
PRINT '📊 Creando tablas de auditoría...';

-- 11. LOG DE CAMBIOS DE ESTADO
CREATE TABLE Pedidos_Historial (
    id_historial INT IDENTITY(1,1) PRIMARY KEY,
    id_pedido INT NOT NULL,
    estado_anterior VARCHAR(50),
    estado_nuevo VARCHAR(50),
    cambio_realizado_por INT NULL,
    motivo TEXT,
    fecha_cambio DATETIME DEFAULT GETDATE(),
    
    CONSTRAINT FK_PedidoHistorial_Pedido 
        FOREIGN KEY (id_pedido) REFERENCES Pedidos(id_pedido),
    CONSTRAINT FK_PedidoHistorial_Usuario
        FOREIGN KEY (cambio_realizado_por) REFERENCES Usuarios(id_usuario)
);

CREATE INDEX idx_historial_pedido ON Pedidos_Historial(id_pedido);
CREATE INDEX idx_historial_fecha ON Pedidos_Historial(fecha_cambio DESC);

-- 12. MOVIMIENTOS DE STOCK
CREATE TABLE Stock_Movimientos (
    id_movimiento INT IDENTITY(1,1) PRIMARY KEY,
    id_variante INT NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    cantidad INT NOT NULL,
    stock_anterior INT NOT NULL,
    stock_nuevo INT NOT NULL,
    motivo VARCHAR(255),
    realizado_por INT NULL,
    fecha DATETIME DEFAULT GETDATE(),
    
    CONSTRAINT FK_StockMov_Variante 
        FOREIGN KEY (id_variante) REFERENCES Producto_Variantes(id_variante),
    CONSTRAINT FK_StockMov_Usuario
        FOREIGN KEY (realizado_por) REFERENCES Usuarios(id_usuario),
    CONSTRAINT CK_Stock_Tipo CHECK (tipo IN ('entrada', 'salida', 'ajuste', 'devolucion'))
);

CREATE INDEX idx_stock_mov_variante ON Stock_Movimientos(id_variante);
CREATE INDEX idx_stock_mov_fecha ON Stock_Movimientos(fecha DESC);

PRINT '✅ Tablas de auditoría creadas';

-- ============================================================
-- TRIGGERS
-- ============================================================
PRINT '⚡ Creando triggers...';

-- Trigger: Guardar historial de cambios de estado
GO
CREATE TRIGGER trg_Pedido_GuardarHistorial
ON Pedidos
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    IF UPDATE(estado)
    BEGIN
        INSERT INTO Pedidos_Historial (id_pedido, estado_anterior, estado_nuevo, fecha_cambio)
        SELECT 
            i.id_pedido,
            d.estado,
            i.estado,
            GETDATE()
        FROM inserted i
        INNER JOIN deleted d ON i.id_pedido = d.id_pedido
        WHERE i.estado <> d.estado;
    END
END;
GO

PRINT '✅ Triggers creados';
PRINT '';
PRINT '🎉 ¡NUEVA ESTRUCTURA CREADA EXITOSAMENTE!';
PRINT '';
PRINT '🎯 SIGUIENTE PASO: Ejecutar script 03-datos-iniciales.sql';
PRINT '   Para cargar atributos, productos base y datos de ejemplo';

GO
