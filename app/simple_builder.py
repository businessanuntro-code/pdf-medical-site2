from html import escape


# =========================================================
# SIMPLE BUILDER
# =========================================================
#
# Afiseaza 1:1 elementele primite de la simple_parser.py.
#
# NU aplica:
# - stiluri
# - bold
# - italic
# - superscript
# - numerotare
# - Keywords formatting
# - <br> suplimentare
# - interpretare
# - reordonare
#
# =========================================================


def build_simple_html(data):
    """
    Construieste HTML-ul pentru articole simple.

    Afiseaza elementele exact in ordinea in care
    au fost trimise de simple_parser.py.
    """

    if not data:
        return ""

    elements = data.get("elements", [])

    if not elements:
        return ""

    html = []

    for element in elements:

        tag = element.get("tag", "")
        text = element.get("text", "")

        if not text:
            continue

        # -------------------------------------------------
        # Afisam textul exact primit.
        # -------------------------------------------------

        text = escape(text)

        # -------------------------------------------------
        # Folosim tagul original.
        #
        # H1 ramane H1
        # H2 ramane H2
        # H3 ramane H3
        # H4 ramane H4
        # H5 ramane H5
        # P ramane P
        # -------------------------------------------------

        if tag in (
            "H1",
            "H2",
            "H3",
            "H4",
            "H5",
            "P"
        ):

            html.append(
                f"<{tag}>{text}</{tag}>"
            )

        # -------------------------------------------------
        # Pentru celelalte elemente folosim un div simplu.
        #
        # Nu aplicam niciun stil.
        # -------------------------------------------------

        else:

            html.append(
                f"<div>{text}</div>"
            )

    return "\n".join(html)
