import re
from html import escape


# =========================================================
# FUNCTII GENERALE
# =========================================================

def clean_text(text):
    """Normalizeaza spatiile fara a schimba continutul."""

    if not text:
        return ""

    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def escape_html(text):
    """Protejeaza textul pentru HTML."""

    return escape(clean_text(text))


# =========================================================
# CSS - ARTICOLE SIMPLE
# =========================================================

def title_style():
    return """
    <style>
        .simple-title-en {
            margin-top: 0;
            margin-bottom: 0;
            font-weight: bold;
        }

        .simple-title-ro {
            margin-top: 0;
            margin-bottom: 0;
            font-weight: bold;
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
            margin: 0;
        }

        .simple-paragraph {
            margin-top: 0;
            margin-bottom: 10px;
        }

        .simple-keywords {
            margin-top: 0;
            margin-bottom: 0;
        }
    </style>
    """


# =========================================================
# AUTORI
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


def format_authors(text):
    """Afiseaza autorii bold cu numere superscript."""

    if not text:
        return ""

    formatted = format_author_numbers(text)

    return (
        '<div class="simple-authors">'
        f"<strong>{formatted}</strong>"
        "</div>"
    )


# =========================================================
# KEYWORDS
# =========================================================

def is_keywords(text):
    """Verifica daca textul este un bloc Keywords."""

    if not text:
        return False

    normalized = clean_text(text).lower()

    return (
        normalized.startswith("keywords:")
        or normalized.startswith("keywords :")
        or normalized.startswith("cuvinte cheie:")
        or normalized.startswith("cuvinte cheie :")
    )


def format_keywords(text):
    """
    Afiseaza Keywords.

    Keywords: este bold.
    Sunt eliminate spatiile inutile dintre eticheta
    Keywords: si continut.
    """

    if not text:
        return ""

    text = clean_text(text)

    match = re.match(
        r"^\s*(Keywords|Cuvinte\s+cheie)\s*:\s*(.*)$",
        text,
        flags=re.IGNORECASE
    )

    if match:

        label = match.group(1)
        value = match.group(2)

        return (
            '<p class="simple-keywords">'
            f"<strong>{escape_html(label)}:</strong>"
            f" {escape_html(value)}"
            "</p>"
            "<br><br>"
        )

    return (
        '<p class="simple-keywords">'
        f"<strong>{escape_html(text)}</strong>"
        "</p>"
        "<br><br>"
    )


# =========================================================
# AFILIERI
# =========================================================

def format_affiliation(text, counter):
    """
    Afiseaza o afiliere italic.

    Daca XML-ul contine deja numarul:
        1. Institute...

    numarul original este pastrat.

    Daca nu exista:
        se adauga numarul primit prin counter.
    """

    if not text:
        return ""

    text = clean_text(text)

    # -----------------------------------------------------
    # Daca exista deja numerotare in XML
    # -----------------------------------------------------

    match = re.match(
        r"^\s*(\d+)\s*\.\s*(.*)$",
        text
    )

    if match:

        number = match.group(1)
        value = match.group(2)

    else:

        number = str(counter)
        value = text

    return (
        '<div class="simple-affiliation">'
        f'<span class="affiliation-number">'
        f"{escape_html(number)}."
        f"</span> "
        f"{escape_html(value)}"
        "</div>"
    )


# =========================================================
# LISTA AFILIERI
# =========================================================

def format_list_affiliations(element, counter):
    """
    Proceseaza un element L care contine LI.
    """

    html = []

    items = element.get("items", [])

    for item in items:

        text = item.get("text", "")

        if not text:
            continue

        html.append(
            format_affiliation(
                text,
                counter
            )
        )

        counter += 1

    return "\n".join(html), counter


# =========================================================
# FOOTNOTE
# =========================================================

def format_footnote(text, counter):
    """
    Afiseaza o afiliere de tip Footnote.
    """

    if not text:
        return "", counter

    return (
        format_affiliation(
            text,
            counter
        ),
        counter + 1
    )


# =========================================================
# TITLURI
# =========================================================

def format_title_en(text):
    """Primul titlu - bold."""

    if not text:
        return ""

    return (
        '<h4 class="simple-title-en">'
        f"{escape_html(text)}"
        "</h4>"
    )


def format_title_ro(text):
    """Al doilea titlu - bold + italic."""

    if not text:
        return ""

    return (
        '<h4 class="simple-title-ro">'
        f"{escape_html(text)}"
        "</h4>"
    )


# =========================================================
# PARAGRAF
# =========================================================

def format_paragraph(text):
    """Afiseaza un paragraf normal."""

    if not text:
        return ""

    return (
        '<p class="simple-paragraph">'
        f"{escape_html(text)}"
        "</p>"
    )


# =========================================================
# DETECTARE AUTORI
# =========================================================

def looks_like_authors(text):
    """
    Detecteaza un bloc care seamana cu autori.

    Este folosit doar daca XML-ul nu foloseste H3/H5.
    """

    if not text:
        return False

    text = clean_text(text)

    # Trebuie sa existe cel putin o virgula
    # intre doua nume.
    if "," not in text:
        return False

    # Evitam blocurile evidente de continut.
    lower = text.lower()

    forbidden = [
        "introduction.",
        "objective.",
        "materials and method.",
        "results.",
        "conclusions.",
        "keywords:",
        "cuvinte cheie:"
    ]

    for word in forbidden:

        if word in lower:
            return False

    # Numele autorilor sunt relativ scurte.
    if len(text) > 500:
        return False

    return True


