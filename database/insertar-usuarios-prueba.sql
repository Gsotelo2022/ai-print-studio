-- =============================================================
-- USUARIOS DE PRUEBA PARA TESTING
-- =============================================================
-- Contraseña hasheada: PBKDF2-HMAC-SHA256

-- Cliente de prueba
INSERT INTO Usuarios (Nombre, Email, telefono, password_user, Tipo, fecha_registro)
VALUES (
    'Cliente Test',
    'cliente@test.com',
    '1234567890',
    'sha256$2500$someRandomSalt$hashedPassword',  -- password123 hasheado
    'cliente',
    GETDATE()
);

-- Admin de prueba
INSERT INTO Usuarios (Nombre, Email, telefono, password_user, Tipo, fecha_registro)
VALUES (
    'Admin Test',
    'admin@test.com',
    '0987654321',
    'sha256$2500$someRandomSalt$hashedPassword',  -- password123 hasheado
    'admin',
    GETDATE()
);

-- Verificar
SELECT * FROM Usuarios;
