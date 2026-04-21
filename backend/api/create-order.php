<?php
// ============================================
// POST /api/create-order.php
// ============================================
// FLUJO:
// 1. El frontend envía los datos del pedido (producto, talle, color, etc.)
// 2. Validamos los datos
// 3. Calculamos el precio según el producto
// 4. Insertamos en la tabla "pedidos" de SQL Server
// 5. Devolvemos el ID del pedido al frontend
//
// Frontend (Vue) → fetch POST → create-order.php → INSERT SQL → SQL Server
//                ← JSON { order_id, precio_total } ←

require_once __DIR__ . '/../config/app.php';
require_once __DIR__ . '/../config/database.php';
require_once __DIR__ . '/../helpers/response.php';

setupHeaders();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    jsonError('Método no permitido. Usa POST.', 405);
}

// --- 1. Leer datos del frontend ---
$input = getJsonInput();
validateRequired($input, ['producto', 'cantidad', 'prompt', 'imagen_url']);

$producto  = trim($input['producto']);
$talle     = isset($input['talle']) ? trim($input['talle']) : null;
$color     = isset($input['color']) ? trim($input['color']) : null;
$cantidad  = (int)$input['cantidad'];
$prompt    = trim($input['prompt']);
$imagenUrl = trim($input['imagen_url']);

// --- 2. Validar datos ---
$config   = require __DIR__ . '/../config/app.php';
$catalogo = $config['productos'];

// ¿El producto existe en nuestro catálogo?
if (!isset($catalogo[$producto])) {
    jsonError('Producto no válido: ' . $producto);
}

// ¿La cantidad es válida?
if ($cantidad < 1 || $cantidad > 100) {
    jsonError('La cantidad debe ser entre 1 y 100');
}

// Validar talle si el producto lo requiere
$productoConTalle = ['camiseta', 'sudadera'];
$tallesValidos = ['S', 'M', 'L', 'XL', 'XXL'];
if (in_array($producto, $productoConTalle)) {
    if (!$talle || !in_array(strtoupper($talle), $tallesValidos)) {
        jsonError('Talle no válido para ' . $producto . '. Opciones: ' . implode(', ', $tallesValidos));
    }
    $talle = strtoupper($talle);
}

// --- 3. Calcular precio ---
$precioUnitario = $catalogo[$producto]['precio'];
$precioTotal = $precioUnitario * $cantidad;

// --- 4. Insertar en la base de datos ---
// Usamos prepared statements (consultas preparadas) para prevenir SQL injection.
// Los ? son placeholders que PDO reemplaza de forma segura.

$pdo = getDBConnection();

$sql = "INSERT INTO pedidos (producto, talle, color, precio, cantidad, prompt, imagen_url, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pendiente')";

$stmt = $pdo->prepare($sql);
$stmt->execute([
    $producto,
    $talle,
    $color,
    $precioUnitario,
    $cantidad,
    $prompt,
    $imagenUrl,
]);

// Obtener el ID del pedido recién creado
$orderId = $pdo->lastInsertId();

// --- 5. Responder al frontend ---
jsonSuccess([
    'order_id'       => (int)$orderId,
    'producto'       => $catalogo[$producto]['nombre'],
    'precio_unitario'=> $precioUnitario,
    'cantidad'       => $cantidad,
    'precio_total'   => $precioTotal,
]);
