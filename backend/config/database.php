<?php
// ============================================
// Conexión a SQL Server (ODBC)
// ============================================
// Conexión a PrendeteRock usando DSN ODBC

function getDBConnection(): PDO {
    // Intentar con ODBC Driver 17 for SQL Server (moderno)
    // Si falla, usaremos named pipes
    
    $server   = '.';                  // Servidor local
    $database = 'PrendeteRock';       // BD existente
    $username = '';                   // Windows Auth - usuario actual
    $password = '';                   // Windows Auth - no necesita password

    try {
        // Intentar con ODBC Driver 17
        $dsn = "odbc:Driver={ODBC Driver 17 for SQL Server};Server={$server};Database={$database};Trusted_Connection=yes;";
        
        $pdo = new PDO($dsn, $username, $password, [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        ]);

        return $pdo;

    } catch (PDOException $e1) {
        // Si falla, intentar con ODBC Driver 13
        try {
            $dsn = "odbc:Driver={ODBC Driver 13 for SQL Server};Server={$server};Database={$database};Trusted_Connection=yes;";
            
            $pdo = new PDO($dsn, $username, $password, [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            ]);

            return $pdo;

        } catch (PDOException $e2) {
            // Si falla, intentar con SQL Native Client
            try {
                $dsn = "odbc:Driver={SQL Server Native Client 11.0};Server={$server};Database={$database};Trusted_Connection=yes;";
                
                $pdo = new PDO($dsn, $username, $password, [
                    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                ]);

                return $pdo;

            } catch (PDOException $e3) {
                // Si todos fallan, devolver error detallado
                http_response_code(500);
                echo json_encode([
                    'success' => false,
                    'error'   => 'No se pudo conectar a SQL Server. Drivers intentados: ODBC 17, ODBC 13, SQL Native Client 11.0',
                    'details' => 'Error: ' . $e3->getMessage()
                ]);
                error_log('DB Connection Errors:');
                error_log('ODBC 17: ' . $e1->getMessage());
                error_log('ODBC 13: ' . $e2->getMessage());
                error_log('SQL Native Client: ' . $e3->getMessage());
                exit;
            }
        }
    }
}
