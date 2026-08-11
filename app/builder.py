
# =========================================================
# builder.py
# =========================================================

import re


# =========================================================
# =========================================================
# ARTICOLE ȘTIINȚIFICE
# FUNCȚII GENERALE
# =========================================================


def linkify(text):

    if not text:
        return ""

    protected = []

    def protect(match):

        protected.append(
            match.group(0)
        )

        return f"___HTML_{len(protected)-1}___"

    text = re.sub(
        r"<[^>]+>",
        protect,
        text
    )

    text = re.sub(
        r'(https?://[^\s]+|www\.[^\s]+)',
        lambda m:
            f'<a href="{"https://"+m.group(0) if m.group(0).startswith("www.") else m.group(0)}" target="_blank">{m.group(0)}</a>',
        text
    )

    for i, tag in enumerate(protected):

        text = text.replace(
            f"___HTML_{i}___",
            tag
        )

    return text


# =========================================================
# REFERINȚE ÎN PARANTEZE
# ARTICOLE ȘTIINȚIFICE
# =========================================================


def superscript_refs(text):

    if not text:
        return ""

    def convert(match):

        return f"<sup>{match.group(0)}</sup>"

    return re.sub(
        r'\(\d+(?:\s*,\s*\d+)*\)',
        convert,
        text
    )


# =========================================================
# AUTORI
# ARTICOLE ȘTIINȚIFICE
# =========================================================


def superscript_author_refs(text):

    if not text:
        return ""

    return re.sub(
        r'(?<=[A-Za-zĂÂÎȘȚăâîșț\-])(\d+(?:,\d+)*)',
        r'<sup>\1</sup>',
        text
    )


# =========================================================
# SIMBOLURI
# =========================================================


def superscript_symbols(text):

    if not text:
        return ""

    return (
        text
        .replace(
            "™",
            "<sup>™</sup>"
        )
        .replace(
            "®",
            "<sup>®</sup>"
        )
    )


# =========================================================
# IMAGINI
# =========================================================


def render_image(url):

    return (
        f'<figure class="img-figure">'
        f'<img src="{url}" class="article-image"/>'
        f'</figure>'
    )


# =========================================================
# =========================================================
# ARTICOLE ȘTIINȚIFICE
# FORMAT CONTENT
# =========================================================
# NU MODIFICĂM ACEASTĂ SECȚIUNE.
# =========================================================


