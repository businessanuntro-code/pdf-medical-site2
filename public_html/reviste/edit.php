<?php

require "../api/database.php";

$id = intval($_GET["id"] ?? 0);


/* =====================================================
   STERGERE FISIER PRIN AJAX
   ===================================================== */

if (
    $_SERVER["REQUEST_METHOD"] === "POST" &&
    isset($_POST["delete_file"])
) {

    header("Content-Type: application/json; charset=utf-8");

    $fileName = basename($_POST["delete_file"]);

    /*
     * IMPORTANT:
     * upload.php salveaza fisierele in:
     *
     * __DIR__ . '/../upload/'
     */

    $uploadDir = __DIR__ . "/../upload/";

    $filePath = $uploadDir . $fileName;


    /*
     * Verificam ca folderul exista.
     */

    if (!is_dir($uploadDir)) {

        echo json_encode([
            "success" => false,
            "error" => "Folderul upload nu exista."
        ]);

        exit;
    }


    /*
     * Verificam ca fisierul exista.
     */

    if (!is_file($filePath)) {

        echo json_encode([
            "success" => false,
            "error" => "Fisierul nu exista."
        ]);

        exit;
    }


    /*
     * Verificare suplimentara de securitate.
     *
     * Nu permitem stergerea unui fisier
     * din afara folderului upload.
     */

    $realUploadDir = realpath($uploadDir);
    $realFilePath  = realpath($filePath);


    if (
        $realUploadDir === false ||
        $realFilePath === false ||
        strpos(
            $realFilePath,
            $realUploadDir . DIRECTORY_SEPARATOR
        ) !== 0
    ) {

        echo json_encode([
            "success" => false,
            "error" => "Fisier invalid."
        ]);

        exit;
    }


    /*
     * Stergem fisierul.
     */

    if (unlink($realFilePath)) {

        echo json_encode([
            "success" => true,
            "file" => $fileName
        ]);

        exit;

    }


    echo json_encode([
        "success" => false,
        "error" => "Fisierul nu a putut fi sters."
    ]);

    exit;
}


/* =====================================================
   ARTICOL
   ===================================================== */

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


/* =====================================================
   FISIERE UPLOADATE
   ===================================================== */

$uploadDir = __DIR__ . "/../upload/";

$uploadBaseUrl =
    "https://diaconu-daniel.ro/upload/";


$uploadedFiles = [];


if (is_dir($uploadDir)) {

    $files = scandir($uploadDir);


    if ($files !== false) {

        foreach ($files as $file) {

            /*
             * Ignoram . si ..
             */

            if (
                $file === "." ||
                $file === ".."
            ) {

                continue;

            }


            $filePath =
                $uploadDir . $file;


            /*
             * Afisam doar fisiere,
             * nu directoare.
             */

            if (!is_file($filePath)) {

                continue;

            }


            $uploadedFiles[] = [

                "name" =>
                    $file,

                "size" =>
                    filesize($filePath),

                "modified" =>
                    filemtime($filePath)

            ];

        }

    }

}


/* =====================================================
   SORTARE FISIERE DUPA NUME
   ===================================================== */

usort(
    $uploadedFiles,
    function ($a, $b) {

        return strcasecmp(
            $a["name"],
            $b["name"]
        );

    }
);


/* =====================================================
   DIMENSIUNE FISIER
   ===================================================== */

function formatFileSize($bytes)
{

    if ($bytes < 1024) {

        return $bytes . " B";

    }


    if ($bytes < 1024 * 1024) {

        return round(
            $bytes / 1024,
            1
        ) . " KB";

    }


    if ($bytes < 1024 * 1024 * 1024) {

        return round(
            $bytes / (1024 * 1024),
            1
        ) . " MB";

    }


    return round(
        $bytes / (1024 * 1024 * 1024),
        1
    ) . " GB";

}

?>

<!DOCTYPE html>

<html lang="ro">

<head>

<meta charset="UTF-8">

<title>Editare articol</title>


<style>


/* =====================================================
   PAGINA
   ===================================================== */

body{

    font-family:Arial;

    max-width:1200px;

    margin:auto;

    padding:30px;

}


/* =====================================================
   LABEL
   ===================================================== */

label{

    font-weight:bold;

    display:block;

    margin-top:20px;

}


/* =====================================================
   INPUT
   ===================================================== */

input[type=text],
input[type=date]{

    width:100%;

    padding:10px;

    font-size:16px;

    box-sizing:border-box;

}


/* =====================================================
   TEXTAREA
   ===================================================== */

