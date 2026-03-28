<?php
// ============================================
// Configuración general de la aplicación
// ============================================
// Aquí centralizamos todas las claves y URLs de APIs externas.
// EN PRODUCCIÓN: estas claves deben ir en variables de entorno,
// nunca directamente en el código ni en el repositorio.

return [
    // DALL-E 3 de OpenAI
    'openai' => [
        'api_key' => 'TU_OPENAI_API_KEY',
        'api_url' => 'https://api.openai.com/v1/images/generations',
    ],

    // --- MercadoPago ---
    // Obtener en: https://www.mercadopago.com.ar/developers
    'mercadopago' => [
        'access_token' => 'TU_MERCADOPAGO_ACCESS_TOKEN',
        'api_url'      => 'https://api.mercadopago.com/checkout/preferences',
    ],

    // --- URLs de la aplicación ---
    'app' => [
        'base_url'    => 'http://localhost:8080',
        'uploads_dir' => __DIR__ . '/../uploads/',
        'uploads_url' => 'http://localhost:8080/uploads/',
    ],

    // --- Productos y precios ---
    // Catálogo simple de productos con sus precios base
    'productos' => [
        'camiseta'  => ['nombre' => 'Camiseta',  'precio' => 12000],
        'taza'      => ['nombre' => 'Taza',      'precio' => 8000],
        'sudadera'  => ['nombre' => 'Sudadera',  'precio' => 18000],
        'cojin'     => ['nombre' => 'Cojín',     'precio' => 10000],
        'mochila'   => ['nombre' => 'Mochila',   'precio' => 15000],
        'gorra'     => ['nombre' => 'Gorra',     'precio' => 9000],
    ],
];
