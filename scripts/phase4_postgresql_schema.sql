-- ================================================================
-- AI Print Studio / Prendete Rock
-- Schema completo para PostgreSQL (pgAdmin)
-- ================================================================
-- Instrucciones:
--   1. Abrir pgAdmin → Tools → Query Tool
--   2. En el panel izquierdo crear la BD manualmente:
--        Servers → tu_servidor → Databases → clic derecho → Create → Database
--        Name: PrendeteRock   (⚠️ respetar mayúsculas — PostgreSQL guarda el nombre tal cual lo ingresás)
--   3. Seleccionar esa BD en el dropdown de pgAdmin (arriba del editor)
--   4. Pegar este script completo y ejecutar (F5)
-- ================================================================

-- Verificación: el script debe ejecutarse CONECTADO a la BD PrendeteRock.
-- Si estás en la BD correcta, esta consulta devuelve 'prendeterock':
-- SELECT current_database();

-- Extensión para UUIDs (opcional)
-- CREATE EXTENSION IF NOT EXISTS "pgcrypto";


-- ================================================================
-- TABLA: Usuarios
-- ================================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario       SERIAL       PRIMARY KEY,
    nombre           VARCHAR(100) NOT NULL,
    email            VARCHAR(100) UNIQUE NOT NULL,
    telefono         VARCHAR(20),
    password_user    VARCHAR(255) NOT NULL,
    tipo             VARCHAR(50)  NOT NULL DEFAULT 'cliente', -- 'cliente' | 'admin'
    cuenta_bloqueada BOOLEAN      NOT NULL DEFAULT FALSE,
    fecha_registro   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios (email);
CREATE INDEX IF NOT EXISTS idx_usuarios_tipo  ON usuarios (tipo);


