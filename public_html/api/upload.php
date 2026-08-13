<?php

ini_set('display_errors', 1);
error_reporting(E_ALL);

header('Content-Type: application/json');

$uploadDir = __DIR__ . '/../upload/';

if (!is_dir($uploadDir)) {
    mkdir($uploadDir, 0777, true);
}

if (!isset($_FILES['file'])) {
    echo json_encode([
        'success' => false,
        'error' => 'Nu exista fisier'
    ]);
    exit;
}

$file = $_FILES['file'];

if ($file['error'] != UPLOAD_ERR_OK) {
    echo json_encode([
        'success' => false,
        'error' => 'Cod eroare upload: ' . $file['error']
    ]);
    exit;
}

$ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));

$allowed = [
    'jpg',
    'jpeg',
    'png',
    'gif',
    'webp',
    'pdf'
];

if (!in_array($ext, $allowed)) {
    echo json_encode([
        'success' => false,
        'error' => 'Extensie nepermisa'
    ]);
    exit;
}

$newName = uniqid() . "." . $ext;

$destination = $uploadDir . $newName;

if (!move_uploaded_file($file['tmp_name'], $destination)) {
    echo json_encode([
        'success' => false,
        'error' => 'Nu pot salva fisierul'
    ]);
    exit;
}

$url = "https://diaconu-daniel.ro/upload/" . $newName;

echo json_encode([
    'success' => true,
    'url' => $url
]);