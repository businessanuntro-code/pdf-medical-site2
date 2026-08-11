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


# =========================================================
# =========================================================
# ARTICOLE SIMPLE
# =========================================================
# =========================================================


# =========================================================
# AUTORI SIMPLE
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

    text = re.sub(
        r"<[^>]+>",
        protect,
        text,
    )

    text = re.sub(
        r"(?<=[A-Za-zĂÂÎȘȚăâîșț\-])"
        r"(\d+(?:,\d+)*)",
        r"<sup>\1</sup>",
        text,
    )

    for i, tag in enumerate(
        protected
    ):

        text = text.replace(
            f"___AUTHOR_HTML_{i}___",
            tag,
        )

    return text


# =========================================================
# UTILE SIMPLE
# =========================================================

def _clean_xml_text(text):

    text = re.sub(
        r"<[^>]+>",
        "",
        text or "",
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def _is_keywords_text(text):

    clean = _clean_xml_text(
        text
    )

    return bool(
        re.match(
            r"^(?:Keywords|Cuvinte\s+cheie)\s*:?",
            clean,
            flags=re.I,
        )
    )


# =========================================================
# ELIMINARE H2 DUPLICATE
# =========================================================

def _remove_duplicate_h2(text):

    seen = set()

    def replace(match):

        content = match.group(1)

        key = re.sub(
            r"<[^>]+>",
            "",
            content or "",
        )

        key = re.sub(
            r"\s+",
            " ",
            key,
        ).strip().casefold()

        if not key:
            return match.group(0)

        if key in seen:
            return ""

        seen.add(key)

        return match.group(0)

    return re.sub(
        r"<h2\b[^>]*>(.*?)</h2\s*>",
        replace,
        text,
        flags=re.I | re.S,
    )


# =========================================================
# NU INCEPE ARTICOLUL CU KEYWORDS
# =========================================================

def _remove_leading_keywords(text):

    while True:

        original = text

        # P Keywords...</P>
        text = re.sub(
            r"^\s*"
            r"<p\b[^>]*>\s*"
            r"(?:<[^>]+>\s*)*"
            r"(?:Keywords|Cuvinte\s+cheie)"
            r"\s*:?.*?"
            r"</p\s*>",
            "",
            text,
            count=1,
            flags=re.I | re.S,
        )

        # Linie simpla Keywords...
        text = re.sub(
            r"^\s*"
            r"(?:Keywords|Cuvinte\s+cheie)"
            r"\s*:?[^\n]*",
            "",
            text,
            count=1,
            flags=re.I,
        )

        if text == original:
            break

    return text


# =========================================================
# PRIMUL H4 = TITLU
# =========================================================

def _extract_first_h4(text):

    match = re.search(
        r"<H4\b[^>]*>(.*?)</H4\s*>",
        text,
        flags=re.I | re.S,
    )

    if not match:
        return "", text

    title = _clean_xml_text(
        match.group(1)
    )

    remaining = (
        text[:match.start()]
        + text[match.end():]
    )

    return title, remaining


# =========================================================
# H5 = AUTORI
# =========================================================

def _prepare_simple_h5(match):

    author_text = match.group(
        1
    ).strip()

    author_text = (
        superscript_simple_author_refs(
            author_text
        )
    )

    return (
        "\n"
        "__SIMPLE_AUTHORS__"
        f"<strong>{author_text}</strong>"
        "\n"
    )


# =========================================================
# LBody = AFILIERE
# =========================================================

def _process_simple_lbody(
    match,
    counter,
):

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


# =========================================================
# PROCESARE H5 + LBody
# =========================================================

def _process_simple_sections(text):

    parts = re.split(
        r"(<H5\b[^>]*>.*?</H5\s*>)",
        text,
        flags=re.I | re.S,
    )

    output = []

    in_author_section = False

    affiliation_counter = 0

    for part in parts:

        if not part:
            continue

        # -------------------------------------------------
        # H5 = AUTORI
        # -------------------------------------------------

        if re.match(
            r"<H5\b",
            part,
            flags=re.I,
        ):

            output.append(
                re.sub(
                    r"<H5\b[^>]*>(.*?)</H5\s*>",
                    _prepare_simple_h5,
                    part,
                    flags=re.I | re.S,
                )
            )

            in_author_section = True

            affiliation_counter = 0

            continue

        # -------------------------------------------------
        # DUPA H5 PROCESAM LBody
        # -------------------------------------------------

        if in_author_section:

            def replace_lbody(match):

                nonlocal affiliation_counter

                affiliation_counter += 1

                return _process_simple_lbody(
                    match,
                    affiliation_counter,
                )

            # LBody aflat in LI
            part = re.sub(
                r"<LI>\s*"
                r"<Lbl>.*?</Lbl>\s*"
                r"<LBody>(.*?)</LBody>\s*"
                r"</LI>",
                replace_lbody,
                part,
                flags=re.I | re.S,
            )

            # LBody direct
            def replace_direct_lbody(match):

                nonlocal affiliation_counter

                affiliation_counter += 1

                return _process_simple_lbody(
                    match,
                    affiliation_counter,
                )

            part = re.sub(
                r"<LBody>(.*?)</LBody>",
                replace_direct_lbody,
                part,
                flags=re.I | re.S,
            )

        output.append(
            part
        )

    return "".join(
        output
    )


# =========================================================
# FORMAT CONTENT ARTICOL SIMPLU
# =========================================================

def format_simple_content(text):

    if not text:
        return "", ""

    # -----------------------------------------------------
    # CARACTERE SPECIALE
    # -----------------------------------------------------

    text = text.replace(
        "\u2029",
        "\n",
    )

    # -----------------------------------------------------
    # TAGURI GENERALE
    # -----------------------------------------------------

    text = re.sub(
        r"</?(ContinutArticol|continut_articol|body)[^>]*>",
        "",
        text,
        flags=re.I,
    )

    # -----------------------------------------------------
    # TABELE
    # -----------------------------------------------------

    text = re.sub(
        r"<table\b.*?</table\s*>",
        "",
        text,
        flags=re.I | re.S,
    )

    # -----------------------------------------------------
    # FIGURI
    # -----------------------------------------------------

    text = re.sub(
        r"<figure\b.*?</figure\s*>",
        "",
        text,
        flags=re.I | re.S,
    )

    # -----------------------------------------------------
    # IMAGINI XML
    # -----------------------------------------------------

    text = re.sub(
        r"<imagine\d+[^>]*/?>",
        "",
        text,
        flags=re.I,
    )

    # -----------------------------------------------------
    # H2 DUPLICATE
    # -----------------------------------------------------

    text = _remove_duplicate_h2(
        text
    )

    # -----------------------------------------------------
    # NU INCEPE CU KEYWORDS
    # -----------------------------------------------------

    text = _remove_leading_keywords(
        text
    )

    # -----------------------------------------------------
    # PRIMUL H4 = TITLU
    # -----------------------------------------------------

    title, text = _extract_first_h4(
        text
    )

    # -----------------------------------------------------
    # H5 = AUTORI
    # LBody = AFILIERI
    # -----------------------------------------------------

    text = _process_simple_sections(
        text
    )

    # -----------------------------------------------------
    # H4 URMATOARE = BOLD + ITALIC
    # -----------------------------------------------------

    text = re.sub(
        r"<H4\b[^>]*>(.*?)</H4\s*>",
        r"\n__SIMPLE_H4_ITALIC__\1\n",
        text,
        flags=re.I | re.S,
    )

    # -----------------------------------------------------
    # INTERTITLU
    # -----------------------------------------------------

    text = re.sub(
        r"<Intertitlu>(.*?)</Intertitlu>",
        r"\n<strong>\1</strong>\n",
        text,
        flags=re.I | re.S,
    )

    # -----------------------------------------------------
    # SUB INTERTITLU
    # -----------------------------------------------------

    text = re.sub(
        r"<Sub_Intertitlu>(.*?)</Sub_Intertitlu>",
        r"\n<strong><i>\1</i></strong>\n",
        text,
        flags=re.I | re.S,
    )

    # -----------------------------------------------------
    # INTER STYLE 3
    # -----------------------------------------------------

    text = re.sub(
        r"<INTER_Style_3>(.*?)</INTER_Style_3>",
        r"\n<strong><i>\1</i></strong>\n",
        text,
        flags=re.I | re.S,
    )

    # -----------------------------------------------------
    # Linii
    # -----------------------------------------------------

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    html = []

    for line in lines:

        # =================================================
        # AUTORI
        # =================================================

        if line.startswith(
            "__SIMPLE_AUTHORS__"
        ):

            author_html = line.replace(
                "__SIMPLE_AUTHORS__",
                "",
                1,
            ).strip()

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
            flags=re.I | re.S,
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

            affiliation_text = (
                superscript_symbols(
                    affiliation_text
                )
            )

            html.append(
                f"<p>{number}. "
                f"<i>{affiliation_text}</i>"
                f"</p>"
            )

            continue

        # =================================================
        # H4 SECUNDAR
        # =================================================

        if line.startswith(
            "__SIMPLE_H4_ITALIC__"
        ):

            h4_text = line.replace(
                "__SIMPLE_H4_ITALIC__",
                "",
                1,
            ).strip()

            h4_text = linkify(
                h4_text
            )

            h4_text = (
                superscript_symbols(
                    h4_text
                )
            )

            html.append(
                f"<p><strong><i>"
                f"{h4_text}"
                f"</i></strong></p>"
            )

            continue

        # =================================================
        # PROCESARE TEXT
        # =================================================

        processed = linkify(
            line
        )

        processed = superscript_symbols(
            processed
        )

        # =================================================
        # KEYWORDS
        # =================================================

        keywords_match = re.match(
            r"^(Keywords|Cuvinte\s+cheie)"
            r"(\s*:?)"
            r"(.*)$",
            re.sub(
                r"<[^>]+>",
                "",
                processed,
            ),
            flags=re.I,
        )

        if keywords_match:

            processed = re.sub(
                r"^(Keywords|Cuvinte\s+cheie)"
                r"(\s*:?)",
                lambda m: (
                    f"<strong>"
                    f"{m.group(1)}"
                    f"{m.group(2)}"
                    f"</strong>"
                ),
                processed,
                count=1,
                flags=re.I,
            )

            html.append(
                f"<p>{processed}</p><br>"
            )

            continue

        # =================================================
        # H2
        # =================================================

        h2_match = re.match(
            r"<h2\b[^>]*>(.*?)</h2\s*>$",
            processed,
            flags=re.I | re.S,
        )

        if h2_match:

            h2_text = h2_match.group(
                1
            ).strip()

            html.append(
                f"<h2>{h2_text}</h2>"
            )

            continue

        # =================================================
        # P / p
        # =================================================

        p_match = re.match(
            r"<p\b[^>]*>(.*?)</p\s*>$",
            processed,
            flags=re.I | re.S,
        )

        if p_match:

            html.append(
                f"<p>{p_match.group(1)}</p>"
            )

        else:

            html.append(
                f"<p>{processed}</p>"
            )

    return (
        "\n".join(html),
        title,
    )


# =========================================================
# KEYWORDS BREAK
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
        flags=re.I | re.S,
    )


# =========================================================
# ARTICOLE SIMPLE
# BUILD HTML
# =========================================================

def build_simple_html(data):

    continut_text = data.get(
        "continut_articol",
        data.get(
            "continut",
            "",
        ),
    )

    # -----------------------------------------------------
    # FORMATAM DOAR ARTICOLUL SIMPLU
    # -----------------------------------------------------

    continut, xml_title = (
        format_simple_content(
            continut_text
        )
    )

    # -----------------------------------------------------
    # PRIMUL H4 DIN XML ESTE TITLUL
    # -----------------------------------------------------

    titlu = (
        xml_title
        or data.get(
            "titlu",
            "",
        )
    )

    titlu = (
        titlu
        or ""
    ).strip()

    # -----------------------------------------------------
    # KEYWORDS
    # -----------------------------------------------------

    continut = add_keywords_break(
        continut
    )

    # -----------------------------------------------------
    # TITLU HTML
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