def format_content(text):

    if not text:
        return ""

    # -----------------------------------------------------
    # ELIMINARE TAGURI XML GENERALE
    # -----------------------------------------------------

    text = re.sub(
        r"</?(ContinutArticol|continut_articol|body)[^>]*>",
        "",
        text,
        flags=re.I
    )

    # -----------------------------------------------------
    # ELIMINARE TABELE
    # -----------------------------------------------------

    text = re.sub(
        r"<table.*?</table>",
        "",
        text,
        flags=re.I | re.S
    )

    # -----------------------------------------------------
    # ELIMINARE FIGURI
    # -----------------------------------------------------

    text = re.sub(
        r"<figure.*?</figure>",
        "",
        text,
        flags=re.I | re.S
    )

    # -----------------------------------------------------
    # ELIMINARE IMAGINI XML
    # -----------------------------------------------------

    text = re.sub(
        r"<imagine\d+[^>]*/?>",
        "",
        text,
        flags=re.I
    )

    text = text.replace(
        "\u2029",
        "\n"
    )

    # -----------------------------------------------------
    # LISTE
    # -----------------------------------------------------

    text = re.sub(
        r"<LI>\s*<Lbl>.*?</Lbl>\s*<LBody>(.*?)</LBody>\s*</LI>",
        r"\n__LBODY__&#8226; \1\n",
        text,
        flags=re.I | re.S
    )

    # -----------------------------------------------------
    # INTERTITLU
    # -----------------------------------------------------

    text = re.sub(
        r"<Intertitlu>(.*?)</Intertitlu>",
        r"\n<strong>\1</strong>\n",
        text,
        flags=re.I | re.S
    )

    # -----------------------------------------------------
    # SUB_INTERTITLU
    # -----------------------------------------------------

    text = re.sub(
        r"<Sub_Intertitlu>(.*?)</Sub_Intertitlu>",
        r"\n<strong><i>\1</i></strong>\n",
        text,
        flags=re.I | re.S
    )

    # -----------------------------------------------------
    # INTER_STYLE_3
    # -----------------------------------------------------

    text = re.sub(
        r"<INTER_Style_3>(.*?)</INTER_Style_3>",
        r"\n<strong><i>\1</i></strong>\n",
        text,
        flags=re.I | re.S
    )

    lines = [
        x.strip()
        for x in text.splitlines()
        if x.strip()
    ]

    html = []

    for i, line in enumerate(lines):

        is_lbody = line.startswith(
            "__LBODY__"
        )

        if is_lbody:

            line = line.replace(
                "__LBODY__",
                "",
                1
            )

        processed = linkify(
            line
        )

        processed = superscript_refs(
            processed
        )

        processed = superscript_symbols(
            processed
        )

        clean = re.sub(
            r"<[^>]+>",
            "",
            processed
        )

        words = len(
            clean.split()
        )

        next_long = False

        if i + 1 < len(lines):

            next_clean = re.sub(
                r"<[^>]+>",
                "",
                lines[i + 1].replace(
                    "__LBODY__",
                    ""
                )
            )

            next_long = (
                len(next_clean.split()) > 8
            )

        # -------------------------------------------------
        # LISTĂ
        # -------------------------------------------------

        if is_lbody:

            html.append(
                f"<p>{processed}</p>"
            )

        # -------------------------------------------------
        # TITLU / INTERTITLU AUTOMAT
        # -------------------------------------------------

        elif (
            1 <= words <= 8
            and next_long
        ):

            html.append(
                f"<p><strong>{processed}</strong></p>"
            )

        # -------------------------------------------------
        # PARAGRAF NORMAL
        # -------------------------------------------------

        else:

            html.append(
                f"<p>{processed}</p>"
            )

    return "\n".join(
        html
    )


# =========================================================
# =========================================================
# ARTICOLE ȘTIINȚIFICE
# BIBLIOGRAFIE
# =========================================================


def format_bibliography(text):

    if not text:
        return ""

    html = "<ol>"

    for r in [
        x.strip()
        for x in text.splitlines()
        if x.strip()
    ]:

        html += (
            f"<li>{linkify(r)}</li>"
        )

    return html + "</ol>"


# =========================================================
# =========================================================
# ARTICOLE ȘTIINȚIFICE
# BUILD HTML
# =========================================================
# NU MODIFICĂM FLUXUL ȘTIINȚIFIC.
# =========================================================


