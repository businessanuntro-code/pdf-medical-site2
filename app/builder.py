# =========================================================
# builder.py
# =========================================================
#
# IMPORTANT:
# - ARTICOLELE STIINTIFICE sunt pastrate separat.
# - Regulile noi de mai jos se aplica DOAR articolelor simple.
# =========================================================

import re


# =========================================================
# =========================================================
# ARTICOLE STIINTIFICE
# FUNCTII GENERALE
# =========================================================

def linkify(text):

    if not text:
        return ""

    protected = []

    def protect(match):
        protected.append(match.group(0))
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
# ARTICOLE STIINTIFICE
# REFERINTE IN PARANTEZE
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
# ARTICOLE STIINTIFICE
# AUTORI
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
# ARTICOLE STIINTIFICE
# FORMAT CONTENT
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
        r"<imagine\d+[^>]*\/?>",
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

        processed = linkify(line)

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

    return "\n".join(html)


# =========================================================
# =========================================================
# ARTICOLE STIINTIFICE
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
# ARTICOLE STIINTIFICE
# BUILD HTML
# =========================================================

def build_html(data):

    titlu_ro = data.get(
        "titlu_ro",
        data.get("titlu", "")
    )

    titlu_en = data.get(
        "titlu_en",
        data.get("english_title", "")
    )

    autori = data.get(
        "autori",
        data.get("autor", "")
    )

    continut_text = data.get(
        "continut",
        data.get("continut_articol", "")
    )

    continut = format_content(
        continut_text
    )

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

    keywords = data.get(
        "keywords",
        data.get("keywords_eng", "")
    )

    kwe = superscript_symbols(
        superscript_refs(
            linkify(keywords)
        )
    )

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

    cuvinte_cheie = data.get(
        "cuvinte_cheie",
        data.get("keywords_rom", "")
    )

    kwr = superscript_symbols(
        superscript_refs(
            linkify(cuvinte_cheie)
        )
    )

    autor_corespondent = data.get(
        "autor_corespondent",
        data.get("corespondent", "")
    )

    suport = data.get(
        "suport",
        data.get("financial_support", "")
    )

    licenta = data.get(
        "licenta_cc_by",
        data.get("cc_by", "")
    )

    primit = data.get(
        "primit",
        ""
    )

    if primit.lower().startswith("primit:"):

        primit = primit.split(
            ":",
            1
        )[1].strip()

    acceptat = data.get(
        "acceptat",
        ""
    )

    if acceptat.lower().startswith("acceptat:"):

        acceptat = acceptat.split(
            ":",
            1
        )[1].strip()

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

</html>


# =========================================================
# =========================================================
# ARTICOLE SIMPLE
# REGULI SEPARATE
# =========================================================
#
# Structura XML:
#
# H4       -> titlu / titlu secundar
# H5       -> autori
# LBody    -> afiliere
# p / P    -> continut
# P Keywords: -> cuvinte cheie
#
# IMPORTANT:
# Nicio functie de mai jos nu este folosita de
# build_html() pentru articolele stiintifice.
# =========================================================


# =========================================================
# ARTICOLE SIMPLE
# H5 = AUTORI
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

    # Protejam eventualele taguri HTML.

    text = re.sub(
        r"<[^>]+>",
        protect,
        text
    )

    # Autor + numar:
    # Adam1 -> Adam<sup>1</sup>
    # Ormenisan2 -> Ormenisan<sup>2</sup>

    text = re.sub(
        r"(?<=[A-Za-zĂÂÎȘȚăâîșț\-])"
        r"(\d+(?:,\d+)*)",
        r"<sup>\1</sup>",
        text
    )

    for i, tag in enumerate(protected):

        text = text.replace(
            f"___AUTHOR_HTML_{i}___",
            tag
        )

    return text


# =========================================================
# ARTICOLE SIMPLE
# H5 = AUTORI
# =========================================================

def process_simple_h5(match):

    author_text = match.group(1)

    author_text = (
        superscript_simple_author_refs(
            author_text
        )
    )

    # Autorii sunt bold.

    author_text = (
        "<strong>"
        + author_text.strip()
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
# =========================================================
#
# Numerotarea:
#
# H5
# LBody -> 1
# LBody -> 2
#
# urmatorul H5
# LBody -> 1
# LBody -> 2
# LBody -> 3
#
# Se reseteaza la fiecare H5.
# =========================================================

def process_simple_affiliations(text):

    parts = text.split(
        "__SIMPLE_AUTHORS__"
    )

    processed_parts = []

    for index, part in enumerate(parts):

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
                f"{counter}."
                "__AFFILIATION_TEXT__"
                f"{content}"
                "__END_AFFILIATION__"
                "\n"
            )

        # LBody poate aparea:
        # 1. in LI
        # 2. singur
        #
        # In ambele cazuri il tratam ca afiliere.

        part = re.sub(
            r"<LI>\s*"
            r"(?:<Lbl>.*?</Lbl>\s*)?"
            r"<LBody>(.*?)</LBody>\s*"
            r"</LI>",
            replace_lbody,
            part,
            flags=re.I | re.S
        )

        part = re.sub(
            r"<LBody>(.*?)</LBody>",
            replace_lbody,
            part,
            flags=re.I | re.S
        )

        processed_parts.append(
            part
        )

    return (
        "__SIMPLE_AUTHORS__"
    ).join(processed_parts)


