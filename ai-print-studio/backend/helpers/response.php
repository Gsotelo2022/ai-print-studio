<?php
// ============================================
// Helper: Funciones para respuestas JSON
// ============================================
// Centraliza cómo tu API responde al frontend.
// Todos los endpoints usan estas funciones para ser consistentes.

// Configura los headers necesarios para respuestas JSON
// y para permitir peticiones desde el frontend (CORS)
function setupHeaders(): void {
    // Le dice al navegador que la respuesta es JSON
    header('Content-Type: application/json; charset=utf-8');

    // CORS: permite que el frontend (en otro puerto) haga peticiones
    // En producción, cambiar * por el dominio real del frontend
    header('Access-Control-Allow-Origin: *');
    header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
    header('Access-Control-Allow-Headers: Content-Type');

    // Si el navegador envía una petición OPTIONS (preflight CORS),
    // respondemos OK y cortamos
    if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
        http_response_code(200);
        exit;
    }
}

// Envía una respuesta exitosa al frontend
function jsonSuccess(array $data): void {
    echo json_encode([
        'success' => true,
        'data'    => $data,
    ]);
    exit;
}

// Envía una respuesta de error al frontend
function jsonError(string $message, int $statusCode = 400): void {
    http_response_code($statusCode);
    echo json_encode([
        'success' => false,
        'error'   => $message,
    ]);
    exit;
}

// Lee el cuerpo JSON de la petición del frontend
// El frontend envía datos como JSON en el body del fetch()
function getJsonInput(): array {
    $raw = file_get_contents('php://input');
    $data = json_decode($raw, true);

    if ($data === null) {
        jsonError('El cuerpo de la petición no es JSON válido');
    }

    return $data;
}

// Valida que los campos requeridos estén presentes en el input
function validateRequired(array $input, array $requiredFields): void {
    $missing = [];
    foreach ($requiredFields as $field) {
        if (!isset($input[$field]) || $input[$field] === '') {
            $missing[] = $field;
        }
    }

    if (!empty($missing)) {
        jsonError('Campos requeridos faltantes: ' . implode(', ', $missing));
    }
}