def build_html(data):

    # -----------------------------------------------------
    # TITLU ROMÂNĂ
    # -----------------------------------------------------

    titlu_ro = data.get(
        "titlu_ro",
        data.get(
            "titlu",
            ""
        )
    )

    # -----------------------------------------------------
    # TITLU ENGLEZĂ
    # -----------------------------------------------------

    titlu_en = data.get(
        "titlu_en",
        data.get(
            "english_title",
            ""
        )
    )

    # -----------------------------------------------------
    # AUTORI
    # -----------------------------------------------------

    autori = data.get(
        "autori",
        data.get(
            "autor",
            ""
        )
    )

    # -----------------------------------------------------
    # CONȚINUT
    # -----------------------------------------------------

    continut_text = data.get(
        "continut",
        data.get(
            "continut_articol",
            ""
        )
    )

    continut = format_content(
        continut_text
    )

    # -----------------------------------------------------
    # ABSTRACT
    # -----------------------------------------------------

    abstract = superscript_symbols(
        superscript_refs(
            linkify(
                data.get(
                    "abstract",
                    ""
                )
            )
        )
    )

    # -----------------------------------------------------
    # KEYWORDS ENGLEZĂ
    # -----------------------------------------------------

    keywords = data.get(
        "keywords",
        data.get(
            "keywords_eng",
            ""
        )
    )

    kwe = superscript_symbols(
        superscript_refs(
            linkify(
                keywords
            )
        )
    )

    # -----------------------------------------------------
    # REZUMAT
    # -----------------------------------------------------

    rez = superscript_symbols(
        superscript_refs(
            linkify(
                data.get(
                    "rezumat",
                    ""
                )
            )
        )
    )

    # -----------------------------------------------------
    # CUVINTE CHEIE ROMÂNĂ
    # -----------------------------------------------------

    cuvinte_cheie = data.get(
        "cuvinte_cheie",
        data.get(
            "keywords_rom",
            ""
        )
    )

    kwr = superscript_symbols(
        superscript_refs(
            linkify(
                cuvinte_cheie
            )
        )
    )

    # -----------------------------------------------------
    # AUTOR CORESPONDENT
    # -----------------------------------------------------

    autor_corespondent = data.get(
        "autor_corespondent",
        data.get(
            "corespondent",
            ""
        )
    )

    # -----------------------------------------------------
    # SUPORT FINANCIAR
    # -----------------------------------------------------

    suport = data.get(
        "suport",
        data.get(
            "financial_support",
            ""
        )
    )

    # -----------------------------------------------------
    # LICENȚĂ
    # -----------------------------------------------------

    licenta = data.get(
        "licenta_cc_by",
        data.get(
            "cc_by",
            ""
        )
    )

    # -----------------------------------------------------
    # PRIMIT
    # -----------------------------------------------------

    primit = data.get(
        "primit",
        ""
    )

    if primit.lower().startswith(
        "primit:"
    ):

        primit = primit.split(
            ":",
            1
        )[1].strip()

    # -----------------------------------------------------
    # ACCEPTAT
    # -----------------------------------------------------

    acceptat = data.get(
        "acceptat",
        ""
    )

    if acceptat.lower().startswith(
        "acceptat:"
    ):

        acceptat = acceptat.split(
            ":",
            1
        )[1].strip()

    # =====================================================
    # HTML ARTICOL ȘTIINȚIFIC
    # =====================================================

    return f"""<!DOCTYPE html>
<html lang="ro">

<head>

<meta charset="utf-8">

<title>{titlu_ro}</title>

<link
    rel="stylesheet"
    href="/static/style.css"
>

<style>

    .scientific-keywords {{
        margin-bottom: 28px;
    }}

    .scientific-keywords + h2 {{
        margin-top: 28px;
    }}

</style>

</head>

<body>

<h1>
{titlu_ro}
</h1>

<h2>
{titlu_en}
</h2>

<div>

<b>Autori:</b>

{superscript_author_refs(autori)}

</div>

<div>

Data publicării:
{data.get('data_publicarii', '')}

</div>

<div>

Primit:
{primit}

</div>

<div>

Acceptat:
{acceptat}

</div>

<div>

Editorial Group:
{data.get('editorial_grup', '')}

</div>

<div>

DOI:
{data.get('doi', '')}

</div>

<div>

Descarcă PDF:

<a
    href="{data.get('descarca_pdf', '')}"
    target="_blank"
>
    Click aici!
</a>

</div>

<hr>

<h2>
Abstract
</h2>

<p>

<i>
{abstract}
</i>

</p>

<p class="scientific-keywords">
{kwe}
</p>

<h2>
Rezumat
</h2>

<p>

<i>
{rez}
</i>

</p>

<p class="scientific-keywords">
{kwr}
</p>

<h2>
Conținut articol
</h2>

{continut}

<p>

<b>
{autor_corespondent}
</b>

</p>

<p>

<b>
{data.get('conflict', '')}
</b>

</p>

<p>

<b>
{suport}
</b>

</p>

<p>

{licenta}

</p>

<img
    src="https://www.medichub.ro/upload/photos/sigla_cc_by_25101.png"
    style="max-width:220px;"
>

<h2>
Bibliografie
</h2>

{format_bibliography(
    data.get(
        'bibliografie',
        ''
    )
)}

</body>

</html>"""


