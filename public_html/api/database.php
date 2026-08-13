<?php

$config = require __DIR__ . '/config.php';

try {

    $dsn = "mysql:host={$config['host']};dbname={$config['database']};charset={$config['charset']}";

    $pdo = new PDO(
        $dsn,
        $config['username'],
        $config['password'],
        [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false
        ]
    );

} catch (PDOException $e) {

    http_response_code(500);

    echo json_encode([
        "success" => false,
        "message" => "Conexiune MySQL esuata.",
        "error" => $e->getMessage()
    ]);

    exit;
}