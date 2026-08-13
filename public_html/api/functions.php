<?php

// =========================
// INSERT ARTICOL STIINTIFIC
// =========================

function insertArticle($pdo, $data)
{

    $sql = "
        INSERT INTO articole_stiintifice
        (
            titlu_ro,
            titlu_en,
            autori,
            primit,
            acceptat,
            abstract,
            keywords,
            rezumat,
            cuvinte_cheie,
            continut,
            continut_html,
            autor_corespondent,
            conflict,
            suport,
            licenta_cc_by,
            bibliografie
        )
        VALUES
        (
            :titlu_ro,
            :titlu_en,
            :autori,
            :primit,
            :acceptat,
            :abstract,
            :keywords,
            :rezumat,
            :cuvinte_cheie,
            :continut,
            :continut_html,
            :autor_corespondent,
            :conflict,
            :suport,
            :licenta_cc_by,
            :bibliografie
        )
    ";

    $stmt = $pdo->prepare($sql);

    $stmt->execute([

        ':titlu_ro'            => $data['titlu'] ?? null,

        ':titlu_en'            => $data['english_title'] ?? null,

        ':autori'              => $data['autor'] ?? null,

        ':primit'              => $data['primit'] ?? null,

        ':acceptat'            => $data['acceptat'] ?? null,

        ':abstract'            => $data['abstract'] ?? null,

        ':keywords'            => $data['keywords_eng'] ?? null,

        ':rezumat'             => $data['rezumat'] ?? null,

        ':cuvinte_cheie'       => $data['keywords_rom'] ?? null,

        ':continut'            => $data['continut_articol'] ?? null,

        ':continut_html'       => $data['continut_html'] ?? null,

        ':autor_corespondent'  => $data['corespondent'] ?? null,

        ':conflict'            => $data['conflict'] ?? null,

        ':suport'              => $data['financial_support'] ?? null,

        ':licenta_cc_by'       => $data['cc_by'] ?? null,

        ':bibliografie'        => $data['bibliografie'] ?? null

    ]);

    return $pdo->lastInsertId();

}