textarea{

    width:100%;

    min-height:180px;

    padding:10px;

    font-size:15px;

    box-sizing:border-box;

}


#continut{

    min-height:700px;

    font-family:
        Consolas,
        Monaco,
        monospace;

    font-size:14px;

    line-height:1.5;

    background:#fafafa;

}


#continut_html{

    min-height:500px;

    font-family:
        Consolas,
        Monaco,
        monospace;

    font-size:14px;

    background:#fafafa;

}


/* =====================================================
   TOOLBAR
   ===================================================== */

.toolbar{

    margin-top:10px;

    margin-bottom:10px;

}


.toolbar button{

    padding:8px 14px;

    margin-right:5px;

    cursor:pointer;

    font-weight:bold;

    border:1px solid #999;

    background:#fff;

}


.toolbar button:hover{

    background:#eee;

}


/* =====================================================
   SAVE
   ===================================================== */

button.save{

    margin-top:30px;

    padding:15px 35px;

    font-size:16px;

    cursor:pointer;

}


/* =====================================================
   SECTIUNEA FISIERE
   ===================================================== */

.files-section{

    margin-top:30px;

    margin-bottom:30px;

    border:1px solid #ccc;

    background:#fafafa;

    padding:20px;

    border-radius:6px;

}


.files-header{

    display:flex;

    justify-content:space-between;

    align-items:center;

    margin-bottom:15px;

}


.files-header h2{

    margin:0;

    font-size:20px;

}


.files-refresh{

    padding:8px 14px;

    cursor:pointer;

    border:1px solid #999;

    background:#fff;

}


.files-refresh:hover{

    background:#eee;

}


/* =====================================================
   TABEL
   ===================================================== */

.files-table{

    width:100%;

    border-collapse:collapse;

    background:#fff;

}


/* =====================================================
   SCROLL LISTA FISIERE
   ===================================================== */

#filesTable{

    display:block;

    max-height:300px;

    overflow-y:auto;

}


/*
 * Pastreaza latimea tabelului
 */

#filesTable thead,
#filesTable tbody{

    width:100%;

}


/*
 * Capul tabelului ramane vizibil
 * cand derulam lista.
 */

#filesTable thead{

    position:sticky;

    top:0;

    z-index:2;

}


/*
 * Coloanele raman aliniate.
 */

#filesTable tr{

    display:table;

    width:100%;

    table-layout:fixed;

}

.files-table th{

    text-align:left;

    padding:10px;

    border-bottom:2px solid #ccc;

    background:#f0f0f0;

}


.files-table td{

    padding:10px;

    border-bottom:1px solid #ddd;

    vertical-align:middle;

}


.files-table tr:hover{

    background:#fafafa;

}


/* =====================================================
   NUME FISIER
   ===================================================== */

.file-name{

    font-weight:bold;

    word-break:break-all;

}


/* =====================================================
   ACTIUNI
   ===================================================== */

.file-actions{

    white-space:nowrap;

}


.file-actions a,
.file-actions button{

    display:inline-block;

    margin-right:5px;

    padding:7px 10px;

    border:1px solid #aaa;

    background:#fff;

    color:#000;

    text-decoration:none;

    cursor:pointer;

    font-size:13px;

}


.file-actions a:hover,
.file-actions button:hover{

    background:#eee;

}


.file-delete{

    color:#b00000 !important;

}


/* =====================================================
   FARA FISIERE
   ===================================================== */

.no-files{

    padding:20px;

    text-align:center;

    color:#666;

    background:#fff;

    border:1px dashed #ccc;

}


/* =====================================================
   MESAJ
   ===================================================== */

.file-message{

    margin-bottom:15px;

    padding:10px;

    border:1px solid #ccc;

    background:#fff;

}


/* =====================================================
   UPLOAD RESULT
   ===================================================== */

#uploadResult{

    margin-top:10px;

}


</style>

</head>


<body>


<h1>Editare articol</h1>


<!-- =====================================================
     FORMULAR PRINCIPAL DE EDITARE
     ===================================================== -->

<form
method="post"
action="save.php"
id="editForm"
>


<input
type="hidden"
name="id"
value="<?=$articol["id"]?>"
>


<label>Titlu RO</label>

<input
type="text"
name="titlu_ro"
value="<?=htmlspecialchars(
    $articol["titlu_ro"] ?? ""
)?>"
>


<label>Titlu EN</label>

<input
type="text"
name="titlu_en"
value="<?=htmlspecialchars(
    $articol["titlu_en"] ?? ""
)?>"
>


<label>Autori</label>

