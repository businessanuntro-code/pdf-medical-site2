<?php

require "../api/database.php";

$sql = "
SELECT
    id,
    titlu_ro,
    autori,
    created_at
FROM articole_stiintifice
ORDER BY id DESC
";

$articole = $pdo->query($sql)->fetchAll(PDO::FETCH_ASSOC);

?>

<!DOCTYPE html>
<html lang="ro">

<head>

<meta charset="utf-8">

<title>Articole</title>

<style>

body{

    font-family:Arial;
    width:900px;
    margin:auto;
    padding:40px;

}

.item{

    padding:20px;
    border-bottom:1px solid #ddd;

}

a{

    font-size:24px;
    text-decoration:none;

}

.autori{

    color:#666;
    margin-top:8px;

}

</style>

</head>

<body>

<h1>Articole</h1>

<?php foreach($articole as $articol): ?>

<div class="item">

<a href="articol.php?id=<?=$articol['id']?>">

<?=htmlspecialchars($articol['titlu_ro'])?>

</a>

<div class="autori">

<?=htmlspecialchars($articol['autori'])?>

</div>

</div>

<?php endforeach; ?>

</body>

</html>