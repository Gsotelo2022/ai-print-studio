<?php
// api/get-users.php
// Endpoint: devuelve la lista de usuarios desde la tabla Usuarios

declare(strict_types=1);

require_once __DIR__ . '/../helpers/response.php';
require_once __DIR__ . '/../config/database.php';

setupHeaders();

try {
    // Obtener conexión PDO unificada
    $pdo = getDBConnection();

    // Query - usar alias para devolver Id, Nombre, Email
    $sql = "SELECT id_usuario AS Id, Nombre, Email FROM Usuarios ORDER BY Nombre";
    $stmt = $pdo->query($sql);
    
    $users = $stmt->fetchAll(PDO::FETCH_ASSOC);

    jsonSuccess($users);

} catch (Throwable $e) {
    jsonError('Error del servidor: ' . $e->getMessage(), 500);
}