# =========================================================
# ARTICOLE SIMPLE
# HEADERE REPETATE DE PAGINA
# =========================================================
#
# In XML-ul articolelor simple, un header de pagina este
# de regula un paragraf (<p> / <P>) repetat identic la
# inceputul paginilor.
#
# Nu eliminam automat H4:
# H4 poate reprezenta un titlu/subtitlu legitim si poate
# aparea de mai multe ori in articol.
# =========================================================

def remove_repeated_simple_page_headers(text):

    if not text:
        return ""

    # Gasim paragrafele XML.
    paragraphs = re.findall(
        r"<p\b[^>]*>(.*?)</p>",
        text,
        flags=re.I | re.S
    )

    paragraphs_upper = re.findall(
        r"<P\b[^>]*>(.*?)</P>",
        text,
        flags=re.I | re.S
    )

    all_paragraphs = paragraphs + paragraphs_upper

    normalized = []

    for paragraph in all_paragraphs:

        clean = re.sub(
            r"<[^>]+>",
            " ",
            paragraph
        )

        clean = re.sub(
            r"\s+",
            " ",
            clean
        ).strip()

        if clean:
            normalized.append(
                clean.casefold()
            )

    counts = {}

    for value in normalized:

        counts[value] = (
            counts.get(value, 0) + 1
        )

    # Consideram header doar daca este repetat si este
    # relativ scurt. Nu eliminam paragrafe lungi.
    repeated = {
        value
        for value, count in counts.items()
        if count >= 2
        and 1 <= len(value.split()) <= 12
    }

    if not repeated:
        return text

    def remove_paragraph(match):

        content = match.group(1)

        clean = re.sub(
            r"<[^>]+>",
            " ",
            content
        )

        clean = re.sub(
            r"\s+",
            " ",
            clean
        ).strip()

        if clean.casefold() in repeated:
            return ""

        return match.group(0)

    return re.sub(
        r"<p\b[^>]*>.*?</p>",
        remove_paragraph,
        text,
        flags=re.I | re.S
    )


# =========================================================
# ARTICOLE SIMPLE
# FORMAT CONTENT
# =========================================================