# =========================================================
# =========================================================
# ARTICOLE SIMPLE
# FUNCȚII SEPARATE
# =========================================================
# =========================================================


# =========================================================
# ARTICOLE SIMPLE
# AUTORI
# =========================================================


def superscript_simple_author_refs(text):

    if not text:
        return ""

    protected = []

    def protect(match):

        protected.append(
            match.group(0)
        )

        return (
            f"___AUTHOR_HTML_"
            f"{len(protected)-1}___"
        )

    # Protejăm eventualele taguri HTML
    text = re.sub(
        r"<[^>]+>",
        protect,
        text
    )

    # Numerele imediat după numele autorilor
    # devin superscript.
    text = re.sub(
        r"(?<=[A-Za-zĂÂÎȘȚăâîșț\-])"
        r"(\d+(?:,\d+)*)",
        r"<sup>\1</sup>",
        text
    )

    # Restaurăm tagurile
    for i, tag in enumerate(
        protected
    ):

        text = text.replace(
            f"___AUTHOR_HTML_{i}___",
            tag
        )

    return text


# =========================================================
# ARTICOLE SIMPLE
# H5 = AUTORI
#
# H5:
# - întotdeauna bold
# - numerele autorilor superscript
# =========================================================


def process_simple_h5(match):

    author_text = match.group(
        1
    ).strip()

    # Superscript DOAR pentru autori
    author_text = (
        superscript_simple_author_refs(
            author_text
        )
    )

    # Bold pentru toți autorii
    author_text = (
        "<strong>"
        + author_text
        + "</strong>"
    )

    return (
        "\n"
        "__SIMPLE_AUTHORS__"
        + author_text
        + "\n"
    )


# =========================================================
# ARTICOLE SIMPLE
# AFILIERI
#
# LBody = afiliere.
#
# Numerotarea se resetează la fiecare H5.
# =========================================================


def process_simple_affiliations(text):

    parts = text.split(
        "__SIMPLE_AUTHORS__"
    )

    processed_parts = []

    for index, part in enumerate(
        parts
    ):

        # Înainte de primul H5
        if index == 0:

            processed_parts.append(
                part
            )

            continue

        counter = 0

        def replace_lbody(match):

            nonlocal counter

            counter += 1

            content = match.group(
                1
            ).strip()

            return (
                "\n"
                "__SIMPLE_AFFILIATION__"
                f"{counter}"
                "__AFFILIATION_TEXT__"
                f"{content}"
                "__END_AFFILIATION__"
                "\n"
            )

        # -------------------------------------------------
        # Varianta LBody simplă
        # -------------------------------------------------

        part = re.sub(
            r"<LBody>(.*?)</LBody>",
            replace_lbody,
            part,
            flags=re.I | re.S
        )

        # -------------------------------------------------
        # Dacă LBody era în LI, eliminăm LI/Lbl.
        # -------------------------------------------------

        part = re.sub(
            r"<LI>\s*"
            r"<Lbl>.*?</Lbl>\s*"
            r"(__SIMPLE_AFFILIATION__"
            r"\d+"
            r"__AFFILIATION_TEXT__"
            r".*?"
            r"__END_AFFILIATION__)"
            r"\s*</LI>",
            r"\1",
            part,
            flags=re.I | re.S
        )

        processed_parts.append(
            part
        )

    return (
        "__SIMPLE_AUTHORS__"
    ).join(
        processed_parts
    )


# =========================================================
# ARTICOLE SIMPLE
# H2 DUPLICATE
#
# Dacă există:
#
# <h2>Același text</h2>
# ...
# <h2>Același text</h2>
#
# se păstrează prima apariție.
# =========================================================


