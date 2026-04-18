<?php
// api/get-users.php
// Endpoint de ejemplo: devuelve la lista de usuarios desde la tabla Usuarios

declare(strict_types=1);

// Helpers
require_once __DIR__ . '/../helpers/response.php';

// Config y conexión
// Espera que config/db.php retorne un array con getConnection callable
try {
    $dbConfig = require __DIR__ . '/../config/db.php';
    if (!isset($dbConfig['getConnection']) || !is_callable($dbConfig['getConnection'])) {
        throw new RuntimeException('La configuración de DB no es válida.');
    }
} catch (Throwable $e) {
    // No usar jsonError directo antes de setupHeaders por robustez
    header('Content-Type: application/json; charset=utf-8');
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => $e->getMessage()]);
    exit;
}

// CORS + JSON headers
setupHeaders();

try {
    $conn = $dbConfig['getConnection']();

    // Query de ejemplo - usar alias para devolver Id, Nombre, Email
    $sql = "SELECT id_usuario AS Id, Nombre, Email FROM Usuarios ORDER BY Nombre";

    $stmt = sqlsrv_query($conn, $sql);
    if ($stmt === false) {
        $errors = sqlsrv_errors(SQLSRV_ERR_ERRORS);
        throw new RuntimeException('Error en consulta: ' . json_encode($errors));
    }

    $users = [];
    while ($row = sqlsrv_fetch_array($stmt, SQLSRV_FETCH_ASSOC)) {
        // Asegurar encoding UTF-8 (sqlsrv con CharacterSet UTF-8 ya lo maneja,
        // pero normalizamos por si acaso)
        $users[] = array_map(function ($value) {
            if (is_string($value)) {
                return mb_convert_encoding($value, 'UTF-8', 'UTF-8');
            }
            return $value;
        }, $row);
    }

    // Liberar recursos
    sqlsrv_free_stmt($stmt);
    sqlsrv_close($conn);

    // Responder JSON
    jsonSuccess($users);

} catch (Throwable $e) {
    jsonError('Error del servidor: ' . $e->getMessage(), 500);
}
