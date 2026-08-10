# =========================================================
# builder.py
# =========================================================

import re


# =========================================================
# =========================================================
# ARTICOLE ȘTIINȚIFICE
# FUNCȚII GENERALE
# =========================================================
# =========================================================


def linkify(text):

    if not text:
        return ""

    # Protejeaza tagurile HTML existente
    protected = []

    def protect(match):

        protected.append(match.group(0))

        return f"___HTML_{len(protected)-1}___"

    text = re.sub(
        r"<[^>]+>",
        protect,
        text
    )

    # Transforma doar URL-urile din text normal
    text = re.sub(
        r'(https?://[^\s]+|www\.[^\s]+)',
        lambda m:
            f'<a href="{"https://"+m.group(0) if m.group(0).startswith("www.") else m.group(0)}" target="_blank">{m.group(0)}</a>',
        text
    )

    # Pune tagurile HTML inapoi
    for i, tag in enumerate(protected):

        text = text.replace(
            f"___HTML_{i}___",
            tag
        )

    return text


# =========================================================
# REFERINTE IN PARANTEZE
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
        .replace("™", "<sup>™</sup>")
        .replace("®", "<sup>®</sup>")
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
# =========================================================

def format_content(text):

    if not text:
        return ""

    # =====================================================
    # ELIMINARE TAGURI XML
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
        r"<imagine\d+[^>]*\/?>",
        "",
        text,
        flags=re.I
    )

    text = text.replace(
        "\u2029",
        "\n"
    )

    # =====================================================
    # LISTE
    # =====================================================

    text = re.sub(
        r"<LI>\s*<Lbl>.*?</Lbl>\s*<LBody>(.*?)</LBody>\s*</LI>",
        r"\n__LBODY__&#8226; \1\n",
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
    # SEPARARE RANDURI
    # =====================================================

    lines = [
        x.strip()
        for x in text.splitlines()
        if x.strip()
    ]

    html = []

    # =====================================================
    # PROCESARE RANDURI
    # =====================================================

    for i, line in enumerate(lines):

        # Verificam daca este LBody
        is_lbody = line.startswith(
            "__LBODY__"
        )

        if is_lbody:

            line = line.replace(
                "__LBODY__",
                "",
                1
            )

        # -------------------------------------------------
        # LINKURI
        # -------------------------------------------------

        processed = linkify(
            line
        )

        # -------------------------------------------------
        # REFERINTE
        # -------------------------------------------------

        processed = superscript_refs(
            processed
        )

        # -------------------------------------------------
        # SIMBOLURI
        # -------------------------------------------------

        processed = superscript_symbols(
            processed
        )

        # -------------------------------------------------
        # TEXT CURAT
        # -------------------------------------------------

        clean = re.sub(
            r"<[^>]+>",
            "",
            processed
        )

        words = len(
            clean.split()
        )

        # -------------------------------------------------
        # URMATORUL PARAGRAF
        # -------------------------------------------------

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
        # LISTA
        # -------------------------------------------------

        if is_lbody:

            html.append(
                f"<p>{processed}</p>"
            )

        # -------------------------------------------------
        # TITLU / INTERTITLU AUTOMAT
        # -------------------------------------------------

        elif 1 <= words <= 8 and next_long:

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
# =========================================================

def build_html(data):

    # =====================================================
    # TITLU ROMANA
    # =====================================================

    titlu_ro = data.get(
        "titlu_ro",
        data.get("titlu", "")
    )

    # =====================================================
    # TITLU ENGLEZA
    # =====================================================

    titlu_en = data.get(
        "titlu_en",
        data.get("english_title", "")
    )

    # =====================================================
    # AUTORI
    # =====================================================

    autori = data.get(
        "autori",
        data.get("autor", "")
    )

    # =====================================================
    # CONTINUT
    # =====================================================

    continut_text = data.get(
        "continut",
        data.get("continut_articol", "")
    )

    continut = format_content(
        continut_text
    )

    # =====================================================
    # ABSTRACT
    # =====================================================

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

    # =====================================================
    # KEYWORDS ENGLEZA
    # =====================================================

    keywords = data.get(
        "keywords",
        data.get("keywords_eng", "")
    )

    kwe = superscript_symbols(
        superscript_refs(
            linkify(keywords)
        )
    )

    # =====================================================
    # REZUMAT
    # =====================================================

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

    # =====================================================
    # CUVINTE CHEIE ROMANA
    # =====================================================

    cuvinte_cheie = data.get(
        "cuvinte_cheie",
        data.get("keywords_rom", "")
    )

    kwr = superscript_symbols(
        superscript_refs(
            linkify(cuvinte_cheie)
        )
    )

    # =====================================================
    # AUTOR CORESPONDENT
    # =====================================================

    autor_corespondent = data.get(
        "autor_corespondent",
        data.get("corespondent", "")
    )

    # =====================================================
    # SUPORT FINANCIAR
    # =====================================================

    suport = data.get(
        "suport",
        data.get("financial_support", "")
    )

    # =====================================================
    # LICENTA
    # =====================================================

    licenta = data.get(
        "licenta_cc_by",
        data.get("cc_by", "")
    )

    # =====================================================
    # PRIMIT
    # =====================================================

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

    # =====================================================
    # ACCEPTAT
    # =====================================================

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
    # HTML
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

<p>

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

<p>

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
#
# Popescu1
# Popescu2
# Popescu1,2
#
# devin:
#
# Popescu<sup>1</sup>
# Popescu<sup>2</sup>
# Popescu<sup>1,2</sup>
# =========================================================

def superscript_simple_author_refs(text):

    if not text:
        return ""

    # Protejam eventualele taguri HTML existente
    protected = []

    def protect(match):

        protected.append(
            match.group(0)
        )

        return (
            f"___AUTHOR_HTML_"
            f"{len(protected)-1}___"
        )

    text = re.sub(
        r"<[^>]+>",
        protect,
        text
    )

    # Autor + numar
    text = re.sub(
        r"(?<=[A-Za-zĂÂÎȘȚăâîșț\-])"
        r"(\d+(?:,\d+)*)",
        r"<sup>\1</sup>",
        text
    )

    # Restauram tagurile
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
# Autorii:
# - bold
# - numere superscript
# =========================================================

def process_simple_h5(match):

    author_text = match.group(
        1
    )

    # Superscript DOAR pentru autori
    author_text = (
        superscript_simple_author_refs(
            author_text
        )
    )

    # Bold pentru intreaga zona
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
# <LI>...</LI>
#
# devine:
#
# 1. afiliere
# 2. afiliere
# 3. afiliere
#
# fiecare afiliere este italic.
# =========================================================

def process_simple_affiliations(text):

    counter = 0

    def replace_lbody(match):

        nonlocal counter

        counter += 1

        content = match.group(
            1
        ).strip()

        return (
            "\n"
            f"__SIMPLE_AFFILIATION__"
            f"{counter}."
            f"__AFFILIATION_TEXT__"
            f"{content}"
            f"__END_AFFILIATION__"
            "\n"
        )

    text = re.sub(
        r"<LI>\s*"
        r"<Lbl>.*?</Lbl>\s*"
        r"<LBody>(.*?)</LBody>\s*"
        r"</LI>",
        replace_lbody,
        text,
        flags=re.I | re.S
    )

    return text


# =========================================================
# ARTICOLE SIMPLE
# FORMAT CONTENT
#
# IMPORTANT:
#
# Nu folosim format_content() pentru partea de autori.
#
# Astfel:
#
# H5 -> bold + superscript
#
# LI -> 1. 2. 3. + italic
#
# Restul textului NU primeste regula de superscript
# pentru autori.
# =========================================================

def format_simple_content(text):

    if not text:
        return ""

    # =====================================================
    # ELIMINARE TAGURI GENERALE
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
        r"<imagine\d+[^>]*\/?>",
        "",
        text,
        flags=re.I
    )

    text = text.replace(
        "\u2029",
        "\n"
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
    # AFILIERI
    # =====================================================

    text = process_simple_affiliations(
        text
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
    # SEPARARE RANDURI
    # =====================================================

    lines = [
        x.strip()
        for x in text.splitlines()
        if x.strip()
    ]

    html = []

    # =====================================================
    # PROCESARE RANDURI
    # =====================================================

    for i, line in enumerate(lines):

        # =================================================
        # AUTORI
        # =================================================

        if line.startswith(
            "__SIMPLE_AUTHORS__"
        ):

            author_html = line.replace(
                "__SIMPLE_AUTHORS__",
                "",
                1
            )

            html.append(
                f"<p>{author_html}</p>"
            )

            continue

        # =================================================
        # AFILIERE
        # =================================================

        affiliation_match = re.match(
            r"__SIMPLE_AFFILIATION__"
            r"(\d+)\."
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
                affiliation_match.group(2)
            )

            # Linkuri in afiliere
            affiliation_text = linkify(
                affiliation_text
            )

            html.append(
                f"<p>{number}. "
                f"<i>{affiliation_text}</i>"
                f"</p>"
            )

            continue

        # =================================================
        # LINKURI
        # =================================================

        processed = linkify(
            line
        )

        # =================================================
        # SIMBOLURI
        #
        # Nu aplicam superscript pentru numerele autorilor.
        # =================================================

        processed = superscript_symbols(
            processed
        )

        # =================================================
        # TEXT CURAT
        # =================================================

        clean = re.sub(
            r"<[^>]+>",
            "",
            processed
        )

        words = len(
            clean.split()
        )

        # =================================================
        # URMATORUL RAND
        # =================================================

        next_long = False

        if i + 1 < len(lines):

            next_clean = re.sub(
                r"<[^>]+>",
                "",
                lines[i + 1]
            )

            next_long = (
                len(
                    next_clean.split()
                ) > 8
            )

        # =================================================
        # TITLU / INTERTITLU AUTOMAT
        # =================================================

        if (
            1 <= words <= 8
            and next_long
        ):

            html.append(
                f"<p><strong>{processed}</strong></p>"
            )

        # =================================================
        # PARAGRAF NORMAL
        # =================================================

        else:

            html.append(
                f"<p>{processed}</p>"
            )

    return "\n".join(
        html
    )


# =========================================================
# =========================================================
# ARTICOLE SIMPLE
# BUILD HTML
# =========================================================
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
    # CONTINUT
    # =====================================================

    continut_text = data.get(
        "continut_articol",
        ""
    )

    # =====================================================
    # FORMAT CONTINUT SIMPLU
    #
    # NU folosim build_html()
    # NU folosim superscript_author_refs()
    #
    # Articolul simplu are reguli proprii.
    # =====================================================

    continut = format_simple_content(
        continut_text
    )

    # =====================================================
    # TITLU
    # =====================================================

    titlu_html = superscript_symbols(
        linkify(titlu)
    )

    # =====================================================
    # HTML FINAL
    # =====================================================

    return f"""<!DOCTYPE html>
<html lang="ro">

<head>

    <meta charset="UTF-8">

    <title>{titlu}</title>

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

</html>"""
