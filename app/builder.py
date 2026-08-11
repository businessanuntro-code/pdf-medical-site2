import re


# =========================================================
# ARTICOLE STIINTIFICE - FUNCTII EXISTENTE
# =========================================================

def linkify(text):
    if not text:
        return ""

    protected = []

    def protect(match):
        protected.append(match.group(0))
        return f"___HTML_{len(protected) - 1}___"

    text = re.sub(r"<[^>]+>", protect, text)

    text = re.sub(
        r'(https?://[^\s]+|www\.[^\s]+)',
        lambda m: (
            f'<a href="{"https://" + m.group(0) if m.group(0).startswith("www.") else m.group(0)}" '
            f'target="_blank">{m.group(0)}</a>'
        ),
        text,
    )

    for i, tag in enumerate(protected):
        text = text.replace(f"___HTML_{i}___", tag)

    return text


def superscript_refs(text):
    if not text:
        return ""

    def convert(match):
        return f"<sup>{match.group(0)}</sup>"

    return re.sub(
        r'\(\d+(?:\s*,\s*\d+)*\)',
        convert,
        text,
    )


def superscript_author_refs(text):
    if not text:
        return ""

    return re.sub(
        r'(?<=[A-Za-zĂÂÎȘȚăâîșț\-])(\d+(?:,\d+)*)',
        r'<sup>\1</sup>',
        text,
    )


def superscript_symbols(text):
    if not text:
        return ""

    return (
        text
        .replace("™", "<sup>™</sup>")
        .replace("®", "<sup>®</sup>")
    )


def render_image(url):
    return (
        f'<figure class="img-figure">'
        f'<img src="{url}" class="article-image"/>'
        f'</figure>'
    )


# =========================================================
# ARTICOLE STIINTIFICE
# FORMAT CONTENT
# =========================================================

def format_content(text):
    if not text:
        return ""

    text = re.sub(
        r"</?(ContinutArticol|continut_articol|body)[^>]*>",
        "",
        text,
        flags=re.I,
    )

    text = re.sub(
        r"<table.*?</table>",
        "",
        text,
        flags=re.I | re.S,
    )

    text = re.sub(
        r"<figure.*?</figure>",
        "",
        text,
        flags=re.I | re.S,
    )

    text = re.sub(
        r"<imagine\d+[^>]*/?>",
        "",
        text,
        flags=re.I,
    )

    text = text.replace("\u2029", "\n")

    text = re.sub(
        r"<LI>\s*<Lbl>.*?</Lbl>\s*<LBody>(.*?)</LBody>\s*</LI>",
        r"\n__LBODY__&#8226; \1\n",
        text,
        flags=re.I | re.S,
    )

    text = re.sub(
        r"<Intertitlu>(.*?)</Intertitlu>",
        r"\n<strong>\1</strong>\n",
        text,
        flags=re.I | re.S,
    )

    text = re.sub(
        r"<Sub_Intertitlu>(.*?)</Sub_Intertitlu>",
        r"\n<strong><i>\1</i></strong>\n",
        text,
        flags=re.I | re.S,
    )

    text = re.sub(
        r"<INTER_Style_3>(.*?)</INTER_Style_3>",
        r"\n<strong><i>\1</i></strong>\n",
        text,
        flags=re.I | re.S,
    )

    lines = [
        x.strip()
        for x in text.splitlines()
        if x.strip()
    ]

    html = []

    for i, line in enumerate(lines):

        is_lbody = line.startswith("__LBODY__")

        if is_lbody:
            line = line.replace(
                "__LBODY__",
                "",
                1,
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
            processed,
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
                    "",
                ),
            )

            next_long = (
                len(next_clean.split()) > 8
            )

        if is_lbody:

            html.append(
                f"<p>{processed}</p>"
            )

        elif (
            1 <= words <= 8
            and next_long
        ):

            html.append(
                f"<p><strong>{processed}</strong></p>"
            )

        else:

            html.append(
                f"<p>{processed}</p>"
            )

    return "\n".join(html)


# =========================================================
# ARTICOLE STIINTIFICE
# BIBLIOGRAFIE
# =========================================================

def format_bibliography(text):
    if not text:
        return ""

    items = [
        x.strip()
        for x in text.splitlines()
        if x.strip()
    ]

    return (
        "<ol>"
        + "".join(
            f"<li>{linkify(item)}</li>"
            for item in items
        )
        + "</ol>"
    )


