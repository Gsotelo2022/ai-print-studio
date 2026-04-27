<?php
require_once __DIR__ . '/../config/database.php';

header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Headers: Content-Type");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

header("Content-Type: application/json");

try {
    // =========================
    // CONEXIÓN SQL SERVER (PDO)
    // =========================
    $pdo = getDBConnection();

    // =========================
    // PAGINACIÓN
    // =========================
    $page = isset($_GET['page']) ? intval($_GET['page']) : 1;
    $limit = isset($_GET['limit']) ? intval($_GET['limit']) : 10;
    $offset = ($page - 1) * $limit;

    // =========================
    // STATS
    // =========================
    $sql_total = "SELECT COUNT(*) as total FROM Usuarios";
    $stmt = $pdo->query($sql_total);
    $total_usuarios = $stmt->fetch(PDO::FETCH_ASSOC)['total'];

    $sql_semana = "
        SELECT COUNT(*) as total 
        FROM Usuarios 
        WHERE fecha_registro >= DATEADD(day, -7, GETDATE())
    ";
    $stmt = $pdo->query($sql_semana);
    $usuarios_semana = $stmt->fetch(PDO::FETCH_ASSOC)['total'];

    $sql_tipo = "
        SELECT tipo as tipo_usuario, COUNT(*) as total
        FROM Usuarios
        GROUP BY tipo
    ";
    $stmt = $pdo->query($sql_tipo);

    $usuarios_por_tipo = [];
    while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
        $usuarios_por_tipo[] = $row;
    }

    // =========================
    // ACTIVIDAD
    // =========================
    $sql_actividad = "
        SELECT TOP 5 
            id_usuario,
            Nombre as nombre,
            '' as apellido,
            tipo as tipo_usuario,
            DATEDIFF(MINUTE, fecha_registro, GETDATE()) as minutos_desde_registro
        FROM Usuarios
        ORDER BY fecha_registro DESC
    ";
    $stmt = $pdo->query($sql_actividad);

    $actividad = [];
    while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
        $actividad[] = $row;
    }

    // =========================
    // TOTAL REGISTROS
    // =========================
    $sql_count = "SELECT COUNT(*) as total FROM Usuarios";
    $stmt = $pdo->query($sql_count);
    $total_registros = $stmt->fetch(PDO::FETCH_ASSOC)['total'];

    $total_paginas = ceil($total_registros / $limit);

    // =========================
    // USUARIOS PAGINADOS (SQL SERVER)
    // =========================
    $sql_usuarios = "
        SELECT 
            id_usuario,
            Nombre as nombre,
            Email as email,
            tipo as tipo_usuario,
            fecha_registro
        FROM Usuarios
        ORDER BY id_usuario
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    ";

    $stmt = $pdo->prepare($sql_usuarios);
    $stmt->execute([$offset, $limit]);

    $usuarios = [];
    while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
        // PDO devuelve las fechas como strings, no necesita conversión
        $usuarios[] = $row;
    }

    // =========================
    // RESPUESTA
    // =========================
    echo json_encode([
        "success" => true,
        "stats" => [
            "total_usuarios" => $total_usuarios,
            "usuarios_semana" => $usuarios_semana,
            "usuarios_por_tipo" => $usuarios_por_tipo
        ],
        "usuarios" => $usuarios,
        "actividad" => $actividad,
        "paginacion" => [
            "pagina_actual" => $page,
            "total_paginas" => $total_paginas,
            "total_registros" => $total_registros,
            "registros_por_pagina" => $limit
        ]
    ]);

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        "success" => false,
        "error" => $e->getMessage(),
        "trace" => $e->getTraceAsString()
    ]);
} catch (Error $e) {
    http_response_code(500);
    echo json_encode([
        "success" => false,
        "error" => $e->getMessage(),
        "trace" => $e->getTraceAsString()
    ]);
}
?>