def remove_duplicate_simple_h2(text):

    if not text:
        return ""

    seen = set()

    def replace_h2(match):

        content = match.group(
            1
        ).strip()

        # Eliminăm tagurile HTML pentru comparație
        clean_content = re.sub(
            r"<[^>]+>",
            "",
            content
        )

        # Normalizăm spațiile
        normalized = re.sub(
            r"\s+",
            " ",
            clean_content
        ).strip().lower()

        # H2 gol
        if not normalized:
            return ""

        # Dacă a mai fost întâlnit,
        # eliminăm această apariție.
        if normalized in seen:
            return ""

        seen.add(
            normalized
        )

        return (
            "\n"
            "__SIMPLE_H2__"
            + content
            + "__END_H2__"
            "\n"
        )

    return re.sub(
        r"<h2>(.*?)</h2>",
        replace_h2,
        text,
        flags=re.I | re.S
    )


# =========================================================
# ARTICOLE SIMPLE
# H4
#
# Primul H4 întâlnit = TITLU
#
# Dacă următorul H4 este întâlnit:
# = bold + italic
#
# Exemplu:
#
# <H4>Titlu articol</H4>
# <H4>Subtitlu</H4>
#
# devine:
#
# <h1>Titlu articol</h1>
# <p><strong><i>Subtitlu</i></strong></p>
# =========================================================


def process_simple_h4(match):

    # Această funcție este folosită doar dacă este apelată
    # cu starea externă corespunzătoare.
    return match.group(1)


# =========================================================
# ARTICOLE SIMPLE
# FORMAT CONTENT
# =========================================================


