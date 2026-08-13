<?php

require "../api/database.php";


$id = intval($_POST["id"]);



$sql = "

UPDATE articole_stiintifice

SET

titlu_ro=?,
titlu_en=?,
autori=?,
data_publicarii=?,
primit=?,
acceptat=?,
editorial_grup=?,
doi=?,
descarca_pdf=?,

abstract=?,
keywords=?,

rezumat=?,
cuvinte_cheie=?,

continut=?,

autor_corespondent=?,
conflict=?,
suport=?,
licenta_cc_by=?,
bibliografie=?

WHERE id=?

";



$stmt = $pdo->prepare($sql);



$stmt->execute([


    $_POST["titlu_ro"] ?? "",
    $_POST["titlu_en"] ?? "",
    $_POST["autori"] ?? "",

    $_POST["data_publicarii"] ?? "",
    $_POST["primit"] ?? "",
    $_POST["acceptat"] ?? "",
    $_POST["editorial_grup"] ?? "",
    $_POST["doi"] ?? "",
    $_POST["descarca_pdf"] ?? "",


    $_POST["abstract"] ?? "",
    $_POST["keywords"] ?? "",


    $_POST["rezumat"] ?? "",
    $_POST["cuvinte_cheie"] ?? "",


    $_POST["continut"] ?? "",


    $_POST["autor_corespondent"] ?? "",
    $_POST["conflict"] ?? "",
    $_POST["suport"] ?? "",
    $_POST["licenta_cc_by"] ?? "",
    $_POST["bibliografie"] ?? "",


    $id

]);




// =======================================
// REGENERARE HTML CU BUILDER (PYTHON)
// =======================================


$payload = [


    "id" => $id,


    "titlu_ro" => $_POST["titlu_ro"] ?? "",

    "titlu_en" => $_POST["titlu_en"] ?? "",

    "autori" => $_POST["autori"] ?? "",


    "data_publicarii" => $_POST["data_publicarii"] ?? "",

    "primit" => $_POST["primit"] ?? "",

    "acceptat" => $_POST["acceptat"] ?? "",

    "editorial_grup" => $_POST["editorial_grup"] ?? "",

    "doi" => $_POST["doi"] ?? "",

    "descarca_pdf" => $_POST["descarca_pdf"] ?? "",


    "abstract" => $_POST["abstract"] ?? "",

    "keywords" => $_POST["keywords"] ?? "",


    "rezumat" => $_POST["rezumat"] ?? "",

    "cuvinte_cheie" => $_POST["cuvinte_cheie"] ?? "",


    "continut" => $_POST["continut"] ?? "",


    "autor_corespondent" => $_POST["autor_corespondent"] ?? "",

    "conflict" => $_POST["conflict"] ?? "",

    "suport" => $_POST["suport"] ?? "",

    "licenta_cc_by" => $_POST["licenta_cc_by"] ?? "",

    "bibliografie" => $_POST["bibliografie"] ?? ""

];




$ch = curl_init("https://pdf-medical-site2.onrender.com/regenerate");


curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

curl_setopt($ch, CURLOPT_POST, true);


curl_setopt($ch, CURLOPT_HTTPHEADER, [

    "Content-Type: application/json"

]);


curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));



$response = curl_exec($ch);



curl_close($ch);



$result = json_decode($response, true);




if (!empty($result["success"])) {


    $stmt = $pdo->prepare("

        UPDATE articole_stiintifice

        SET continut_html=?

        WHERE id=?

    ");



    $stmt->execute([


        $result["continut_html"],

        $id

    ]);

}



header("Location: articol.php?id=".$id);

exit;
