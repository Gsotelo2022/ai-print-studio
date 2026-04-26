<?php
// 🔥 CORS
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Headers: Content-Type");
header("Access-Control-Allow-Methods: POST, OPTIONS");
header("Content-Type: application/json");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// 🔥 DEBUG
ini_set('display_errors', 1);
error_reporting(E_ALL);

require __DIR__ . '/../vendor/autoload.php';

use MercadoPago\Client\Preference\PreferenceClient;
use MercadoPago\MercadoPagoConfig;

// 🔐 TOKEN (poné el tuyo de TEST)
MercadoPagoConfig::setAccessToken('TEST-1492177583757030-032120-4e536f078e8cf2e2f51b871b89dea0c7-193328483');

// Leer datos del frontend
$data = json_decode(file_get_contents('php://input'), true);

if (!$data) {
    echo json_encode(["error" => "No se recibieron datos"]);
    exit;
}

try {
    // ✅ Crear cliente
    $client = new PreferenceClient();

    // ✅ Crear preferencia
    $preference = $client->create([
        "items" => [
            [
                "title" => $data['producto'] ?? 'Producto',
                "quantity" => (int)($data['cantidad'] ?? 1),
                "unit_price" => (float)($data['precio'] ?? 1000),
                "currency_id" => "ARS"
            ]
        ],
        "payer" => [
            "email" => "test_user_123456@testuser.com"
        ],
        "back_urls" => [
            "success" => "http://127.0.0.1:5173/success",
            "failure" => "http://127.0.0.1:5173/failure",
            "pending" => "http://127.0.0.1:5173/pending"
        ]
        // 🚫 SIN auto_return por ahora
    ]);

    // ✅ Respuesta OK
    echo json_encode([
        "success" => true,
        "sandbox_url" => $preference->init_point,
        "payment_url" => $preference->init_point,
        "init_point" => $preference->init_point
    ]);

} catch (\MercadoPago\Exceptions\MPApiException $e) {

    echo json_encode([
        "error" => $e->getMessage(),
        "status" => $e->getApiResponse()->getStatusCode(),
        "response" => $e->getApiResponse()->getContent()
    ]);

} catch (Exception $e) {

    echo json_encode([
        "error" => $e->getMessage()
    ]);
}