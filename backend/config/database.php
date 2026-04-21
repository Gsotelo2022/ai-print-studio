<?php
// ============================================
// Conexión a SQL Server
// ============================================
// Este archivo devuelve una conexión PDO a SQL Server.
//
// FLUJO: Cada endpoint PHP incluye este archivo para
// obtener la conexión a la base de datos.
//
// REQUISITO: Tener instalada la extensión pdo_sqlsrv de PHP.
// Descarga: https://docs.microsoft.com/en-us/sql/connect/php/download-drivers-php-sql-server

function getDBConnection(): PDO {
    $server   = 'localhost';       // Dirección del servidor SQL Server
    $database = 'ai_print_studio'; // Nombre de la base de datos
    $username = 'sa';              // Usuario (cambiar en producción)
    $password = 'TU_PASSWORD';     // Contraseña (cambiar en producción)

    // DSN (Data Source Name) para SQL Server con PDO
    // Formato: sqlsrv:Server=HOST;Database=NOMBRE
    $dsn = "sqlsrv:Server={$server};Database={$database}";

    try {
        // Creamos la conexión PDO con opciones seguras:
        $pdo = new PDO($dsn, $username, $password, [
            // Lanza excepciones cuando hay errores SQL (no falla silenciosamente)
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,

            // Devuelve filas como arrays asociativos (más fácil de usar)
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        ]);

        return $pdo;

    } catch (PDOException $e) {
        // Si no puede conectar, devolvemos error JSON y cortamos ejecución
        http_response_code(500);
        echo json_encode([
            'success' => false,
            'error'   => 'Error de conexión a la base de datos'
        ]);
        // Registramos el error real en el log del servidor (no lo exponemos al usuario)
        error_log('DB Connection Error: ' . $e->getMessage());
        exit;
    }
}