def format_simple_content(text):

    if not text:
        return ""

    # -----------------------------------------------------
    # TAGURI GENERALE
    # -----------------------------------------------------

    text = re.sub(
        r"</?(ContinutArticol|continut_articol|body)[^>]*>",
        "",
        text,
        flags=re.I
    )

    # -----------------------------------------------------
    # TABELE
    # -----------------------------------------------------

    text = re.sub(
        r"<table.*?</table>",
        "",
        text,
        flags=re.I | re.S
    )

    # -----------------------------------------------------
    # FIGURI
    # -----------------------------------------------------

    text = re.sub(
        r"<figure.*?</figure>",
        "",
        text,
        flags=re.I | re.S
    )

    # -----------------------------------------------------
    # IMAGINI XML
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # HEADERE REPETATE DE PAGINA
    #
    # Doar paragrafele <p>/<P> scurte si repetate.
    # H4/H5 nu sunt eliminate aici.
    # -----------------------------------------------------

    text = remove_repeated_simple_page_headers(
        text
    )

    # =====================================================
    # H4 = TITLU / TITLU SECUNDAR
    # =====================================================
    #
    # Primul titlu principal este deja construit de
    # parse_simple_xml() si afisat de build_simple_html().
    #
    # H4-urile ramase in continut sunt titluri/secundare.
    # =====================================================

    text = re.sub(
        r"<H4\b[^>]*>(.*?)</H4>",
        r"\n__SIMPLE_H4__\1\n",
        text,
        flags=re.I | re.S
    )

    # =====================================================
    # H5 = AUTORI
    # =====================================================

    text = re.sub(
        r"<H5\b[^>]*>(.*?)</H5>",
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
    # KEYWORDS
    #
    # Pastram markerul pentru a putea formata exact
    # "Keywords:" / "Cuvinte cheie:".
    # =====================================================

    def process_keywords(match):

        content = match.group(1).strip()

        keyword_match = re.match(
            r"^\s*(Keywords|Cuvinte\s+cheie)"
            r"(\s*:?)\s*(.*)$",
            content,
            flags=re.I | re.S
        )

        if keyword_match:

            label = keyword_match.group(1)
            colon = keyword_match.group(2)
            values = keyword_match.group(3).strip()

            return (
                "\n"
                "__SIMPLE_KEYWORDS__"
                f"<strong>{label}{colon}</strong>"
                f"{(' ' + values) if values else ''}"
                "__END_KEYWORDS__"
                "\n"
            )

        return match.group(0)

    text = re.sub(
        r"<P\b[^>]*>(.*?)</P>",
        process_keywords,
        text,
        flags=re.I | re.S
    )

    # Aceeasi regula daca XML-ul foloseste <p>.

    text = re.sub(
        r"<p\b[^>]*>(.*?)</p>",
        process_keywords,
        text,
        flags=re.I | re.S
    )

    # =====================================================
    # ALTE INTERTITLURI EXISTENTE
    # =====================================================

    text = re.sub(
        r"<Intertitlu>(.*?)</Intertitlu>",
        r"\n<strong>\1</strong>\n",
        text,
        flags=re.I | re.S
    )

    text = re.sub(
        r"<Sub_Intertitlu>(.*?)</Sub_Intertitlu>",
        r"\n<strong><i>\1</i></strong>\n",
        text,
        flags=re.I | re.S
    )

    text = re.sub(
        r"<INTER_Style_3>(.*?)</INTER_Style_3>",
        r"\n<strong><i>\1</i></strong>\n",
        text,
        flags=re.I | re.S
    )

    # =====================================================
    # LINII
    # =====================================================

    lines = [
        x.strip()
        for x in text.splitlines()
        if x.strip()
    ]

    html = []

    for line in lines:

        # -------------------------------------------------
        # H4 = TITLU / TITLU SECUNDAR
        # -------------------------------------------------

        if line.startswith(
            "__SIMPLE_H4__"
        ):

            h4_text = line.replace(
                "__SIMPLE_H4__",
                "",
                1
            )

            h4_text = h4_text.strip()

            h4_text = linkify(
                h4_text
            )

            h4_text = superscript_symbols(
                h4_text
            )

            html.append(
                f"<h2>{h4_text}</h2>"
            )

            continue

        # -------------------------------------------------
        # AUTORI
        # -------------------------------------------------

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

        # -------------------------------------------------
        # AFILIERE
        # -------------------------------------------------

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
                affiliation_match.group(2).strip()
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

        # -------------------------------------------------
        # KEYWORDS
        # -------------------------------------------------

        if line.startswith(
            "__SIMPLE_KEYWORDS__"
        ):

            keyword_html = line.replace(
                "__SIMPLE_KEYWORDS__",
                "",
                1
            )

            keyword_html = keyword_html.replace(
                "__END_KEYWORDS__",
                "",
                1
            )

            keyword_html = linkify(
                keyword_html
            )

            keyword_html = superscript_symbols(
                keyword_html
            )

            html.append(
                f"<p>{keyword_html}</p><br>"
            )

            continue

        # -------------------------------------------------
        # RESTUL CONTINUTULUI
        # -------------------------------------------------

        processed = linkify(
            line
        )

        processed = superscript_symbols(
            processed
        )

        # Daca au ramas taguri XML simple, le pastram
        # doar pe cele HTML utile; tagurile XML necunoscute
        # sunt eliminate pentru a nu aparea in pagina.

        processed = re.sub(
            r"</?(?:NormalParagraphStyle|NoParagraphStyle|"
            r"ParagraphStyle|LBody|LI|Lbl)[^>]*>",
            "",
            processed,
            flags=re.I
        )

        if not processed.strip():
            continue

        html.append(
            f"<p>{processed}</p>"
        )

    return "\n".join(
        html
    )


# =========================================================
# ARTICOLE SIMPLE
# BUILD HTML
# =========================================================

def build_simple_html(data):

    # =====================================================
    # TITLU PRINCIPAL
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

    continut = format_simple_content(
        continut_text
    )

    # =====================================================
    # TITLU HTML
    # =====================================================

    titlu_html = superscript_symbols(
        linkify(titlu)
    )

    # =====================================================
    # HTML FINAL
    # =====================================================

    return f"""
<!DOCTYPE html>
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

        h2 {{
            font-size: 21px;

            line-height: 1.4;

            margin-top: 28px;

            margin-bottom: 12px;
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
