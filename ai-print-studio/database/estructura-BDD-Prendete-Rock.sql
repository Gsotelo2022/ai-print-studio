CREATE DATABASE PrendeteRock;
GO

USE PrendeteRock;
GO

CREATE TABLE Usuarios (
    id_usuario INT IDENTITY(1,1) PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    contraseña VARCHAR(255) NOT NULL,
    Tipo VARCHAR(50)
);

CREATE TABLE Productos (
    id_producto INT IDENTITY(1,1) PRIMARY KEY,
    Detalle VARCHAR(255),
    Color VARCHAR(50),
    talle VARCHAR(20)
);

CREATE TABLE Pedidos (
    id_pedido INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario INT NOT NULL,
    
    CONSTRAINT FK_Pedidos_Usuarios 
    FOREIGN KEY (id_usuario) 
    REFERENCES Usuarios(id_usuario)
);

CREATE TABLE Pedidos_detalle (
    id_detalle INT IDENTITY(1,1) PRIMARY KEY,
    id_pedido INT NOT NULL,
    id_producto INT NOT NULL,
    detalle VARCHAR(255),
    imagen VARCHAR(255),
    fecha DATETIME DEFAULT GETDATE(),
    estado VARCHAR(50),
    pago VARCHAR(50),
    total DECIMAL(10,2),

    CONSTRAINT FK_Detalle_Pedidos 
    FOREIGN KEY (id_pedido) 
    REFERENCES Pedidos(id_pedido),

    CONSTRAINT FK_Detalle_Productos 
    FOREIGN KEY (id_producto) 
    REFERENCES Productos(id_producto)
);