def format_simple_content(text):

    if not text:
        return ""

    # =====================================================
    # ELIMINARE TAGURI XML GENERALE
    # =====================================================

    text = re.sub(
        r"</?(ContinutArticol|continut_articol|body)[^>]*>",
        "",
        text,
        flags=re.I
    )

    # =====================================================
    # ELIMINARE TABELE
    # =====================================================

    text = re.sub(
        r"<table.*?</table>",
        "",
        text,
        flags=re.I | re.S
    )

    # =====================================================
    # ELIMINARE FIGURI
    # =====================================================

    text = re.sub(
        r"<figure.*?</figure>",
        "",
        text,
        flags=re.I | re.S
    )

    # =====================================================
    # ELIMINARE IMAGINI XML
    # =====================================================

    text = re.sub(
        r"<imagine\d+[^>]*/?>",
        "",
        text,
        flags=re.I
    )

    text = text.replace(
        "\u2029",
        "\n"
    )

    # =====================================================
    # H2 DUPLICAT
    #
    # Se face înaintea procesării celorlalte taguri,
    # pentru a compara exact conținutul H2.
    # =====================================================

    text = remove_duplicate_simple_h2(
        text
    )

    # =====================================================
    # H5 = AUTORI
    # =====================================================

    text = re.sub(
        r"<H5>(.*?)</H5>",
        process_simple_h5,
        text,
        flags=re.I | re.S
    )

    # =====================================================
    # LBody = AFILIERI
    # =====================================================

    text = process_simple_affiliations(
        text
    )

    # =====================================================
    # H4
    #
    # Primul H4 = titlu.
    # Următoarele H4 = italic + bold.
    # =====================================================

    h4_counter = 0

    def replace_h4(match):

        nonlocal h4_counter

        h4_counter += 1

        content = match.group(
            1
        ).strip()

        if h4_counter == 1:

            return (
                "\n"
                "__SIMPLE_TITLE__"
                + content
                + "__END_TITLE__"
                "\n"
            )

        return (
            "\n"
            "__SIMPLE_H4_ITALIC__"
            + content
            + "__END_H4_ITALIC__"
            "\n"
        )

    text = re.sub(
        r"<H4>(.*?)</H4>",
        replace_h4,
        text,
        flags=re.I | re.S
    )

    # =====================================================
    # INTERTITLU
    # =====================================================

    text = re.sub(
        r"<Intertitlu>(.*?)</Intertitlu>",
        r"\n<strong>\1</strong>\n",
        text,
        flags=re.I | re.S
    )

    # =====================================================
    # SUB_INTERTITLU
    # =====================================================

    text = re.sub(
        r"<Sub_Intertitlu>(.*?)</Sub_Intertitlu>",
        r"\n<strong><i>\1</i></strong>\n",
        text,
        flags=re.I | re.S
    )

    # =====================================================
    # INTER_STYLE_3
    # =====================================================

    text = re.sub(
        r"<INTER_Style_3>(.*?)</INTER_Style_3>",
        r"\n<strong><i>\1</i></strong>\n",
        text,
        flags=re.I | re.S
    )

    # =====================================================
    # P / p KEYWORDS
    #
    # Exemplu:
    #
    # <P>Keywords: alergie, copii</P>
    #
    # este transformat într-un marker separat.
    # =====================================================

    text = re.sub(
        r"<p[^>]*>\s*"
        r"(Keywords|Cuvinte cheie)"
        r"\s*:?\s*"
        r"(.*?)"
        r"</p>",
        lambda m: (
            "\n"
            "__SIMPLE_KEYWORDS__"
            + m.group(1)
            + ": "
            + m.group(2).strip()
            + "__END_KEYWORDS__"
            "\n"
        ),
        text,
        flags=re.I | re.S
    )

    # =====================================================
    # P / p NORMAL
    #
    # După ce Keywords a fost extras, toate celelalte
    # p/P devin text.
    # =====================================================

    text = re.sub(
        r"</?p[^>]*>",
        "\n",
        text,
        flags=re.I
    )

    # =====================================================
    # LI / LBL RĂMASE
    # =====================================================

    text = re.sub(
        r"<Lbl>.*?</Lbl>",
        "",
        text,
        flags=re.I | re.S
    )

    text = re.sub(
        r"</?LI>",
        "\n",
        text,
        flags=re.I
    )

    # =====================================================
    # LINII
    # =====================================================

    lines = [
        x.strip()
        for x in text.splitlines()
        if x.strip()
    ]

    # =====================================================
    # ELIMINARE HEADERE REPETATE
    #
    # IMPORTANT:
    #
    # Această regulă este numai pentru articole simple.
    #
    # Nu afectează H1/H4/H5/H2 procesate prin markeri.
    # =====================================================

    candidate_lines = []

    for line in lines:

        if line.startswith(
            "__SIMPLE_TITLE__"
        ):
            continue

        if line.startswith(
            "__SIMPLE_H4_ITALIC__"
        ):
            continue

        if line.startswith(
            "__SIMPLE_AUTHORS__"
        ):
            continue

        if line.startswith(
            "__SIMPLE_AFFILIATION__"
        ):
            continue

        if line.startswith(
            "__SIMPLE_H2__"
        ):
            continue

        if line.startswith(
            "__SIMPLE_KEYWORDS__"
        ):
            continue

        clean_line = re.sub(
            r"<[^>]+>",
            "",
            line
        ).strip()

        if not clean_line:
            continue

        words = clean_line.split()

        if 1 <= len(words) <= 12:

            candidate_lines.append(
                clean_line
            )

    # =====================================================
    # IDENTIFICARE REPETIȚII
    # =====================================================

    from collections import Counter

    line_counter = Counter(
        candidate_lines
    )

    repeated_headers = {
        line
        for line, count in line_counter.items()
        if count >= 2
    }

    # =====================================================
    # ELIMINARE REPETIȚII
    #
    # Pentru header-ele de pagină repetate:
    # eliminăm aparițiile.
    #
    # Markerii speciali sunt păstrați.
    # =====================================================

    filtered_lines = []

    for line in lines:

        # -------------------------------------------------
        # TITLU
        # -------------------------------------------------

        if line.startswith(
            "__SIMPLE_TITLE__"
        ):

            filtered_lines.append(
                line
            )

            continue

        # -------------------------------------------------
        # H4
        # -------------------------------------------------

        if line.startswith(
            "__SIMPLE_H4_ITALIC__"
        ):

            filtered_lines.append(
                line
            )

            continue

        # -------------------------------------------------
        # AUTORI
        # -------------------------------------------------

        if line.startswith(
            "__SIMPLE_AUTHORS__"
        ):

            filtered_lines.append(
                line
            )

            continue

        # -------------------------------------------------
        # AFILIERI
        # -------------------------------------------------

        if line.startswith(
            "__SIMPLE_AFFILIATION__"
        ):

            filtered_lines.append(
                line
            )

            continue

        # -------------------------------------------------
        # H2
        # -------------------------------------------------

        if line.startswith(
            "__SIMPLE_H2__"
        ):

            filtered_lines.append(
                line
            )

            continue

        # -------------------------------------------------
        # KEYWORDS
        # -------------------------------------------------

        if line.startswith(
            "__SIMPLE_KEYWORDS__"
        ):

            filtered_lines.append(
                line
            )

            continue

        # -------------------------------------------------
        # TEXT NORMAL
        # -------------------------------------------------

        clean_line = re.sub(
            r"<[^>]+>",
            "",
            line
        ).strip()

        if clean_line in repeated_headers:

            continue

        filtered_lines.append(
            line
        )

    lines = filtered_lines

    # =====================================================
    # PROCESARE HTML
    # =====================================================

    html = []

    for line in lines:

        # =================================================
        # PRIMUL H4 = TITLU
        # =================================================

        if line.startswith(
            "__SIMPLE_TITLE__"
        ):

            title = line.replace(
                "__SIMPLE_TITLE__",
                "",
                1
            )

            title = title.replace(
                "__END_TITLE__",
                "",
                1
            ).strip()

            title = linkify(
                title
            )

            title = superscript_symbols(
                title
            )

            html.append(
                f"<h1>{title}</h1>"
            )

            continue

        # =================================================
        # H4 ULTERIOR = ITALIC + BOLD
        # =================================================

        if line.startswith(
            "__SIMPLE_H4_ITALIC__"
        ):

            h4_text = line.replace(
                "__SIMPLE_H4_ITALIC__",
                "",
                1
            )

            h4_text = h4_text.replace(
                "__END_H4_ITALIC__",
                "",
                1
            ).strip()

            h4_text = linkify(
                h4_text
            )

            h4_text = superscript_symbols(
                h4_text
            )

            html.append(
                f"<p><strong><i>{h4_text}</i></strong></p>"
            )

            continue

        # =================================================
        # H2
        #
        # Duplicatele au fost eliminate anterior.
        # =================================================

        if line.startswith(
            "__SIMPLE_H2__"
        ):

            h2_text = line.replace(
                "__SIMPLE_H2__",
                "",
                1
            )

            h2_text = h2_text.replace(
                "__END_H2__",
                "",
                1
            ).strip()

            h2_text = linkify(
                h2_text
            )

            h2_text = superscript_symbols(
                h2_text
            )

            html.append(
                f"<p><strong>{h2_text}</strong></p>"
            )

            continue

        # =================================================
        # H5 = AUTORI
        # =================================================

        if line.startswith(
            "__SIMPLE_AUTHORS__"
        ):

            author_html = line.replace(
                "__SIMPLE_AUTHORS__",
                "",
                1
            ).strip()

            html.append(
                f"<p>{author_html}</p>"
            )

            continue

        # =================================================
        # LBody = AFILIERE
        # =================================================

        affiliation_match = re.match(
            r"__SIMPLE_AFFILIATION__"
            r"(\d+)"
            r"__AFFILIATION_TEXT__"
            r"(.*?)"
            r"__END_AFFILIATION__$",
            line,
            flags=re.I | re.S
        )

        if affiliation_match:

            number = affiliation_match.group(
                1
            )

            affiliation_text = (
                affiliation_match.group(
                    2
                ).strip()
            )

            affiliation_text = linkify(
                affiliation_text
            )

            affiliation_text = superscript_symbols(
                affiliation_text
            )

            html.append(
                f"<p>{number}. "
                f"<i>{affiliation_text}</i>"
                f"</p>"
            )

            continue

        # =================================================
        # KEYWORDS
        # =================================================

        if line.startswith(
            "__SIMPLE_KEYWORDS__"
        ):

            keywords_text = line.replace(
                "__SIMPLE_KEYWORDS__",
                "",
                1
            )

            keywords_text = keywords_text.replace(
                "__END_KEYWORDS__",
                "",
                1
            ).strip()

            keywords_text = linkify(
                keywords_text
            )

            keywords_text = superscript_symbols(
                keywords_text
            )

            html.append(
                f"<p><strong>{keywords_text}</strong></p>"
            )

            continue

        # =================================================
        # TEXT NORMAL
        # =================================================

        processed = linkify(
            line
        )

        processed = superscript_symbols(
            processed
        )

        html.append(
            f"<p>{processed}</p>"
        )

    # =====================================================
    # REGULA:
    # ARTICOLUL NU ÎNCEPE CU KEYWORDS
    #
    # Dacă primul element este Keywords, îl mutăm după
    # primul element real.
    # =====================================================

    if html:

        def is_keywords_html(value):

            clean_value = re.sub(
                r"<[^>]+>",
                "",
                value
            ).strip().lower()

            return (
                clean_value.startswith("keywords:")
                or clean_value.startswith("keywords ")
                or clean_value.startswith("cuvinte cheie:")
                or clean_value.startswith("cuvinte cheie ")
            )

        if is_keywords_html(
            html[0]
        ):

            keywords_block = html.pop(
                0
            )

            # Dacă există un alt element,
            # Keywords va veni după primul element.
            if html:

                html.insert(
                    1,
                    keywords_block
                )

            else:

                # Dacă articolul conține numai Keywords,
                # îl păstrăm.
                html.insert(
                    0,
                    keywords_block
                )

    return "\n".join(
        html
    )


