<?php
// api/login.php
// Endpoint para autenticar usuario por email/contraseña

declare(strict_types=1);

require_once __DIR__ . '/../helpers/response.php';

// Cargar configuración DB
try {
    $dbConfig = require __DIR__ . '/../config/db.php';
    if (!isset($dbConfig['getConnection']) || !is_callable($dbConfig['getConnection'])) {
        throw new RuntimeException('La configuración de DB no es válida.');
    }
} catch (Throwable $e) {
    header('Content-Type: application/json; charset=utf-8');
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => $e->getMessage()]);
    exit;
}

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

    $conn = $dbConfig['getConnection']();

    // Obtener usuario por email
    $sql = "SELECT id_usuario AS id, Nombre, Email, [contraseña], Tipo FROM Usuarios WHERE Email = ?";
    $params = [$email];
    $stmt = sqlsrv_query($conn, $sql, $params);
    if ($stmt === false) {
        throw new RuntimeException('Error al consultar usuario');
    }

    $user = sqlsrv_fetch_array($stmt, SQLSRV_FETCH_ASSOC);
    if (!$user) {
        jsonError('Credenciales inválidas', 401);
    }

    $hash = $user['contraseña'] ?? $user['contraseña'];
    // Dependiendo del driver, el índice puede variar; comprobamos varios
    if (isset($user['contraseña'])) {
        $hash = $user['contraseña'];
    } elseif (isset($user['contraseÃ±a'])) {
        $hash = $user['contraseÃ±a'];
    }

    if (!password_verify($password, $hash)) {
        jsonError('Credenciales inválidas', 401);
    }

    // Excluir contraseña de la respuesta
    unset($user['contraseña']);

    sqlsrv_free_stmt($stmt);
    sqlsrv_close($conn);

    jsonSuccess($user);

} catch (Throwable $e) {
    jsonError('Error del servidor: ' . $e->getMessage(), 500);
}