-- ================================================================
-- TABLA: Productos
-- ================================================================
CREATE TABLE IF NOT EXISTS productos (
    id_producto          SERIAL        PRIMARY KEY,
    nombre               VARCHAR(255)  NOT NULL,
    descripcion          TEXT,
    categoria            VARCHAR(100),
    imagen_mockup        VARCHAR(500),            -- ruta relativa al mockup
    area_impresion_ancho INT,
    area_impresion_alto  INT,
    activo               BOOLEAN       NOT NULL DEFAULT TRUE,
    orden_visualizacion  INT           NOT NULL DEFAULT 0,
    fecha_creacion       TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_productos_activo ON productos (activo);


-- ================================================================
-- TABLA: Producto_Atributos  (ej: "Color", "Talle")
-- ================================================================
CREATE TABLE IF NOT EXISTS producto_atributos (
    id_atributo SERIAL      PRIMARY KEY,
    nombre      VARCHAR(50) NOT NULL UNIQUE    -- 'Color', 'Talle', 'Material', …
);


-- ================================================================
-- TABLA: Producto_Atributo_Valores  (ej: "Rojo", "XL")
-- ================================================================
CREATE TABLE IF NOT EXISTS producto_atributo_valores (
    id_valor    SERIAL       PRIMARY KEY,
    id_atributo INT          NOT NULL REFERENCES producto_atributos (id_atributo) ON DELETE CASCADE,
    valor       VARCHAR(100) NOT NULL,
    UNIQUE (id_atributo, valor)
);


-- ================================================================
-- TABLA: Producto_Variantes
-- ================================================================
CREATE TABLE IF NOT EXISTS producto_variantes (
    id_variante  SERIAL          PRIMARY KEY,
    id_producto  INT             NOT NULL REFERENCES productos (id_producto) ON DELETE CASCADE,
    sku          VARCHAR(100)    UNIQUE,
    precio       NUMERIC(10, 2)  NOT NULL,
    stock_actual INT             NOT NULL DEFAULT 0,
    activo       BOOLEAN         NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_variantes_producto ON producto_variantes (id_producto);
CREATE INDEX IF NOT EXISTS idx_variantes_activo   ON producto_variantes (activo);


-- ================================================================
-- TABLA: Variante_Atributos  (relación variante ↔ valor de atributo)
-- ================================================================
CREATE TABLE IF NOT EXISTS variante_atributos (
    id_variante INT NOT NULL REFERENCES producto_variantes (id_variante) ON DELETE CASCADE,
    id_valor    INT NOT NULL REFERENCES producto_atributo_valores (id_valor) ON DELETE CASCADE,
    PRIMARY KEY (id_variante, id_valor)
);


-- ================================================================
-- TABLA: Archivos_Diseno
-- ================================================================
CREATE TABLE IF NOT EXISTS archivos_diseno (
    id_archivo         SERIAL        PRIMARY KEY,
    id_usuario         INT           NOT NULL REFERENCES usuarios (id_usuario) ON DELETE CASCADE,
    nombre_original    VARCHAR(255),
    nombre_almacenado  VARCHAR(255)  NOT NULL,
    ruta_archivo       VARCHAR(500)  NOT NULL,
    ruta_thumbnail     VARCHAR(500),
    tipo_mime          VARCHAR(100),
    tamano_bytes       INT,
    ancho_px           INT,
    alto_px            INT,
    hash_md5           VARCHAR(32),
    es_generado_ia     BOOLEAN       NOT NULL DEFAULT FALSE,
    prompt_usado       TEXT,
    fecha_subida       TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_disenos_usuario ON archivos_diseno (id_usuario);


-- ================================================================
-- TABLA: Pedidos
-- ================================================================
CREATE TABLE IF NOT EXISTS pedidos (
    id_pedido           SERIAL          PRIMARY KEY,
    numero_orden        VARCHAR(30)     UNIQUE NOT NULL,
    id_usuario          INT             NOT NULL REFERENCES usuarios (id_usuario),
    fecha_pedido        TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    estado              VARCHAR(50)     NOT NULL DEFAULT 'pendiente',
        -- pendiente | en_proceso | enviado | completado | cancelado
    estado_pago         VARCHAR(50)     NOT NULL DEFAULT 'pendiente',
        -- pendiente | aprobado | rechazado
    subtotal            NUMERIC(10, 2)  NOT NULL DEFAULT 0,
    descuento           NUMERIC(10, 2)  NOT NULL DEFAULT 0,
    gastos_envio        NUMERIC(10, 2)  NOT NULL DEFAULT 0,
    total               NUMERIC(10, 2)  NOT NULL DEFAULT 0,
    direccion_envio     VARCHAR(300),
    ciudad              VARCHAR(100),
    provincia           VARCHAR(100),
    codigo_postal       VARCHAR(20),
    telefono_contacto   VARCHAR(30),
    notas_cliente       TEXT,
    notas_admin         TEXT,
    referencia_externa  VARCHAR(200),   -- ID de pago en MercadoPago
    fecha_pago          TIMESTAMPTZ
);

-- Índice compuesto requerido por Phase 4 (acelera /mis-pedidos)
CREATE INDEX IF NOT EXISTS ix_pedidos_usuario_fecha
    ON pedidos (id_usuario ASC, fecha_pedido DESC);

-- Índice para filtros de admin
CREATE INDEX IF NOT EXISTS ix_pedidos_estado_pago_fecha
    ON pedidos (estado ASC, estado_pago ASC, fecha_pedido DESC);


-- ================================================================
-- TABLA: Pedidos_Items
-- ================================================================
CREATE TABLE IF NOT EXISTS pedidos_items (
    id_item            SERIAL         PRIMARY KEY,
    id_pedido          INT            NOT NULL REFERENCES pedidos (id_pedido) ON DELETE CASCADE,
    id_variante        INT            NOT NULL REFERENCES producto_variantes (id_variante),
    cantidad           INT            NOT NULL DEFAULT 1,
    precio_unitario    NUMERIC(10, 2) NOT NULL,
    subtotal           NUMERIC(10, 2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED,
    estado             VARCHAR(50)    NOT NULL DEFAULT 'pendiente',
    -- diseño personalizado
    archivo_diseno     INT            REFERENCES archivos_diseno (id_archivo),
    id_diseno          INT            REFERENCES archivos_diseno (id_archivo),
    tiene_diseno       BOOLEAN        NOT NULL DEFAULT FALSE,
    diseno_posicion_x  NUMERIC(10, 4) DEFAULT 0,
    diseno_posicion_y  NUMERIC(10, 4) DEFAULT 0,
    diseno_zoom        NUMERIC(10, 4) DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_items_pedido   ON pedidos_items (id_pedido);
CREATE INDEX IF NOT EXISTS idx_items_variante ON pedidos_items (id_variante);


-- ================================================================
-- TABLA: Pagos
-- ================================================================
CREATE TABLE IF NOT EXISTS pagos (
    id_pago             SERIAL         PRIMARY KEY,
    id_pedido           INT            NOT NULL REFERENCES pedidos (id_pedido) ON DELETE CASCADE,
    metodo_pago         VARCHAR(50),   -- 'mercadopago' | 'transferencia' | 'efectivo' | 'manual'
    referencia_externa  VARCHAR(200),
    monto               NUMERIC(10, 2) NOT NULL,
    estado              VARCHAR(50)    NOT NULL DEFAULT 'pendiente',
    fecha_pago          TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    fecha_aprobacion    TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_pagos_pedido ON pagos (id_pedido);


-- ================================================================
-- TABLA: Cupones
-- ================================================================
CREATE TABLE IF NOT EXISTS cupones (
    id_cupon                SERIAL         PRIMARY KEY,
    codigo                  VARCHAR(50)    UNIQUE NOT NULL,
    descripcion             VARCHAR(200),
    descuento_porcentaje    NUMERIC(5, 2)  NOT NULL,
    usos_maximos            INT,           -- NULL = ilimitado
    usos_actuales           INT            NOT NULL DEFAULT 0,
    fecha_expiracion        DATE,          -- NULL = sin expiración
    activo                  BOOLEAN        NOT NULL DEFAULT TRUE,
    fecha_creacion          TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_cupones_codigo ON cupones (codigo);


-- ================================================================
-- TABLA: Descuentos  (promociones temporales / por categoría)
-- ================================================================
CREATE TABLE IF NOT EXISTS descuentos (
    id_descuento    SERIAL         PRIMARY KEY,
    tipo            VARCHAR(50)    NOT NULL,   -- 'temporal' | 'cantidad' | 'categoria' | 'especial'
    nombre          VARCHAR(100)   NOT NULL,
    descripcion     TEXT,
    porcentaje      NUMERIC(5, 2)  NOT NULL,
    fecha_inicio    DATE,
    fecha_fin       DATE,
    condicion_json  JSONB,                     -- condiciones extra (PostgreSQL JSONB)
    activo          BOOLEAN        NOT NULL DEFAULT TRUE,
    fecha_creacion  TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_descuentos_fechas ON descuentos (fecha_inicio, fecha_fin, activo);


-- ================================================================
-- TABLA: Pedidos_detalle  (tabla legada — compatibilidad)
--   En el nuevo schema se usa pedidos_items.
--   Se mantiene para migración de datos históricos.
-- ================================================================
CREATE TABLE IF NOT EXISTS pedidos_detalle (
    id_detalle   SERIAL         PRIMARY KEY,
    id_pedido    INT            NOT NULL REFERENCES pedidos (id_pedido),
    id_producto  INT            NOT NULL REFERENCES productos (id_producto),
    detalle      VARCHAR(255),
    imagen       TEXT,          -- Base64 legacy (se migra a imagen_ruta)
    imagen_ruta  VARCHAR(500),  -- Ruta en disco (Phase 4)
    fecha        TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    estado       VARCHAR(50)    NOT NULL DEFAULT 'pendiente',
    pago         VARCHAR(50)    NOT NULL DEFAULT 'pendiente',
    total        NUMERIC(10, 2)
);

CREATE INDEX IF NOT EXISTS idx_pedidos_detalle_pedido   ON pedidos_detalle (id_pedido);
CREATE INDEX IF NOT EXISTS idx_pedidos_detalle_producto ON pedidos_detalle (id_producto);


-- ================================================================
-- VISTAS ÚTILES
-- ================================================================

CREATE OR REPLACE VIEW vw_descuentos_activos AS
SELECT id_descuento, tipo, nombre, descripcion, porcentaje,
       fecha_inicio, fecha_fin,
       (fecha_fin - CURRENT_DATE) AS dias_restantes
FROM   descuentos
WHERE  activo = TRUE
  AND  CURRENT_DATE BETWEEN fecha_inicio AND fecha_fin;


CREATE OR REPLACE VIEW vw_cupones_disponibles AS
SELECT id_cupon, codigo, descripcion, descuento_porcentaje,
       CASE
           WHEN usos_maximos IS NULL THEN 'Ilimitado'
           ELSE (usos_maximos - usos_actuales)::TEXT || ' restantes'
       END AS disponibilidad,
       fecha_expiracion,
       CASE
           WHEN fecha_expiracion IS NULL          THEN 'Sin expiración'
           WHEN fecha_expiracion < CURRENT_DATE   THEN 'Expirado'
           ELSE 'Vigente'
       END AS estado
FROM   cupones
WHERE  activo = TRUE;


-- ================================================================
-- DATOS SEMILLA (desarrollo / staging)
-- ================================================================

INSERT INTO producto_atributos (nombre) VALUES ('Color'), ('Talle')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO cupones (codigo, descripcion, descuento_porcentaje, usos_maximos, fecha_expiracion, activo) VALUES
    ('PRIMERACOMPRA10', 'Descuento primera compra',      10.00, NULL, NULL,             TRUE),
    ('AMIGOS15',        'Descuento por referido',        15.00,  100, '2026-12-31',     TRUE),
    ('VIP25',           'Cupón exclusivo VIP',           25.00,   20, NULL,             TRUE)
ON CONFLICT (codigo) DO NOTHING;


-- ================================================================
-- VERIFICACIÓN FINAL
-- ================================================================

SELECT table_name AS tabla
FROM   information_schema.tables
WHERE  table_schema = 'public'
  AND  table_type   = 'BASE TABLE'
ORDER  BY table_name;
