
import re
from html import escape


# =========================================================
# FUNCTII GENERALE - ARTICOLE SIMPLE
# =========================================================

def clean_text(text):
    """Normalizeaza spatiile dintr-un text."""

    if not text:
        return ""

    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def escape_html(text):
    """Protejeaza textul pentru HTML."""

    return escape(clean_text(text))


def simple_styles():
    """
    Stiluri folosite EXCLUSIV pentru articolele simple.
    """

    return """
    <style>

        .simple-title-en {
            margin-top: 0;
            margin-bottom: 0;
        }

        .simple-title-ro {
            margin-top: 0;
            margin-bottom: 0;
            font-style: italic;
        }

        .simple-authors {
            margin-top: 0;
            margin-bottom: 0;
        }

        .simple-affiliations {
            margin-top: 0;
            margin-bottom: 0;
        }

        .simple-affiliation {
            font-style: italic;
            margin-top: 0;
            margin-bottom: 0;
        }

        .simple-paragraph {
            margin-top: 0;
            margin-bottom: 1em;
        }

        .simple-keywords {
            margin-top: 0;
            margin-bottom: 0;
            padding-top: 0;
            padding-bottom: 0;
        }

    </style>
    """


# =========================================================
# AUTORI - ARTICOLE SIMPLE
# =========================================================

def format_author_numbers(text):
    """
    Transforma numerele asociate autorilor in superscript.

    Exemple:

    Autor1
    Autor1,2
    Autor1,2,3

    devin:

    Autor<sup>1</sup>
    Autor<sup>1,2</sup>
    Autor<sup>1,2,3</sup>

    Regula se aplica DOAR in zona autorilor.
    """

    if not text:
        return ""

    text = escape_html(text)

    text = re.sub(
        r"(?<=[A-Za-zÀ-ÖØ-öø-ÿĂăÂâÎîȘșŞşȚțŢţ\-])"
        r"(\d+(?:\s*,\s*\d+)*)",
        lambda match: f"<sup>{match.group(1)}</sup>",
        text
    )

    return text


def format_authors(authors):
    """
    Afiseaza autorii cu bold.
    Numerele autorilor sunt superscript.
    """

    if not authors:
        return ""

    formatted = format_author_numbers(authors)

    return (
        '<div class="simple-authors">'
        f"<strong>{formatted}</strong>"
        "</div>"
    )


# =========================================================
# AFILIERI - ARTICOLE SIMPLE
# =========================================================

def format_affiliations(affiliations):
    """
    Formateaza afilierile.

    Numerotarea incepe de la 1 pentru fiecare articol.
    Afilierile sunt afisate italic.
    """

    if not affiliations:
        return ""

    html = []

    html.append(
        '<div class="simple-affiliations">'
    )

    for index, affiliation in enumerate(
        affiliations,
        start=1
    ):

        if isinstance(affiliation, dict):
            text = affiliation.get(
                "text",
                ""
            )
        else:
            text = affiliation

        text = escape_html(text)

        if not text:
            continue

        html.append(
            '<div class="simple-affiliation">'
            f'<span class="affiliation-number">'
            f'{index}.'
            f'</span> '
            f"{text}"
            "</div>"
        )

    html.append(
        "</div>"
    )

    return "\n".join(html)


# =========================================================
# KEYWORDS - ARTICOLE SIMPLE
# =========================================================

def format_keywords(keywords):
    """
    Formateaza Keywords.

    Keywords: este bold.

    NU folosim <p> si NU folosim <br>,
    pentru a evita spatiul vertical suplimentar.
    """

    if not keywords:
        return ""

    keywords = escape_html(keywords)

    return (
        '<div class="simple-keywords">'
        '<strong>Keywords:</strong> '
        f'{keywords}'
        '</div>'
    )


# =========================================================
# PARAGRAFE - ARTICOLE SIMPLE
# =========================================================

def format_paragraphs(paragraphs):
    """
    Transforma paragrafele articolului in elemente <p>.
    """

    if not paragraphs:
        return ""

    html = []

    for paragraph in paragraphs:

        paragraph = clean_text(
            paragraph
        )

        if not paragraph:
            continue

        # Keywords este tratat separat.
        if re.match(
            r"^(?:Keywords|Cuvinte\s+cheie)\s*:",
            paragraph,
            flags=re.IGNORECASE
        ):
            continue

        html.append(
            '<p class="simple-paragraph">'
            f"{escape_html(paragraph)}"
            "</p>"
        )

    return "\n".join(html)


# =========================================================
# CONSTRUIRE UN ARTICOL SIMPLU
# =========================================================

def build_simple_article(article):
    """
    Construieste HTML-ul pentru un singur articol simplu.
    """

    if not article:
        return ""

    title_en = clean_text(
        article.get(
            "title_en",
            ""
        )
    )

    title_ro = clean_text(
        article.get(
            "title_ro",
            ""
        )
    )

    authors = article.get(
        "authors",
        ""
    )

    affiliations = article.get(
        "affiliations",
        []
    )

    paragraphs = article.get(
        "paragraphs",
        []
    )

    keywords = article.get(
        "keywords",
        ""
    )

    html = []

    # -----------------------------------------------------
    # CSS - ARTICOLE SIMPLE
    # -----------------------------------------------------

    html.append(
        simple_styles()
    )

    html.append(
        '<article class="simple-article">'
    )

    # -----------------------------------------------------
    # TITLU ENGLEZA
    # -----------------------------------------------------

    if title_en:

        html.append(
            '<h4 class="simple-title-en">'
            f"{escape_html(title_en)}"
            "</h4>"
        )

    # -----------------------------------------------------
    # TITLU ROMANA
    # -----------------------------------------------------

    if title_ro:

        html.append(
            '<h4 class="simple-title-ro">'
            f"{escape_html(title_ro)}"
            "</h4>"
        )

    # -----------------------------------------------------
    # AUTORI
    # -----------------------------------------------------

    if authors:

        html.append(
            format_authors(
                authors
            )
        )

    # -----------------------------------------------------
    # AFILIERI
    # -----------------------------------------------------

    if affiliations:

        html.append(
            format_affiliations(
                affiliations
            )
        )

    # -----------------------------------------------------
    # CONTINUT
    # -----------------------------------------------------

    content_html = format_paragraphs(
        paragraphs
    )

    if content_html:

        html.append(
            content_html
        )

    # -----------------------------------------------------
    # KEYWORDS
    # -----------------------------------------------------

    keywords_html = format_keywords(
        keywords
    )

    if keywords_html:

        html.append(
            keywords_html
        )

    # -----------------------------------------------------
    # FINAL ARTICOL
    # -----------------------------------------------------

    html.append(
        "</article>"
    )

    return "\n".join(html)


# =========================================================
# BUILDER PRINCIPAL - ARTICOLE SIMPLE
# =========================================================

def build_simple_html(data):
    """
    Builder principal pentru articole simple.

    NU foloseste build_html() din builder.py.

    NU foloseste functiile articolelor stiintifice.

    Proceseaza exclusiv datele produse
    de simple_parser.py.
    """

    if not data:
        return ""

    articles = data.get(
        "articles",
        []
    )

    # -----------------------------------------------------
    # COMPATIBILITATE CU UN SINGUR ARTICOL
    # -----------------------------------------------------

    if not articles:

        articles = [
            data
        ]

    html = []

    html.append(
        '<div class="simple-articles">'
    )

    for article in articles:

        article_html = build_simple_article(
            article
        )

        if not article_html:
            continue

        html.append(
            article_html
        )

    html.append(
        "</div>"
    )

    return "\n".join(html)