# =========================================================
# ARTICOLE STIINTIFICE
# BUILD HTML
# =========================================================

def build_html(data):

    titlu_ro = data.get(
        "titlu_ro",
        data.get(
            "titlu",
            "",
        ),
    )

    titlu_en = data.get(
        "titlu_en",
        data.get(
            "english_title",
            "",
        ),
    )

    autori = data.get(
        "autori",
        data.get(
            "autor",
            "",
        ),
    )

    continut_text = data.get(
        "continut",
        data.get(
            "continut_articol",
            "",
        ),
    )

    continut = format_content(
        continut_text
    )

    abstract = superscript_symbols(
        superscript_refs(
            linkify(
                data.get(
                    "abstract",
                    "",
                )
            )
        )
    )

    keywords = data.get(
        "keywords",
        data.get(
            "keywords_eng",
            "",
        ),
    )

    kwe = superscript_symbols(
        superscript_refs(
            linkify(
                keywords
            )
        )
    )

    rez = superscript_symbols(
        superscript_refs(
            linkify(
                data.get(
                    "rezumat",
                    "",
                )
            )
        )
    )

    cuvinte_cheie = data.get(
        "cuvinte_cheie",
        data.get(
            "keywords_rom",
            "",
        ),
    )

    kwr = superscript_symbols(
        superscript_refs(
            linkify(
                cuvinte_cheie
            )
        )
    )

    autor_corespondent = data.get(
        "autor_corespondent",
        data.get(
            "corespondent",
            "",
        ),
    )

    suport = data.get(
        "suport",
        data.get(
            "financial_support",
            "",
        ),
    )

    licenta = data.get(
        "licenta_cc_by",
        data.get(
            "cc_by",
            "",
        ),
    )

    primit = data.get(
        "primit",
        "",
    )

    if primit.lower().startswith(
        "primit:"
    ):
        primit = primit.split(
            ":",
            1,
        )[1].strip()

    acceptat = data.get(
        "acceptat",
        "",
    )

    if acceptat.lower().startswith(
        "acceptat:"
    ):
        acceptat = acceptat.split(
            ":",
            1,
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
{data.get("data_publicarii", "")}

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
{data.get("editorial_grup", "")}

</div>

<div>

DOI:
{data.get("doi", "")}

</div>

<div>

Descarcă PDF:

<a
    href="{data.get("descarca_pdf", "")}"
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
{data.get("conflict", "")}
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
        "bibliografie",
        "",
    )
)}

</body>