<textarea
name="autori"
><?=htmlspecialchars(
    $articol["autori"] ?? ""
)?></textarea>


<label>Data publicarii</label>

<input
type="date"
name="data_publicarii"
value="<?=htmlspecialchars(
    $articol["data_publicarii"] ?? ""
)?>"
>


<label>Primit</label>

<input
type="text"
name="primit"
value="<?=htmlspecialchars(
    preg_replace(
        '/^Primit:\s*/i',
        '',
        $articol["primit"] ?? ""
    )
)?>"
>


<label>Acceptat</label>

<input
type="text"
name="acceptat"
value="<?=htmlspecialchars(
    preg_replace(
        '/^Acceptat:\s*/i',
        '',
        $articol["acceptat"] ?? ""
    )
)?>"
>


<label>Editorial Group</label>

<input
type="text"
name="editorial_grup"
value="<?=htmlspecialchars(
    $articol["editorial_grup"] ?? ""
)?>"
>


<label>DOI</label>

<input
type="text"
name="doi"
value="<?=htmlspecialchars(
    $articol["doi"] ?? ""
)?>"
>


<label>Descarca PDF</label>

<input
type="text"
name="descarca_pdf"
value="<?=htmlspecialchars(
    $articol["descarca_pdf"] ?? ""
)?>"
placeholder="https://site.ro/document.pdf"
>


<label>Abstract</label>

<textarea
name="abstract"
><?=htmlspecialchars(
    $articol["abstract"] ?? ""
)?></textarea>


<label>Keywords</label>

<textarea
name="keywords"
><?=htmlspecialchars(
    $articol["keywords"] ?? ""
)?></textarea>


<label>Rezumat</label>

<textarea
name="rezumat"
><?=htmlspecialchars(
    $articol["rezumat"] ?? ""
)?></textarea>


<label>Cuvinte cheie</label>

<textarea
name="cuvinte_cheie"
><?=htmlspecialchars(
    $articol["cuvinte_cheie"] ?? ""
)?></textarea>


<!-- =====================================================
     CONTINUT ARTICOL
     ===================================================== -->

<label>Continut articol</label>


<div class="toolbar">


<button
type="button"
title="Bold - text îngroșat"
onmousedown="event.preventDefault()"
onclick="formatHTML('strong')"
>
B
</button>


<button
type="button"
title="Italic - text înclinat"
onmousedown="event.preventDefault()"
onclick="formatHTML('em')"
>
I
</button>


<button
type="button"
title="Underline - text subliniat"
onmousedown="event.preventDefault()"
onclick="formatHTML('u')"
>
U
</button>


<button
type="button"
title="Superscript - text ridicat"
onmousedown="event.preventDefault()"
onclick="formatHTML('sup')"
>
x²
</button>


<button
type="button"
title="Subscript - text coborât"
onmousedown="event.preventDefault()"
onclick="formatHTML('sub')"
>
x₂
</button>


<button
type="button"
title="Paragraf HTML"
onmousedown="event.preventDefault()"
onclick="formatHTML('p')"
>
P
</button>


<button
type="button"
id="uploadButton"
>
Upload
</button>


<input
type="file"
id="uploadFile"
style="display:none"
>


<div id="uploadResult"></div>


</div>


<textarea
id="continut"
name="continut"
><?=htmlspecialchars(
    $articol["continut"] ?? ""
)?></textarea>


<!-- =====================================================
     FISIERE UPLOADATE
     ===================================================== -->

<div
class="files-section"
id="filesSection"
>


<div class="files-header">


<h2>Fișiere server</h2>


<button
type="button"
class="files-refresh"
onclick="reloadFiles()"
>
Reîmprospătează lista
</button>


</div>


<div id="filesMessage"></div>


<?php if (count($uploadedFiles) === 0): ?>


<div
class="no-files"
id="noFilesMessage"
>

Nu există fișiere în folderul de upload.

</div>


<table
class="files-table"
id="filesTable"
style="display:none;"
>

<tbody id="filesTableBody"></tbody>

</table>


<?php else: ?>


<table
class="files-table"
id="filesTable"
>


<thead>

<tr>

<th>Fișier</th>

<th>Dimensiune</th>

<th>Acțiuni</th>

</tr>

</thead>


<tbody id="filesTableBody">


<?php foreach ($uploadedFiles as $file): ?>


<?php

$fileName =
    $file["name"];


$fileUrl =
    $uploadBaseUrl .
    rawurlencode($fileName);

?>


<tr
id="fileRow_<?=htmlspecialchars(
    md5($fileName)
)?>"
>


