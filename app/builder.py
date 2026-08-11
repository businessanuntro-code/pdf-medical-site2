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

def superscript_simple_author_refs(text):
    """
    Transformă numerele lipite de numele autorilor în superscript.

    Exemple:
        Popescu1
        Popescu<sup>1</sup>

        Popescu1, Ionescu2
        Popescu<sup>1</sup>, Ionescu<sup>2</sup>

        Mihăilă2,3
        Mihăilă<sup>2,3</sup>
    """

    if not text:
        return ""

    return re.sub(
        r"(?<=[A-Za-zĂÂÎȘȚăâîșț\-])"
        r"(\d+(?:,\d+)*)",
        r"<sup>\1</sup>",
        text,
    )


# =========================================================
# UTILE ARTICOLE SIMPLE
# =========================================================

def _clean_simple_text(text):
    """
    Elimină tagurile XML și spațiile inutile.
    """

    if not text:
        return ""

    text = re.sub(
        r"<[^>]+>",
        "",
        text,
    )

    text = text.replace(
        "\u00a0",
        " ",
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def _is_keywords_simple(text):
    """
    Verifică dacă textul este un paragraf Keywords.
    """

    clean = _clean_simple_text(
        text
    )

    return bool(
        re.match(
            r"^(Keywords|Cuvinte\s+cheie)\s*:?",
            clean,
            flags=re.I,
        )
    )


def _is_probable_author_continuation(text):
    """
    Verifică dacă un <P> imediat după H5
    reprezintă o continuare a listei de autori.

    Exemplu:

    <H5>
    Mirela Dumitru1, Mirela Mihăilă2,
    Camelia-Mia Hotnog2, ...
    </H5>

    <P>
    Monica Hortopan3, Gabriela Anton2,
    Lorelei-Irina Braşoveanu2
    </P>

    Al doilea P este continuarea autorilor.

    În schimb:

    <P>
    “Prof. Dr. Alexandru Trestioreanu”
    Institute of Oncology...
    </P>

    este afiliere și NU este autor.
    """

    clean = _clean_simple_text(
        text
    )

    if not clean:
        return False

    # Dacă începe cu o formulare tipică de afiliere,
    # nu este continuare de autori.

    affiliation_starts = (
        "Institute ",
        "Faculty ",
        "University ",
        "Hospital ",
        "Clinical ",
        "Association ",
        "Fundeni ",
        "Neolife ",
        "Cernavodă ",
        "“Prof.",
        '"Prof.',
        "Prof.",
    )

    for prefix in affiliation_starts:

        if clean.startswith(prefix):
            return False

    # O continuare de autori trebuie să conțină
    # cel puțin un număr lipit de un cuvânt/nume.

    if not re.search(
        r"[A-Za-zĂÂÎȘȚăâîșț\-]\d+",
        clean,
    ):
        return False

    # Evităm situația în care un paragraf normal
    # conține doar întâmplător numere.

    words = clean.split()

    if len(words) > 25:
        return False

    return True


def _format_simple_text(text):
    """
    Formatare de bază pentru textul articolelor simple.
    """

    if not text:
        return ""

    text = linkify(
        text
    )

    text = superscript_symbols(
        text
    )

    return text


# =========================================================
# H2
# =========================================================

def _remove_simple_h2(text):
    """
    Pentru articole simple NU preluăm niciun H2.

    H2 sunt headere de pagină / secțiune și pot
    produce duplicări.
    """

    if not text:
        return ""

    return re.sub(
        r"<H2\b[^>]*>.*?</H2\s*>",
        "",
        text,
        flags=re.I | re.S,
    )


# =========================================================
# H4
# =========================================================

def _extract_simple_h4(text):
    """
    Extrage primele două H4.

    Primul H4:
        titlu principal

    Al doilea H4:
        titlu secundar
    """

    titles = []

    pattern = re.compile(
        r"<H4\b[^>]*>(.*?)</H4\s*>",
        flags=re.I | re.S,
    )

    def replace(match):

        content = _clean_simple_text(
            match.group(1)
        )

        if content:
            titles.append(
                content
            )

        return ""

    remaining = pattern.sub(
        replace,
        text,
    )

    return (
        titles,
        remaining,
    )


# =========================================================
# EXTRAGERE ELEMENTE
# =========================================================

def _extract_simple_elements(text):
    """
    Extrage elementele în ordinea lor din XML.

    IMPORTANT:
    Nu mai tratăm toate H5 / LBody / P separat.

    Păstrăm ordinea reală:

        H5
        P
        LBody
        P
        P
        ...

    pentru a putea determina corect rolul fiecărui element.
    """

    elements = []

    pattern = re.compile(
        r"<H5\b[^>]*>.*?</H5\s*>"
        r"|"
        r"<LBody\b[^>]*>.*?</LBody\s*>"
        r"|"
        r"<P\b[^>]*>.*?</P\s*>",
        flags=re.I | re.S,
    )

    for match in pattern.finditer(
        text
    ):

        raw = match.group(0)

        if re.match(
            r"<H5\b",
            raw,
            flags=re.I,
        ):

            elements.append(
                (
                    "H5",
                    raw,
                )
            )

        elif re.match(
            r"<LBody\b",
            raw,
            flags=re.I,
        ):

            elements.append(
                (
                    "LBODY",
                    raw,
                )
            )

        elif re.match(
            r"<P\b",
            raw,
            flags=re.I,
        ):

            elements.append(
                (
                    "P",
                    raw,
                )
            )

    return elements


# =========================================================
# EXTRAGERE TEXT ELEMENT
# =========================================================

def _get_simple_element_text(
    raw,
    tag,
):
    """
    Extrage textul dintr-un H5/LBody/P.
    """

    match = re.search(
        rf"<{tag}\b[^>]*>(.*?)</{tag}\s*>",
        raw,
        flags=re.I | re.S,
    )

    if not match:
        return ""

    return _clean_simple_text(
        match.group(1)
    )


# =========================================================
# PROCESARE ARTICOL SIMPLU
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
    # ELIMINĂM TABELE / FIGURI / IMAGINI
    # -----------------------------------------------------

    text = re.sub(
        r"<table\b.*?</table\s*>",
        "",
        text,
        flags=re.I | re.S,
    )

    text = re.sub(
        r"<figure\b.*?</figure\s*>",
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

    # -----------------------------------------------------
    # H2
    #
    # IMPORTANT:
    # toate H2 sunt eliminate.
    # -----------------------------------------------------

    text = _remove_simple_h2(
        text
    )

    # -----------------------------------------------------
    # H4
    #
    # primul = titlu
    # al doilea = subtitlu
    # -----------------------------------------------------

    h4_titles, text = (
        _extract_simple_h4(
            text
        )
    )

    title = ""

    if h4_titles:

        title = h4_titles[0]

    # -----------------------------------------------------
    # EXTRAGEM ELEMENTELE ÎN ORDINE
    # -----------------------------------------------------

    elements = _extract_simple_elements(
        text
    )

    html = []

    # =====================================================
    # TITLU SECUNDAR
    # =====================================================

    if len(h4_titles) >= 2:

        secondary_title = (
            _format_simple_text(
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
    # STAREA ARTICOLULUI
    # =====================================================

    authors = []

    affiliations = []

    content_started = False

    authors_section_finished = False

    pending_author_p = False

    # =====================================================
    # PARCURGERE ELEMENTE
    # =====================================================

    index = 0

    while index < len(elements):

        element_type, raw = elements[index]

        # =================================================
        # H5 = AUTORI
        # =================================================

        if element_type == "H5":

            author_text = (
                _get_simple_element_text(
                    raw,
                    "H5",
                )
            )

            if author_text:

                authors.append(
                    author_text
                )

                content_started = False

                authors_section_finished = False

                pending_author_p = True

            index += 1

            continue

        # =================================================
        # LBody = AFILIERE
        # =================================================

        if element_type == "LBODY":

            affiliation_text = (
                _get_simple_element_text(
                    raw,
                    "LBody",
                )
            )

            if affiliation_text:

                affiliations.append(
                    affiliation_text
                )

            authors_section_finished = True

            pending_author_p = False

            index += 1

            continue

        # =================================================
        # P
        # =================================================

        if element_type == "P":

            paragraph_text = (
                _get_simple_element_text(
                    raw,
                    "P",
                )
            )

            if not paragraph_text:

                index += 1

                continue

            # =============================================
            # KEYWORDS
            # =============================================

            if _is_keywords_simple(
                paragraph_text
            ):

                content_started = True

                keywords_html = (
                    _format_simple_text(
                        paragraph_text
                    )
                )

                keywords_html = re.sub(
                    r"^(Keywords|Cuvinte\s+cheie)"
                    r"(\s*:?)",
                    lambda m: (
                        "<strong>"
                        f"{m.group(1)}"
                        f"{m.group(2)}"
                        "</strong>"
                    ),
                    keywords_html,
                    count=1,
                    flags=re.I,
                )

                html.append(
                    f"<p>{keywords_html}</p><br>"
                )

                index += 1

                continue

            # =============================================
            # P DUPĂ H5
            #
            # Poate fi:
            #
            # 1. continuare autori
            # 2. afiliere
            # 3. conținut
            # =============================================

            if pending_author_p:

                # -----------------------------------------
                # CONTINUARE AUTORI
                # -----------------------------------------

                if _is_probable_author_continuation(
                    paragraph_text
                ):

                    authors.append(
                        paragraph_text
                    )

                    index += 1

                    continue

                # -----------------------------------------
                # Dacă P nu arată ca autor,
                # considerăm că secțiunea autorilor
                # s-a terminat.
                # -----------------------------------------

                pending_author_p = False

                authors_section_finished = True

                # -----------------------------------------
                # PRIMUL P DUPĂ AUTORI
                #
                # În XML-ul tău poate fi afilierea.
                # -----------------------------------------

                if not content_started:

                    # Dacă nu avem încă LBody și P-ul
                    # pare afiliere, îl punem ca afiliere.

                    affiliation_starts = (
                        "Institute ",
                        "Faculty ",
                        "University ",
                        "Hospital ",
                        "Clinical ",
                        "Association ",
                        "Fundeni ",
                        "Neolife ",
                        "Cernavodă ",
                        "“Prof.",
                        '"Prof.',
                        "Prof.",
                    )

                    is_affiliation = any(
                        paragraph_text.startswith(
                            prefix
                        )
                        for prefix in affiliation_starts
                    )

                    if is_affiliation:

                        affiliations.append(
                            paragraph_text
                        )

                        index += 1

                        continue

            # =============================================
            # P NORMAL
            # =============================================

            content_started = True

            paragraph_html = (
                _format_simple_text(
                    paragraph_text
                )
            )

            html.append(
                f"<p>{paragraph_html}</p>"
            )

            index += 1

            continue

        index += 1

    # =====================================================
    # AUTORI
    #
    # Îi inserăm înaintea afilierilor și textului.
    # =====================================================

    author_html = []

    for author in authors:

        author_processed = (
            superscript_simple_author_refs(
                author
            )
        )

        author_html.append(
            "<strong>"
            f"{author_processed}"
            "</strong>"
        )

    # =====================================================
    # AFILIERI
    # =====================================================

    affiliation_html = []

    for number, affiliation in enumerate(
        affiliations,
        start=1,
    ):

        affiliation_processed = (
            _format_simple_text(
                affiliation
            )
        )

        affiliation_html.append(
            f"<p>"
            f"{number}. "
            f"<i>{affiliation_processed}</i>"
            f"</p>"
        )

    # =====================================================
    # RECONSTRUIM ÎN ORDINEA CORECTĂ
    #
    # Titlu secundar
    # Autori
    # Afiliere
    # Conținut
    # =====================================================

    final_html = []

    # Dacă există titlu secundar, este deja în html,
    # dar autorii trebuie să apară după el.

    # În cazul actual, html conține deja titlul secundar
    # la început.

    if html:

        # primul element poate fi subtitlul
        # îl păstrăm înaintea autorilor.

        if len(h4_titles) >= 2:

            final_html.append(
                html[0]
            )

            remaining_html = html[1:]

        else:

            remaining_html = html

    else:

        remaining_html = []

    # -----------------------------------------------------
    # AUTORI
    # -----------------------------------------------------

    for author in author_html:

        final_html.append(
            f"<p>{author}</p>"
        )

    # -----------------------------------------------------
    # AFILIERI
    # -----------------------------------------------------

    for affiliation in affiliation_html:

        final_html.append(
            affiliation
        )

    # -----------------------------------------------------
    # CONȚINUT
    # -----------------------------------------------------

    final_html.extend(
        remaining_html
    )

    return (
        "\n".join(
            final_html
        ),
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
    # PROCESĂM DOAR ARTICOLUL SIMPLU
    #
    # NU apelăm build_html().
    # -----------------------------------------------------

    continut, xml_title = (
        format_simple_content(
            continut_text
        )
    )

    # -----------------------------------------------------
    # TITLU
    # -----------------------------------------------------

    titlu = (
        xml_title
        or data.get(
            "titlu",
            "",
        )
    )

    titlu = (
        titlu or ""
    ).strip()

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



