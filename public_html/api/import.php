<?php

header('Content-Type: application/json; charset=utf-8');

$config = require __DIR__ . '/config.php';

require __DIR__ . '/database.php';
require __DIR__ . '/functions.php';


// =========================
// API KEY
// =========================

$headers = getallheaders();

if (
    !isset($headers['X-API-Key']) ||
    $headers['X-API-Key'] !== $config['api_key']
) {

    http_response_code(401);

    echo json_encode([

        "success" => false,
        "message" => "API Key invalida."

    ]);

    exit;
}


// =========================
// JSON
// =========================

$json = file_get_contents("php://input");

$data = json_decode($json, true);


if (!$data) {

    http_response_code(400);

    echo json_encode([

        "success" => false,
        "message" => "JSON invalid."

    ]);

    exit;
}


// =========================
// INSERT
// =========================

$id = insertArticle($pdo, $data);


// =========================
// RESPONSE
// =========================

echo json_encode([

    "success" => true,
    "message" => "Articol salvat.",
    "id" => $id

], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);