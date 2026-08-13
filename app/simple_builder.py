# =========================================================
# SIMPLE BUILDER
# =========================================================
#
# Pentru articole simple:
#
# HTML exportat din PDF
#        ↓
# simple_parser.py
#        ↓
# simple_builder.py
#        ↓
# continut HTML
#
# Builderul NU:
# - identifica titluri
# - identifica autori
# - identifica afilieri
# - identifica Keywords
# - modifica bold
# - modifica italic
# - modifica superscript
# - modifica fonturi
# - modifica spatierea
# - reconstruieste HTML-ul
#
# Tot HTML-ul primit de la parser este pastrat.
# =========================================================


def build_simple_html(data):
    """
    Primeste HTML-ul exportat din PDF si il returneaza
    fara modificari.

    Parserul este responsabil doar de citirea fisierului.
    Builderul este responsabil doar de transmiterea
    continutului mai departe.
    """

    if not data:
        return ""

    html = data.get(
        "html",
        ""
    )

    if not html:
        return ""

    return html
