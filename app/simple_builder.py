import re
from html import escape


# =========================================================
# FUNCTII GENERALE
# =========================================================

def clean_text(text):
    """
    Normalizeaza doar spatiile.
    Nu modifica informatia primita din parser.
    """

    if not text:
        return ""

    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def escape_html(text):
    """
    Protejeaza textul pentru HTML.
    """

    return escape(
        clean_text(text)
    )


# =========================================================
# CONTINUT
# =========================================================

def format_content(text):
    """
    Regula pentru continut:

    - text normal
    - fara bold
    - fara italic
    - fara superscript
    """

    if not text:
        return ""

    return (
        '<p class="simple-paragraph" '
        'style="font-weight: normal !important; '
        'font-style: normal !important;">'
        f"{escape_html(text)}"
        "</p>"
    )


# =========================================================
# BUILDER
# =========================================================

def build_simple_html(data):
    """
    Afiseaza informatia primita de la simple_parser.py.

    Parserul ramane responsabil doar de extragerea
    informatiilor din XML.

    Builderul incepe sa aplice stilizarea treptat.
    """

    if not data:
        return ""

    elements = data.get(
        "elements",
        []
    )

    if not elements:
        return ""

    html = []

    html.append(
        '<div class="simple-articles">'
    )

    for element in elements:

        if not isinstance(element, dict):
            continue

        tag = element.get(
            "tag",
            ""
        )

        text = element.get(
            "text",
            ""
        )

        if not text:
            continue

        # -------------------------------------------------
        # CONTINUT
        # -------------------------------------------------

        if tag == "P":

            html.append(
                format_content(text)
            )

        # -------------------------------------------------
        # RESTUL ELEMENTELOR
        # -------------------------------------------------
        #
        # Pentru moment NU aplicam nicio stilizare.
        # Le afisam exact ca text.
        #

        else:

            html.append(
                escape_html(text)
            )

    html.append(
        "</div>"
    )

    return "\n".join(html)
