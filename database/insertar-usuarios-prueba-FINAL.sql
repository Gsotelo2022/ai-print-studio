-- =============================================================
-- USUARIOS DE PRUEBA PARA TESTING
-- Contraseña: password123 (hasheada en PBKDF2)
-- =============================================================

-- Cliente de prueba
INSERT INTO Usuarios (Nombre, Email, telefono, password_user, Tipo, fecha_registro)
VALUES (
    'Cliente Test',
    'cliente@test.com',
    '1234567890',
    '2500$fde64b959cf9acd2f6c4a287ab628ddca6b511663375152c078833c3b4ed45e2$bcc18c129948b21dbebcd9e51e8360a5e5c0ba5f035ee03ecdae6365c56ccf77',
    'cliente',
    GETDATE()
);

-- Admin de prueba
INSERT INTO Usuarios (Nombre, Email, telefono, password_user, Tipo, fecha_registro)
VALUES (
    'Admin Test',
    'admin@test.com',
    '0987654321',
    '2500$066bbb4b614f91aeb1560b38cc64e4b1c29a16e2a992bcf3d73d9019df3a4a87$1a09c9b0dbf61f27dccb79456eef449016b98842024b6080e5eee67902e8f316',
    'admin',
    GETDATE()
);

-- Verificar insertados
SELECT id_usuario, Nombre, Email, Tipo FROM Usuarios ORDER BY fecha_registro DESC;
