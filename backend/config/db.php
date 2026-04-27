<?php
// config/db.php
// Conexión reusable a SQL Server usando sqlsrv

declare(strict_types=1);

// Configuración reutilizable de la conexión
return (function () {
    // Ajusta estos valores según tu entorno local
    $config = [
        'server'   => 'localhost\\SQLEXPRESS', // doble backslash en literal PHP
        'database' => 'PrendeteRock',
        'username' => '', // si usás autenticación SQL Server pones usuario
        'password' => '', // y contraseña aquí; si usás autenticación integrada, dejá vacíos
        // Opciones para sqlsrv
        'options'  => [
            'CharacterSet' => 'UTF-8',
            // Opciones adicionales pueden ir aquí
        ],
    ];

    // Función para obtener la conexión
    $getConnection = function () use ($config) {
        // Construir el array de parámetros para sqlsrv_connect
        $serverName = $config['server'];
        $connectionInfo = [
            'Database' => $config['database'],
        ];

        // Si se pasan credenciales, agregarlas
        if (!empty($config['username'])) {
            $connectionInfo['UID'] = $config['username'];
            $connectionInfo['PWD'] = $config['password'];
        }

        // Mezclar opciones de CharacterSet
        if (isset($config['options']) && is_array($config['options'])) {
            $connectionInfo = array_merge($connectionInfo, $config['options']);
        }

        // Intentar conectar
        $conn = @sqlsrv_connect($serverName, $connectionInfo);
        if ($conn === false) {
            $errors = sqlsrv_errors(SQLSRV_ERR_ERRORS);
            $msg = 'Error al conectar a la base de datos.';
            if ($errors) {
                $msg .= ' Detalle: ' . json_encode($errors);
            }
            throw new RuntimeException($msg);
        }

        return $conn;
    };
    return [
        'getConnection' => $getConnection,
        'config' => $config,
    ];
})();
