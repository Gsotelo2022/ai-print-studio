import pyodbc
import sys

output = []

try:
    # Conectar a master para eliminar/crear BD
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=.\\SQLEXPRESS01;'
        'Trusted_Connection=yes;'
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    output.append("- Eliminando BD...")
    cur.execute("DROP DATABASE IF EXISTS PrendeteRock")
    
    output.append("- Creando BD...")
    cur.execute("CREATE DATABASE PrendeteRock")
    
    cur.close()
    conn.close()
    
    # Conectar a PrendeteRock
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=.\\SQLEXPRESS01;'
        'DATABASE=PrendeteRock;'
        'Trusted_Connection=yes;'
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    output.append("- Creando Usuarios...")
    cur.execute("CREATE TABLE Usuarios (id_usuario INT IDENTITY(1,1) PRIMARY KEY, Nombre VARCHAR(100) NOT NULL, Email VARCHAR(100) UNIQUE NOT NULL, telefono VARCHAR(20), password_user VARCHAR(255) NOT NULL, Tipo VARCHAR(50))")
    
    output.append("- Creando Productos...")
    cur.execute("CREATE TABLE Productos (id_producto INT IDENTITY(1,1) PRIMARY KEY, Detalle VARCHAR(255), Color VARCHAR(50), talle VARCHAR(20))")
    
    output.append("- Creando Pedidos...")
    cur.execute("CREATE TABLE Pedidos (id_pedido INT IDENTITY(1,1) PRIMARY KEY, id_usuario INT NOT NULL, CONSTRAINT FK_Pedidos_Usuarios FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario))")
    
    output.append("- Creando Pedidos_detalle...")
    cur.execute("CREATE TABLE Pedidos_detalle (id_detalle INT IDENTITY(1,1) PRIMARY KEY, id_pedido INT NOT NULL, id_producto INT NOT NULL, detalle VARCHAR(255), imagen VARCHAR(255), fecha DATETIME DEFAULT GETDATE(), estado VARCHAR(50), pago VARCHAR(50), total DECIMAL(10,2), CONSTRAINT FK_Detalle_Pedidos FOREIGN KEY (id_pedido) REFERENCES Pedidos(id_pedido), CONSTRAINT FK_Detalle_Productos FOREIGN KEY (id_producto) REFERENCES Productos(id_producto))")
    
    output.append("\nVerificando tablas...")
    cur.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='dbo'")
    tables = cur.fetchall()
    output.append("Tablas creadas:")
    for table in tables:
        output.append(f"  - {table[0]}")
    
    cur.close()
    conn.close()
    
    output.append("\nOK: BD reconstruida correctamente")
    
except Exception as e:
    output.append(f"ERROR: {e}")

# Guardar en archivo y también imprimir
with open('recreate_db_output.txt', 'w') as f:
    for line in output:
        print(line)
        f.write(line + '\n')
