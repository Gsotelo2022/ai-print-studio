<?php
// api/login.php
// Endpoint para autenticar usuario por email/contraseña

declare(strict_types=1);

require_once __DIR__ . '/../helpers/response.php';
require_once __DIR__ . '/../config/database.php';

setupHeaders();

try {
    $input = json_decode(file_get_contents('php://input'), true);
    if (!is_array($input)) {
        jsonError('JSON inválido en la petición');
    }

    if (empty($input['email']) || empty($input['password'])) {
        jsonError('Email y contraseña son requeridos');
    }

    $email = $input['email'];
    $password = $input['password'];

    // Obtener conexión PDO unificada
    $pdo = getDBConnection();

    // Obtener usuario por email
    $sql = "SELECT id_usuario AS id, Nombre, Email, [contraseña], Tipo FROM Usuarios WHERE Email = ?";
    $stmt = $pdo->prepare($sql);
    $stmt->execute([$email]);
    
    $user = $stmt->fetch(PDO::FETCH_ASSOC);
    if (!$user) {
        jsonError('Credenciales inválidas', 401);
    }

    $hash = $user['contraseña'] ?? '';
    
    if (!password_verify($password, $hash)) {
        jsonError('Credenciales inválidas', 401);
    }

    // Excluir contraseña de la respuesta
    unset($user['contraseña']);

    jsonSuccess($user);

} catch (Throwable $e) {
    jsonError('Error del servidor: ' . $e->getMessage(), 500);
}
