<?php
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
    // CONEXIÓN SQL SERVER
    // =========================
    $serverName = "localhost\\SQLEXPRESS01";
    $connectionOptions = [
        "Database" => "PrendeteRock",
        "TrustServerCertificate" => true
    ];

    $conn = sqlsrv_connect($serverName, $connectionOptions);

    if (!$conn) {
        throw new Exception("Error de conexión");
    }

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
    $stmt = sqlsrv_query($conn, $sql_total);
    $total_usuarios = sqlsrv_fetch_array($stmt, SQLSRV_FETCH_ASSOC)['total'];

    $sql_semana = "
        SELECT COUNT(*) as total 
        FROM Usuarios 
        WHERE fecha_registro >= DATEADD(day, -7, GETDATE())
    ";
    $stmt = sqlsrv_query($conn, $sql_semana);
    $usuarios_semana = sqlsrv_fetch_array($stmt, SQLSRV_FETCH_ASSOC)['total'];

    $sql_tipo = "
        SELECT tipo as tipo_usuario, COUNT(*) as total
        FROM Usuarios
        GROUP BY tipo
    ";
    $stmt = sqlsrv_query($conn, $sql_tipo);

    $usuarios_por_tipo = [];
    while ($row = sqlsrv_fetch_array($stmt, SQLSRV_FETCH_ASSOC)) {
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
    $stmt = sqlsrv_query($conn, $sql_actividad);

    $actividad = [];
    while ($row = sqlsrv_fetch_array($stmt, SQLSRV_FETCH_ASSOC)) {
        $actividad[] = $row;
    }

    // =========================
    // TOTAL REGISTROS
    // =========================
    $sql_count = "SELECT COUNT(*) as total FROM Usuarios";
    $stmt = sqlsrv_query($conn, $sql_count);
    $total_registros = sqlsrv_fetch_array($stmt, SQLSRV_FETCH_ASSOC)['total'];

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

    $params = [$offset, $limit];
    $stmt = sqlsrv_query($conn, $sql_usuarios, $params);

    $usuarios = [];
    while ($row = sqlsrv_fetch_array($stmt, SQLSRV_FETCH_ASSOC)) {
        if ($row['fecha_registro'] instanceof DateTime) {
            $row['fecha_registro'] = $row['fecha_registro']->format('Y-m-d H:i:s');
        }
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
    echo json_encode([
        "success" => false,
        "error" => $e->getMessage()
    ]);
}
?>