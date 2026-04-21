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

// Validar si la respuesta es JSON (error)
$jsonResponse = json_decode($response, true);
if ($jsonResponse && isset($jsonResponse['errors'])) {
    error_log("Remove.bg Error JSON - HTTP Code: $httpCode, Errors: " . json_encode($jsonResponse['errors']));
    echo json_encode([
        'error' => 'Remove.bg rechazó la imagen',
        'detalle' => $jsonResponse['errors'][0]['title'] ?? 'Error desconocido',
        'httpCode' => $httpCode
    ]);
    exit;
}

// Validar que sea PNG (primeros 4 bytes)
$pngSignature = substr($response, 0, 4);
if ($pngSignature !== "\x89PNG") {
    error_log("Remove.bg no devolvió PNG válido - HTTP Code: $httpCode, First bytes: " . bin2hex($pngSignature));
    echo json_encode([
        'error' => 'Remove.bg devolvió respuesta inválida',
        'detalle' => 'Primeros bytes: ' . bin2hex($pngSignature),
        'httpCode' => $httpCode
    ]);
    exit;
}

// Guardar PNG válido
if ($httpCode === 200 && strlen($response) > 100) {
    $fileName = "no-bg_" . time() . ".png";
    $filePath = $uploadDir . $fileName;

    file_put_contents($filePath, $response);

    // URL pública
    $publicUrl = "http://ai-print-studio.local/backend/uploads/" . $fileName;

    echo json_encode([
        'imagen_url' => $publicUrl
    ]);
} else {
    echo json_encode([
        'error' => 'Error al remover fondo',
        'httpCode' => $httpCode,
        'responseSize' => strlen($response)
    ]);
}