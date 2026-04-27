<?php
// ============================================
// CONFIGURACIÓN ÚNICA DE BASE DE DATOS
// ============================================
// Conexión unificada a SQL Server usando PDO
// Usada por TODOS los endpoints del backend PHP

function getDBConnection(): PDO {
    // Configuración única - SQL Server SQLEXPRESS01
    $server   = '.\SQLEXPRESS01';     // Instancia activa verificada
    $database = 'PrendeteRock';       // Base de datos del proyecto
    $username = '';                   // Windows Authentication
    $password = '';                   // Windows Authentication

    try {
        // Intentar con ODBC Driver 17 (recomendado)
        $dsn = "odbc:Driver={ODBC Driver 17 for SQL Server};Server={$server};Database={$database};Trusted_Connection=yes;TrustServerCertificate=yes;";
        
        $pdo = new PDO($dsn, $username, $password, [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_TIMEOUT => 5,
        ]);

        return $pdo;

    } catch (PDOException $e1) {
        // Fallback: ODBC Driver 13
        try {
            $dsn = "odbc:Driver={ODBC Driver 13 for SQL Server};Server={$server};Database={$database};Trusted_Connection=yes;TrustServerCertificate=yes;";
            
            $pdo = new PDO($dsn, $username, $password, [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_TIMEOUT => 5,
            ]);

            return $pdo;

        } catch (PDOException $e2) {
            // Fallback final: SQL Native Client
            try {
                $dsn = "odbc:Driver={SQL Server Native Client 11.0};Server={$server};Database={$database};Trusted_Connection=yes;";
                
                $pdo = new PDO($dsn, $username, $password, [
                    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                    PDO::ATTR_TIMEOUT => 5,
                ]);

                return $pdo;

            } catch (PDOException $e3) {
                // Si todos fallan, lanzar error descriptivo
                error_log('=== ERROR DE CONEXIÓN A BASE DE DATOS ===');
                error_log('Servidor intentado: ' . $server);
                error_log('Base de datos: ' . $database);
                error_log('ODBC Driver 17: ' . $e1->getMessage());
                error_log('ODBC Driver 13: ' . $e2->getMessage());
                error_log('SQL Native Client: ' . $e3->getMessage());
                
                throw new RuntimeException(
                    'No se pudo conectar a SQL Server. ' .
                    'Verifica que el servidor ' . $server . ' esté corriendo y que ' .
                    'la base de datos ' . $database . ' exista. ' .
                    'Detalles: ' . $e3->getMessage()
                );
            }
        }
    }
}
