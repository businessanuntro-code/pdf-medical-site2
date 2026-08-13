<?php

require "../api/database.php";

$id = intval($_GET["id"]);

$stmt = $pdo->prepare("
SELECT *
FROM articole_stiintifice
WHERE id=?
");

$stmt->execute([$id]);

$articol = $stmt->fetch(PDO::FETCH_ASSOC);

if (!$articol) {

    die("Articol inexistent");

}

?>

<div style="padding:20px; background:#f5f5f5; border-bottom:1px solid #ddd;">

    <a href="https://diaconu-daniel.ro/reviste/articole.php">← Înapoi la articole</a>

    &nbsp;&nbsp;&nbsp;

   <a href="edit.php?id=<?php echo $id; ?>">✏️ Editează articolul</a>

</div>

<?php

echo $articol["continut_html"];

?>