</html>"""

```python
# =========================================================
# =========================================================
# ARTICOLE SIMPLE
# FUNCȚII SEPARATE
# =========================================================
# =========================================================

import re


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
            f"___AUTHOR_HTML_{len(protected) - 1}___"
        )

    # Protejăm eventualele taguri HTML existente
    text = re.sub(
        r"<[^>]+>",
        protect,
        text
    )

    # Numerele lipite de numele autorilor
    # devin superscript.
    #
    # Exemplu:
    #
    # Alexandru Popescu1, Ion Ionescu2
    #
    # devine:
    #
    # Alexandru Popescu<sup>1</sup>,
    # Ion Ionescu<sup>2</sup>

    text = re.sub(
        r"(?<=[A-Za-zĂÂÎȘȚăâîșț\-])"
        r"(\d+(?:,\d+)*)",
        r"<sup>\1</sup>",
        text
    )

    # Restaurăm eventualele taguri HTML

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
# UTILITARE
# =========================================================

def _clean_simple_text(text):

    if not text:
        return ""

    # Eliminăm tagurile XML rămase
    text = re.sub(
        r"<[^>]+>",
        "",
        text
    )

    # Spații multiple
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def _is_keywords_text(text):

    clean = _clean_simple_text(
        text
    )

    return bool(
        re.match(
            r"^(?:Keywords|Cuvinte\s+cheie)"
            r"\s*:?",
            clean,
            flags=re.I
        )
    )


# =========================================================
# ARTICOLE SIMPLE
# H2
#
# REGULA:
# NU PRELUĂM NICIUN H2.
#
# H2 sunt de obicei headere repetate
# provenite din paginile PDF/XML.
# =========================================================

def _remove_all_h2(text):

    if not text:
        return ""

    return re.sub(
        r"<h2\b[^>]*>.*?</h2\s*>",
        "",
        text,
        flags=re.I | re.S
    )


# =========================================================
# ARTICOLE SIMPLE
# H4
#
# PRIMUL H4  = TITLU PRINCIPAL
# AL DOILEA H4 = TITLU SECUNDAR
# =========================================================

def _extract_simple_h4_titles(text):

    titles = []

    pattern = re.compile(
        r"<H4\b[^>]*>(.*?)</H4\s*>",
        flags=re.I | re.S
    )

    def replace(match):

        title = _clean_simple_text(
            match.group(1)
        )

        if title:
            titles.append(title)

        # Scoatem H4 din conținut.
        # Îl vom afișa separat.

        return ""

    remaining = pattern.sub(
        replace,
        text
    )

    return titles, remaining


# =========================================================
# ARTICOLE SIMPLE
# H5 = AUTORI
#
# BOLD + NUMERE SUPERSCRIPT
# =========================================================

def _process_simple_h5(text):

    authors = []

    pattern = re.compile(
        r"<H5\b[^>]*>(.*?)</H5\s*>",
        flags=re.I | re.S
    )

    def replace(match):

        author_text = _clean_simple_text(
            match.group(1)
        )

        if not author_text:
            return ""

        author_text = (
            superscript_simple_author_refs(
                author_text
            )
        )

        authors.append(
            f"<strong>{author_text}</strong>"
        )

        return ""

    remaining = pattern.sub(
        replace,
        text
    )

    return authors, remaining


# =========================================================
# ARTICOLE SIMPLE
# LBody = AFILIERE
#
# Exemplu:
#
# <LBody>
# Institute of Oncology...
# </LBody>
#
# devine:
#
# 1. Institute of Oncology...
#
# Dacă există mai multe:
#
# 1. ...
# 2. ...
# 3. ...
# =========================================================

def _process_simple_affiliations(text):

    affiliations = []

    # -----------------------------------------------------
    # CAZUL NORMAL:
    #
    # <LI>
    #     <Lbl>•</Lbl>
    #     <LBody>...</LBody>
    # </LI>
    # -----------------------------------------------------

    def replace_li(match):

        content = match.group(1).strip()

        if content:

            affiliations.append(
                content
            )

        return ""

    text = re.sub(
        r"<LI\b[^>]*>\s*"
        r"<Lbl\b[^>]*>.*?</Lbl>\s*"
        r"<LBody\b[^>]*>(.*?)</LBody\s*>\s*"
        r"</LI\s*>",
        replace_li,
        text,
        flags=re.I | re.S
    )

    # -----------------------------------------------------
    # CAZUL ÎN CARE LBody APARE DIRECT
    # -----------------------------------------------------

    def replace_direct_lbody(match):

        content = match.group(1).strip()

        if content:

            affiliations.append(
                content
            )

        return ""

    text = re.sub(
        r"<LBody\b[^>]*>(.*?)</LBody\s*>",
        replace_direct_lbody,
        text,
        flags=re.I | re.S
    )

    return affiliations, text


# =========================================================
# ARTICOLE SIMPLE
# ELIMINARE TAGURI GENERALE
# =========================================================

def _clean_simple_xml(text):

    if not text:
        return ""

    text = text.replace(
        "\u2029",
        "\n"
    )

    # Containere XML generale
    text = re.sub(
        r"</?(ContinutArticol|continut_articol|body)[^>]*>",
        "",
        text,
        flags=re.I
    )

    # Tabele
    text = re.sub(
        r"<table\b.*?</table\s*>",
        "",
        text,
        flags=re.I | re.S
    )

    # Figuri
    text = re.sub(
        r"<figure\b.*?</figure\s*>",
        "",
        text,
        flags=re.I | re.S
    )

    # Imagini XML
    text = re.sub(
        r"<imagine\d+[^>]*/?>",
        "",
        text,
        flags=re.I
    )

    return text


# =========================================================
# ARTICOLE SIMPLE
# PARAGRAFE
#
# Extragem <p> separat pentru a păstra structura XML.
# =========================================================

def _extract_simple_paragraphs(text):

    paragraphs = []

    pattern = re.compile(
        r"<p\b[^>]*>(.*?)</p\s*>",
        flags=re.I | re.S
    )

    def replace(match):

        content = match.group(1).strip()

        if content:

            paragraphs.append(
                content
            )

        return ""

    remaining = pattern.sub(
        replace,
        text
    )

    return paragraphs, remaining


# =========================================================
# ARTICOLE SIMPLE
# FORMATARE PARAGRAF
# =========================================================

def _format_simple_paragraph(text):

    if not text:
        return ""

    text = text.strip()

    # Linkuri
    text = linkify(
        text
    )

    # Simboluri
    text = superscript_symbols(
        text
    )

    return text


# =========================================================
# ARTICOLE SIMPLE
# KEYWORDS
# =========================================================

def _format_simple_keywords(text):

    if not text:
        return ""

    processed = _format_simple_paragraph(
        text
    )

    # Identificăm doar începutul:
    #
    # Keywords:
    # Cuvinte cheie:
    #
    # și îl facem bold.

    processed = re.sub(
        r"^(Keywords|Cuvinte\s+cheie)"
        r"(\s*:?)",
        lambda match: (
            "<strong>"
            + match.group(1)
            + match.group(2)
            + "</strong>"
        ),
        processed,
        count=1,
        flags=re.I
    )

    return processed


# =========================================================
# ARTICOLE SIMPLE
# HEADERE REPETATE
#
# În afară de H2, dacă apar exact aceleași linii
# de header provenite din paginile următoare,
# le putem elimina.
#
# NU aplicăm această regulă pe:
# - H4
# - H5
# - LBody
# - Keywords
# =========================================================

def _remove_repeated_plain_headers(lines):

    if not lines:
        return lines

    from collections import Counter

    candidates = []

    for line in lines:

        clean = _clean_simple_text(
            line
        )

        if not clean:
            continue

        # Keywords nu este header de pagină
        if _is_keywords_text(
            clean
        ):
            continue

        # Nu tratăm liniile foarte lungi
        # ca headere.

        word_count = len(
            clean.split()
        )

        if 1 <= word_count <= 12:

            candidates.append(
                clean.casefold()
            )

    counts = Counter(
        candidates
    )

    repeated = {
        key
        for key, count in counts.items()
        if count >= 2
    }

    result = []

    already_removed = set()

    for line in lines:

        clean = _clean_simple_text(
            line
        )

        key = clean.casefold()

        if (
            key in repeated
            and key not in already_removed
        ):

            # Păstrăm prima apariție.
            already_removed.add(
                key
            )

            result.append(
                line
            )

            continue

        if key in repeated:

            # A doua și următoarele apariții
            # sunt considerate headere repetate.

            continue

        result.append(
            line
        )

    return result


# =========================================================
# ARTICOLE SIMPLE
# FORMAT CONTENT
# =========================================================

def format_simple_content(text):

    if not text:

        return (
            "",
            ""
        )

    # -----------------------------------------------------
    # CURĂȚARE XML
    # -----------------------------------------------------

    text = _clean_simple_xml(
        text
    )

    # -----------------------------------------------------
    # H2
    #
    # IGNORĂM TOATE H2.
    # -----------------------------------------------------

    text = _remove_all_h2(
        text
    )

    # -----------------------------------------------------
    # H4
    #
    # PRIMUL H4 = TITLU PRINCIPAL
    # AL DOILEA H4 = TITLU SECUNDAR
    # -----------------------------------------------------

    h4_titles, text = (
        _extract_simple_h4_titles(
            text
        )
    )

    # -----------------------------------------------------
    # H5
    #
    # AUTORI
    # -----------------------------------------------------

    authors, text = (
        _process_simple_h5(
            text
        )
    )

    # -----------------------------------------------------
    # LBody
    #
    # AFILIERI
    # -----------------------------------------------------

    affiliations, text = (
        _process_simple_affiliations(
            text
        )
    )

    # -----------------------------------------------------
    # PARAGRAFE
    # -----------------------------------------------------

    paragraphs, text = (
        _extract_simple_paragraphs(
            text
        )
    )

    html = []

    # =====================================================
    # TITLU PRINCIPAL
    # =====================================================

    if h4_titles:

        title = _format_simple_paragraph(
            h4_titles[0]
        )

        html.append(
            f"<p><strong>{title}</strong></p>"
        )

    else:

        title = ""

    # =====================================================
    # TITLU SECUNDAR
    # =====================================================

    if len(h4_titles) >= 2:

        secondary_title = (
            _format_simple_paragraph(
                h4_titles[1]
            )
        )

        html.append(
            "<p>"
            "<strong>"
            "<i>"
            f"{secondary_title}"
            "</i>"
            "</strong>"
            "</p>"
        )

    # =====================================================
    # H5 = AUTORI
    # =====================================================

    for author in authors:

        html.append(
            f"<p>{author}</p>"
        )

    # =====================================================
    # AFILIERI
    # =====================================================

    for index, affiliation in enumerate(
        affiliations,
        start=1
    ):

        affiliation_html = (
            _format_simple_paragraph(
                affiliation
            )
        )

        html.append(
            f"<p>"
            f"{index}. "
            f"<i>{affiliation_html}</i>"
            f"</p>"
        )

    # =====================================================
    # PARAGRAFE
    # =====================================================

    for paragraph in paragraphs:

        clean_paragraph = (
            _clean_simple_text(
                paragraph
            )
        )

        if not clean_paragraph:
            continue

        # -------------------------------------------------
        # KEYWORDS
        # -------------------------------------------------

        if _is_keywords_text(
            clean_paragraph
        ):

            keywords_html = (
                _format_simple_keywords(
                    paragraph
                )
            )

            html.append(
                f"<p>{keywords_html}</p>"
            )

            # Spațiere după Keywords
            html.append(
                "<br>"
            )

            continue

        # -------------------------------------------------
        # PARAGRAF NORMAL
        # -------------------------------------------------

        paragraph_html = (
            _format_simple_paragraph(
                paragraph
            )
        )

        html.append(
            f"<p>{paragraph_html}</p>"
        )

    # =====================================================
    # TEXT RĂMAS
    #
    # Aici pot exista fragmente XML care nu au fost
    # încadrate în P/H4/H5/LBody.
    # Le procesăm separat.
    # =====================================================

    remaining_lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # Eliminăm eventualele taguri XML rămase
    # și headere repetate.

    remaining_lines = (
        _remove_repeated_plain_headers(
            remaining_lines
        )
    )

    for line in remaining_lines:

        clean_line = _clean_simple_text(
            line
        )

        if not clean_line:
            continue

        # Nu mai preluăm H2.
        if re.match(
            r"^<h2\b",
            line,
            flags=re.I
        ):
            continue

        # Keywords
        if _is_keywords_text(
            clean_line
        ):

            keywords_html = (
                _format_simple_keywords(
                    line
                )
            )

            html.append(
                f"<p>{keywords_html}</p>"
            )

            html.append(
                "<br>"
            )

            continue

        processed = (
            _format_simple_paragraph(
                line
            )
        )

        html.append(
            f"<p>{processed}</p>"
        )

    return (
        "\n".join(html),
        title
    )


# =========================================================
# ARTICOLE SIMPLE
# KEYWORDS BREAK
#
# Păstrată ca funcție separată pentru compatibilitate
# cu restul aplicației.
# =========================================================

def add_keywords_break(text):

    if not text:
        return ""

    return re.sub(
        r"<p>\s*"
        r"(Keywords|Cuvinte\s+cheie)"
        r"(\s*:?)\s*"
        r"(.*?)"
        r"</p>",
        r"<p><strong>\1\2</strong> \3</p><br>",
        text,
        flags=re.I | re.S
    )


# =========================================================
# ARTICOLE SIMPLE
# BUILD HTML
# =========================================================

def build_simple_html(data):

    # -----------------------------------------------------
    # CONȚINUT XML
    # -----------------------------------------------------

    continut_text = data.get(
        "continut_articol",
        data.get(
            "continut",
            ""
        )
    )

    # -----------------------------------------------------
    # FORMATĂM DOAR ARTICOLUL SIMPLU
    #
    # NU apelăm build_html().
    # NU apelăm funcțiile științifice.
    # -----------------------------------------------------

    continut, xml_title = (
        format_simple_content(
            continut_text
        )
    )

    # -----------------------------------------------------
    # TITLU
    #
    # Primul H4 din XML are prioritate.
    # Dacă nu există, folosim titlul din data.
    # -----------------------------------------------------

    titlu = (
        xml_title
        or data.get(
            "titlu",
            ""
        )
    )

    titlu = (
        titlu or ""
    ).strip()

    # -----------------------------------------------------
    # HTML TITLU
    # -----------------------------------------------------

    titlu_html = superscript_symbols(
        linkify(
            titlu
        )
    )

    # -----------------------------------------------------
    # HTML FINAL
    # -----------------------------------------------------

    return f"""<!DOCTYPE html>

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

</html>"""

