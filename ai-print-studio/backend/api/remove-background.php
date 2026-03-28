<?php
// ============================================
// remove-background.php
// ============================================

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// ----------------------
// CONFIG
// ----------------------
$apiKey = "EagYfmm4q6bBQh1V6CxAQhww"; // 🔥 Remove BG

$uploadDir = __DIR__ . "/../uploads/";

// Crear carpeta si no existe
if (!file_exists($uploadDir)) {
    mkdir($uploadDir, 0777, true);
}

// ----------------------
// VALIDAR INPUT
// ----------------------
if (!isset($_FILES['image'])) {
    echo json_encode(['error' => 'No se envió imagen']);
    exit;
}

$imageTmp = $_FILES['image']['tmp_name'];

// ----------------------
// LLAMADA A REMOVE.BG
// ----------------------
$ch = curl_init();

curl_setopt($ch, CURLOPT_URL, "https://api.remove.bg/v1.0/removebg");
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);

curl_setopt($ch, CURLOPT_POSTFIELDS, [
    'image_file' => new CURLFile($imageTmp),
    'size' => 'auto'
]);

curl_setopt($ch, CURLOPT_HTTPHEADER, [
    "X-Api-Key: $apiKey"
]);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

if (curl_errno($ch)) {
    echo json_encode(['error' => curl_error($ch)]);
    curl_close($ch);
    exit;
}

curl_close($ch);

// ----------------------
// MANEJO RESPUESTA
// ----------------------
if ($httpCode === 200) {
    $fileName = "no-bg_" . time() . ".png";
    $filePath = $uploadDir . $fileName;

    file_put_contents($filePath, $response);

    // URL pública (ajustar según tu server)
    $publicUrl = "http://localhost/ai-print-studio/backend/uploads/" . $fileName;

    echo json_encode([
        'imagen_url' => $publicUrl
    ]);
} else {
    echo json_encode([
        'error' => 'Error al remover fondo',
        'detalle' => $response
    ]);
}