-- ============================================
-- AI Print Studio - Esquema de Base de Datos
-- SQL Server
-- ============================================

-- Tabla principal: almacena cada pedido realizado
CREATE TABLE pedidos (
    id              INT IDENTITY(1,1) PRIMARY KEY,  -- ID autoincremental
    producto        NVARCHAR(50)   NOT NULL,         -- camiseta, taza, gorra, etc.
    talle           NVARCHAR(10)   NULL,             -- S, M, L, XL, XXL (null para tazas/gorras)
    color           NVARCHAR(30)   NULL,             -- Blanco, Negro, etc.
    precio          DECIMAL(10,2)  NOT NULL,         -- Precio unitario
    cantidad        INT            NOT NULL DEFAULT 1,
    prompt          NVARCHAR(500)  NOT NULL,         -- Texto que el usuario escribió
    imagen_url      NVARCHAR(500)  NOT NULL,         -- Ruta o URL de la imagen generada
    estado          NVARCHAR(20)   NOT NULL DEFAULT 'pendiente',  -- pendiente, pagado, enviado
    payment_id      NVARCHAR(100)  NULL,             -- ID de pago de MercadoPago
    fecha           DATETIME       NOT NULL DEFAULT GETDATE()
);

-- Índice para buscar pedidos por estado
CREATE INDEX IX_pedidos_estado ON pedidos(estado);

-- Índice para buscar pedidos por fecha
CREATE INDEX IX_pedidos_fecha ON pedidos(fecha DESC);
