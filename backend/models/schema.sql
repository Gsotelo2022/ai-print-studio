-- ================================================================
-- Base de Datos: Prendete Rock - AI Print Studio
-- Descripción: Sistema de tienda online con generación de productos
-- ================================================================

-- Crear base de datos
CREATE DATABASE PrendeteRock;
GO

USE PrendeteRock;
GO

-- ================================================================
-- TABLA: Usuarios
-- Descripción: Gestiona usuarios registrados en el sistema
-- ================================================================
CREATE TABLE Usuarios (
    id_usuario INT IDENTITY(1,1) PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    password_user VARCHAR(255) NOT NULL,
    Tipo VARCHAR(50) DEFAULT 'cliente',
    fecha_registro DATETIME DEFAULT GETDATE()
);

-- ================================================================
-- TABLA: Productos
-- Descripción: Catálogo de productos disponibles
-- ================================================================
CREATE TABLE Productos (
    id_producto INT IDENTITY(1,1) PRIMARY KEY,
    Detalle VARCHAR(255),
    Color VARCHAR(50),
    talle VARCHAR(20),
    precio DECIMAL(10,2)
);

-- ================================================================
-- TABLA: Pedidos
-- Descripción: Ordenes de compra de usuarios
-- ================================================================
CREATE TABLE Pedidos (
    id_pedido INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario INT NOT NULL,
    fecha_pedido DATETIME DEFAULT GETDATE(),
    estado VARCHAR(50) DEFAULT 'pendiente',
    
    CONSTRAINT FK_Pedidos_Usuarios 
    FOREIGN KEY (id_usuario) 
    REFERENCES Usuarios(id_usuario)
);

-- ================================================================
-- TABLA: Pedidos_detalle
-- Descripción: Detalles de cada pedido (productos, imágenes editadas)
-- IMPORTANTE: imagen es VARCHAR(MAX) para guardar Base64 de imágenes
-- ================================================================
CREATE TABLE Pedidos_detalle (
    id_detalle INT IDENTITY(1,1) PRIMARY KEY,
    id_pedido INT NOT NULL,
    id_producto INT NOT NULL,
    detalle VARCHAR(255),
    imagen VARCHAR(MAX),
    fecha DATETIME DEFAULT GETDATE(),
    estado VARCHAR(50) DEFAULT 'pendiente',
    pago VARCHAR(50) DEFAULT 'pendiente',
    total DECIMAL(10,2),

    CONSTRAINT FK_Detalle_Pedidos 
    FOREIGN KEY (id_pedido) 
    REFERENCES Pedidos(id_pedido),

    CONSTRAINT FK_Detalle_Productos 
    FOREIGN KEY (id_producto) 
    REFERENCES Productos(id_producto)
);

-- ================================================================
-- ÍNDICES (Mejora de rendimiento)
-- ================================================================
CREATE INDEX idx_usuarios_email ON Usuarios(Email);
CREATE INDEX idx_pedidos_usuario ON Pedidos(id_usuario);
CREATE INDEX idx_pedidos_detalle_pedido ON Pedidos_detalle(id_pedido);
CREATE INDEX idx_pedidos_detalle_producto ON Pedidos_detalle(id_producto);

-- ================================================================
-- FIN DE ESTRUCTURA
-- ================================================================