# =========================================================
# CONSTRUIRE ARTICOL
# =========================================================

def build_simple_article(article):
    """
    Construieste articolul folosind structura XML
    pastrata de simple_parser.py.

    IMPORTANT:

    Nu mai reconstruim articolul din:
        title_en
        title_ro
        paragraphs

    ci folosim:

        article["elements"]

    care pastreaza ordinea XML-ului.
    """

    if not article:
        return ""

    elements = article.get(
        "elements",
        []
    )

    if not elements:
        return ""

    html = []

    html.append(
        '<article class="simple-article">'
    )

    html.append(
        title_style()
    )

    # -----------------------------------------------------
    # STARE
    # -----------------------------------------------------

    title_count = 0

    authors_found = False

    affiliation_counter = 1

    # -----------------------------------------------------
    # PARCURGEM EXACT ORDINEA XML-ULUI
    # -----------------------------------------------------

    for element in elements:

        tag = element.get(
            "tag",
            ""
        )

        text = clean_text(
            element.get(
                "text",
                ""
            )
        )

        # =================================================
        # H1
        # =================================================

        if tag == "H1":

            if not text:
                continue

            title_count += 1

            # Primul H1 = titlu EN
            if title_count == 1:

                html.append(
                    format_title_en(text)
                )

            # Orice H1 ulterior
            # este tratat ca titlu nou
            else:

                html.append(
                    format_title_en(text)
                )

        # =================================================
        # H2
        # =================================================

        elif tag == "H2":

            if not text:
                continue

            title_count += 1

            # Daca exista deja un titlu,
            # H2 este tratat ca titlu RO.
            html.append(
                format_title_ro(text)
            )

        # =================================================
        # H3
        # =================================================

        elif tag == "H3":

            if not text:
                continue

            # In AutoTag-ul furnizat de tine,
            # H3 = autori.
            if not authors_found:

                html.append(
                    format_authors(text)
                )

                authors_found = True

            else:

                # Daca exista un H3 ulterior,
                # il afisam ca text normal.
                html.append(
                    format_paragraph(text)
                )

        # =================================================
        # H4
        # =================================================

        elif tag == "H4":

            if not text:
                continue

            # H4 poate fi afiliere in XML AutoTag.
            html.append(
                format_affiliation(
                    text,
                    affiliation_counter
                )
            )

            affiliation_counter += 1

        # =================================================
        # H5
        # =================================================

        elif tag == "H5":

            if not text:
                continue

            # H5 poate fi:
            # - autori
            # - Keywords
            # - alt text editorial

            if is_keywords(text):

                html.append(
                    format_keywords(text)
                )

            elif not authors_found and looks_like_authors(text):

                html.append(
                    format_authors(text)
                )

                authors_found = True

            else:

                html.append(
                    format_paragraph(text)
                )

        # =================================================
        # FOOTNOTE
        # =================================================

        elif tag == "Footnote":

            if not text:
                continue

            affiliation_html, affiliation_counter = (
                format_footnote(
                    text,
                    affiliation_counter
                )
            )

            if affiliation_html:

                html.append(
                    affiliation_html
                )

        # =================================================
        # LISTA AFILIERI
        # =================================================

        elif tag == "L":

            affiliation_html, affiliation_counter = (
                format_list_affiliations(
                    element,
                    affiliation_counter
                )
            )

            if affiliation_html:

                html.append(
                    affiliation_html
                )

        # =================================================
        # PARAGRAF
        # =================================================

        elif tag == "P":

            if not text:
                continue

            # ---------------------------------------------
            # Keywords
            # ---------------------------------------------

            if is_keywords(text):

                html.append(
                    format_keywords(text)
                )

                continue

            # ---------------------------------------------
            # Autori fallback
            # ---------------------------------------------

            if (
                not authors_found
                and looks_like_authors(text)
            ):

                html.append(
                    format_authors(text)
                )

                authors_found = True

                continue

            # ---------------------------------------------
            # Continut normal
            # ---------------------------------------------

            html.append(
                format_paragraph(text)
            )

    # -----------------------------------------------------
    # FINAL
    # -----------------------------------------------------

    html.append(
        "</article>"
    )

    return "\n".join(html)


# =========================================================
# BUILDER PRINCIPAL
# =========================================================

def build_simple_html(data):
    """
    Builder principal pentru articole simple.

    Foloseste structura:
        data["articles"][...]["elements"]

    Nu foloseste builder.py.
    Nu modifica fluxul articolelor stiintifice.
    """

    if not data:
        return ""

    articles = data.get(
        "articles",
        []
    )

    # -----------------------------------------------------
    # Compatibilitate cu un singur articol
    # -----------------------------------------------------

    if not articles:

        if data.get("elements"):

            articles = [
                data
            ]

        else:

            return ""

    html = []

    html.append(
        '<div class="simple-articles">'
    )

    # -----------------------------------------------------
    # Fiecare articol
    # -----------------------------------------------------

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
