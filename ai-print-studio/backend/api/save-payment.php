<?php

header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json");

// Leer datos
$data = json_decode(file_get_contents("php://input"), true);

if (!$data) {
    echo json_encode(["error" => "Sin datos"]);
    exit;
}

// Simular guardado (por ahora en archivo)
file_put_contents(
    __DIR__ . "/pagos.txt",
    json_encode($data) . PHP_EOL,
    FILE_APPEND
);

echo json_encode([
    "message" => "Pago guardado correctamente"
]);