<td class="file-name">

<?=htmlspecialchars(
    $fileName
)?>

</td>


<td>

<?=formatFileSize(
    $file["size"]
)?>

</td>


<td class="file-actions">


<a
href="<?=htmlspecialchars(
    $fileUrl
)?>"
target="_blank"
rel="noopener"
>
Deschide
</a>


<button
type="button"
onclick='copyFileLink(
    <?=json_encode($fileUrl)?>
)'
>
Copiere link
</button>


<button
type="button"
class="file-delete"
onclick='deleteFile(
    <?=json_encode($fileName)?>,
    <?=json_encode(md5($fileName))?>
)'
>
Șterge
</button>


</td>


</tr>


<?php endforeach; ?>


</tbody>

</table>


<?php endif; ?>


</div>


<!-- =====================================================
     AUTOR CORESPONDENT
     ===================================================== -->

<label>Autor corespondent</label>

<textarea
name="autor_corespondent"
><?=htmlspecialchars(
    $articol["autor_corespondent"] ?? ""
)?></textarea>


<label>Conflict</label>

<textarea
name="conflict"
><?=htmlspecialchars(
    $articol["conflict"] ?? ""
)?></textarea>


<label>Suport</label>

<textarea
name="suport"
><?=htmlspecialchars(
    $articol["suport"] ?? ""
)?></textarea>


<label>Licenta CC BY</label>

<textarea
name="licenta_cc_by"
><?=htmlspecialchars(
    $articol["licenta_cc_by"] ?? ""
)?></textarea>


<label>Bibliografie</label>

<textarea
name="bibliografie"
><?=htmlspecialchars(
    $articol["bibliografie"] ?? ""
)?></textarea>


<!-- =====================================================
     SALVARE
     ===================================================== -->

<button
class="save"
type="submit"
>
Salvează modificările
</button>


</form>


<script>


/* =====================================================
   FORMATARE HTML
   ===================================================== */

function formatHTML(tag)
{

    let textarea =
        document.getElementById(
            "continut"
        );


    let scrollPosition =
        textarea.scrollTop;


    let start =
        textarea.selectionStart;


    let end =
        textarea.selectionEnd;


    let text =
        textarea.value.substring(
            start,
            end
        );


    if (text.length === 0) {

        return;

    }


    let before =
        textarea.value.substring(
            0,
            start
        );


    let after =
        textarea.value.substring(
            end
        );


    let replacement =
        "<" +
        tag +
        ">" +
        text +
        "</" +
        tag +
        ">";


    textarea.value =
        before +
        replacement +
        after;


    textarea.focus();


    textarea.selectionStart =
        start;


    textarea.selectionEnd =
        start +
        replacement.length;


    textarea.scrollTop =
        scrollPosition;

}


/* =====================================================
   UPLOAD
   ===================================================== */

document
.getElementById("uploadButton")
.addEventListener(
    "click",
    function()
    {

        console.log(
            "buton upload apasat"
        );


        document
        .getElementById("uploadFile")
        .click();

    }
);


document
.getElementById("uploadFile")
.addEventListener(
    "change",
    function()
    {

        console.log(
            "fisier ales"
        );


        uploadFile(
            this
        );

    }
);


function uploadFile(input)
{

    let file =
        input.files[0];


    if (!file) {

        alert(
            "Nu ai selectat niciun fișier."
        );

        return;

    }


    let formData =
        new FormData();


    formData.append(
        "file",
        file
    );


    fetch(
        "../api/upload.php",
        {
            method: "POST",
            body: formData
        }
    )


    .then(
        response =>
            response.json()
    )


    .then(
        data =>
        {

            console.log(data);


            if (data.success) {


                document
                .getElementById(
                    "uploadResult"
                )
                .innerHTML = `

                    <input
                    id="uploadLink"
                    type="text"
                    value="${data.url}"
                    readonly
                    style="width:80%;padding:8px;">

                    <button
                    type="button"
                    onclick="copyLink()">
                    Copiere link
                    </button>

                    <div
                    style="margin-top:8px;">
                    Fișier încărcat cu succes.
                    </div>

                `;


                /*
                 * Reincarcam lista
                 * dupa upload.
                 */

               

            }


            else {

                alert(
                    data.error ||
                    "Upload eșuat."
                );

            }

        }
    )


    .catch(
        error =>
        {

            console.log(error);


            alert(
                "Eroare upload"
            );

        }
    );

}


/* =====================================================
   COPIERE LINK DUPA UPLOAD
   ===================================================== */