# =========================================================
# =========================================================
# ARTICOLE SIMPLE
# KEYWORDS
# =========================================================


def add_keywords_break(text):

    if not text:
        return ""

    return re.sub(
        r"<p>\s*"
        r"(Keywords|Cuvinte cheie)"
        r"(\s*:?)\s*"
        r"(.*?)"
        r"</p>",
        r"<p><strong>\1\2</strong> \3</p><br>",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )


# =========================================================
# =========================================================
# ARTICOLE SIMPLE
# BUILD HTML
# =========================================================


def build_simple_html(data):

    # =====================================================
    # TITLU
    # =====================================================

    titlu = data.get(
        "titlu",
        ""
    ).strip()

    # =====================================================
    # CONȚINUT
    # =====================================================

    continut_text = data.get(
        "continut_articol",
        ""
    )

    # =====================================================
    # FORMAT CONTENT
    #
    # NU folosim build_html().
    #
    # NU folosim superscript_author_refs().
    #
    # Articolul simplu are propriile reguli.
    # =====================================================

    continut = format_simple_content(
        continut_text
    )

    # =====================================================
    # KEYWORDS
    # =====================================================

    continut = add_keywords_break(
        continut
    )

    # =====================================================
    # TITLU DIN METADATA
    # =====================================================

    titlu_html = superscript_symbols(
        linkify(
            titlu
        )
    )

    # =====================================================
    # HTML FINAL
    # =====================================================

    return f"""
<!DOCTYPE html>

<html lang="ro">

<head>

    <meta charset="UTF-8">

    <title>{titlu_html}</title>

    <style>

        body {{
            font-family:
                Arial,
                Helvetica,
                sans-serif;

            line-height: 1.6;

            max-width: 900px;

            margin: 40px auto;

            padding: 0 20px;

            color: #222;
        }}

        h1 {{

            font-size: 28px;

            line-height: 1.3;

            margin-bottom: 30px;

        }}

        p {{

            margin-bottom: 15px;

        }}

        a {{

            color: #0066cc;

        }}

        sup {{

            font-size: 0.75em;

            vertical-align: super;

        }}

    </style>

</head>

<body>

    <h1>
        {titlu_html}
    </h1>

    <div class="continut-articol">

        {continut}

    </div>

</body>

</html>

