<?php

require_once __DIR__ . '/../config/app.php';
require_once __DIR__ . '/../helpers/response.php';

setupHeaders();

// Solo POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    jsonError('Método no permitido. Usa POST.', 405);
}

// --- 1. Leer datos ---
$input = getJsonInput();
validateRequired($input, ['prompt']);

$prompt = "Diseño para estampado en remera, fondo limpio, estilo gráfico profesional: " . trim($input['prompt']);

// Validar prompt
if (strlen($prompt) < 3 || strlen($prompt) > 500) {
    jsonError('El prompt debe tener entre 3 y 500 caracteres');
}

// --- 2. Configuración ---
$config = require __DIR__ . '/../config/app.php';

$apiKey = $config['openai']['api_key'];
$apiUrl = $config['openai']['api_url'];

// --- 3. Llamada a OpenAI (DALL·E) ---
$ch = curl_init();

curl_setopt_array($ch, [
    CURLOPT_URL => $apiUrl,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST => true,
    CURLOPT_TIMEOUT => 60,
    CURLOPT_HTTPHEADER => [
        'Authorization: Bearer ' . $apiKey,
        'Content-Type: application/json',
    ],
    CURLOPT_POSTFIELDS => json_encode([
        'model' => 'gpt-image-1',
        'prompt' => $prompt,
        'size' => '1024x1024'
    ]),
]);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);

curl_close($ch);

// --- 4. Manejo de errores ---
if ($error) {
    error_log('OpenAI cURL error: ' . $error);
    jsonError('Error de conexión con OpenAI', 502);
}

if ($httpCode !== 200) {
    error_log('OpenAI HTTP ' . $httpCode . ': ' . $response);
    jsonError('Error en OpenAI (HTTP ' . $httpCode . ')', 502);
}

$result = json_decode($response, true);

if (!isset($result['data'][0]['b64_json'])) {
    error_log('Respuesta inválida de OpenAI: ' . $response);
    jsonError('No se pudo generar la imagen', 500);
}

// --- 5. Convertir base64 a imagen ---
$imageBase64 = $result['data'][0]['b64_json'];
$imageData = base64_decode($imageBase64);

// --- 6. Guardar archivo ---
$uploadsDir = $config['app']['uploads_dir'];

if (!is_dir($uploadsDir)) {
    mkdir($uploadsDir, 0755, true);
}

$filename = 'img_' . time() . '_' . bin2hex(random_bytes(4)) . '.png';
$filepath = $uploadsDir . $filename;

file_put_contents($filepath, $imageData);

// --- 7. URL pública ---
$imageUrl = $config['app']['uploads_url'] . $filename;

// --- 8. Respuesta ---
jsonSuccess([
    'imagen_url' => $imageUrl,
    'prompt' => $prompt
]);