function copyLink()
{

    let input =
        document.getElementById(
            "uploadLink"
        );


    if (!input) {

        alert(
            "Nu exista link de copiat"
        );


        return;

    }


    copyTextToClipboard(
        input.value
    );

}


/* =====================================================
   COPIERE LINK FISIER
   ===================================================== */

function copyFileLink(fileUrl)
{

    copyTextToClipboard(
        fileUrl
    );

}


/* =====================================================
   COPIERE GENERICA
   ===================================================== */

function copyTextToClipboard(text)
{

    if (
        navigator.clipboard &&
        window.isSecureContext
    ) {

        navigator
        .clipboard
        .writeText(text)

        .then(
            function()
            {

                alert(
                    "Link copiat"
                );

            }
        )

        .catch(
            function()
            {

                fallbackCopy(
                    text
                );

            }
        );

    }

    else {

        fallbackCopy(
            text
        );

    }

}


/* =====================================================
   FALLBACK COPY
   ===================================================== */

function fallbackCopy(text)
{

    let textarea =
        document.createElement(
            "textarea"
        );


    textarea.value =
        text;


    textarea.style.position =
        "fixed";


    textarea.style.left =
        "-9999px";


    document
    .body
    .appendChild(
        textarea
    );


    textarea.select();


    try {

        document.execCommand(
            "copy"
        );


        alert(
            "Link copiat"
        );

    }

    catch (error) {

        alert(
            "Nu s-a putut copia link-ul"
        );

    }


    document
    .body
    .removeChild(
        textarea
    );

}


/* =====================================================
   STERGERE FISIER
   ===================================================== */

function deleteFile(
    fileName,
    rowId
)
{

    let confirmed =
        confirm(
            "Sigur vrei sa stergi fisierul:\n\n" +
            fileName +
            "\n\nAceasta actiune nu poate fi anulata."
        );


    if (!confirmed) {

        return;

    }


    let formData =
        new FormData();


    formData.append(
        "delete_file",
        fileName
    );


    fetch(
        window.location.href,
        {
            method: "POST",
            body: formData
        }
    )


    .then(
        response =>
            response.json()
    )


    .then(
        data =>
        {

            console.log(
                "delete response:",
                data
            );


            if (data.success) {


                /*
                 * Eliminam imediat randul
                 * din tabel.
                 */

                let row =
                    document.getElementById(
                        "fileRow_" + rowId
                    );


                if (row) {

                    row.remove();

                }


                /*
                 * Daca nu mai exista
                 * niciun rand, afisam mesajul.
                 */

                let tbody =
                    document.getElementById(
                        "filesTableBody"
                    );


                if (
                    tbody &&
                    tbody.children.length === 0
                ) {

                    let table =
                        document.getElementById(
                            "filesTable"
                        );


                    if (table) {

                        table.style.display =
                            "none";

                    }


                    let noFiles =
                        document.getElementById(
                            "noFilesMessage"
                        );


                    if (!noFiles) {

                        noFiles =
                            document.createElement(
                                "div"
                            );


                        noFiles.id =
                            "noFilesMessage";


                        noFiles.className =
                            "no-files";


                        noFiles.innerText =
                            "Nu există fișiere în folderul de upload.";


                        document
                        .getElementById(
                            "filesSection"
                        )
                        .appendChild(
                            noFiles
                        );

                    }

                }


                showFileMessage(
                    "Fișierul a fost șters cu succes."
                );

            }


            else {

                alert(
                    data.error ||
                    "Fișierul nu a putut fi șters."
                );

            }

        }
    )


    .catch(
    error =>
    {
        console.error(error);
    }
);

}


/* =====================================================
   MESAJ FISIER
   ===================================================== */

function showFileMessage(message)
{

    let container =
        document.getElementById(
            "filesMessage"
        );


    if (!container) {

        return;

    }


    container.innerHTML = `

        <div class="file-message">
            ${escapeHtml(message)}
        </div>

    `;


    setTimeout(
        function()
        {

            container.innerHTML = "";

        },
        3000
    );

}


/* =====================================================
   ESCAPE HTML
   ===================================================== */

function escapeHtml(text)
{

    let div =
        document.createElement(
            "div"
        );


    div.textContent =
        text;


    return div.innerHTML;

}


/* =====================================================
   REINCARCARE LISTA
   ===================================================== */

function reloadFiles()
{

    /*
     * Pentru moment reincarcam pagina.
     *
     * Important:
     * nu folosim submit-ul formularului principal.
     */

    window.location.reload();

}


</script>


</body>

</html>

