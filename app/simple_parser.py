# =========================================================
# SIMPLE PARSER
# HTML → BUILDER
# =========================================================
#
# Pentru ARTICOLE SIMPLE.
#
# Parserul NU interpreteaza continutul.
# Parserul NU identifica:
#   - titluri
#   - autori
#   - afilieri
#   - continut
#   - keywords
#
# Parserul NU modifica HTML-ul.
#
# Citeste fisierul HTML exportat din PDF si transmite
# continutul exact asa cum exista in fisier.
#
# Flux:
#
# PDF
#   ↓
# Export HTML
#   ↓
# simple_parser.py
#   ↓
# HTML original
#   ↓
# simple_builder.py
#   ↓
# DB
#
# =========================================================


# =========================================================
# CITIRE HTML
# =========================================================

def read_html_file(html_path):
    """
    Citeste fisierul HTML exact asa cum exista pe disc.

    NU:
    - curata spatii
    - modifica taguri
    - modifica clase
    - modifica CSS
    - identifica elemente
    - transforma continutul

    Returneaza continutul HTML ca string.
    """

    if not html_path:
        return ""

    with open(
        html_path,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as file:

        return file.read()


# =========================================================
# PARSER PRINCIPAL
# =========================================================

def parse_simple_html(html_path):
    """
    Parser pentru articole simple provenite din HTML
    exportat din PDF.

    HTML-ul este transmis 1:1 catre builder.
    """

    html = read_html_file(
        html_path
    )

    if not html:
        return {
            "type": "simple",
            "html": ""
        }

    return {
        "type": "simple",
        "html": html
    }


# =========================================================
# COMPATIBILITATE
# =========================================================

def parse_simple_xml(xml_path):
    """
    Functie pastrata pentru compatibilitate cu
    simple_main.py / main.py.

    IMPORTANT:

    Desi numele functiei este inca parse_simple_xml(),
    ea citeste continutul fisierului ca TEXT si il
    transmite nemodificat.

    Astfel nu mai folosim ElementTree si nu mai
    interpretam structura XML.
    """

    return parse_simple_html(
        xml_path
    )
