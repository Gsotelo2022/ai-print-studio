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
try {
    $pdo = getDBConnection();

    // Usar sintaxis SQL Server para obtener el ID del registro insertado
    $sql = "INSERT INTO Pedidos 
            (producto, talle, color, precio, cantidad, prompt, imagen_url, posicion_x, posicion_y, zoom, estado, fecha_creacion)
            OUTPUT INSERTED.id_pedido
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pendiente', GETDATE())";

    $stmt = $pdo->prepare($sql);
    $stmt->execute([
        $producto,
        $talle,
        $color,
        $precioUnitario,
        $cantidad,
        $prompt,
        $imagenUrl,
        isset($input['posicion_x']) ? (int)$input['posicion_x'] : 0,
        isset($input['posicion_y']) ? (int)$input['posicion_y'] : 0,
        isset($input['zoom']) ? (float)$input['zoom'] : 1.0,
    ]);

    // Obtener el ID del pedido recién creado desde la salida de OUTPUT
    $result = $stmt->fetch();
    $orderId = $result['id_pedido'] ?? null;
    
    if (!$orderId) {
        throw new Error('No se obtuvo ID del pedido');
    }

    // --- 5. Responder al frontend ---
    jsonSuccess([
        'order_id'       => (int)$orderId,
        'producto'       => $catalogo[$producto]['nombre'],
        'precio_unitario'=> $precioUnitario,
        'cantidad'       => $cantidad,
        'precio_total'   => $precioTotal,
    ]);

} catch (Exception $e) {
    error_log('Error creando pedido: ' . $e->getMessage());
    jsonError('Error al crear el pedido: ' . $e->getMessage());
}
