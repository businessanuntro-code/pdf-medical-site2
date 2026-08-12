import xml.etree.ElementTree as ET
import re


# =========================================================
# UTILITARE
# =========================================================

def tag_name(element):
    """
    Returneaza numele tagului fara namespace.
    """

    return element.tag.split("}")[-1]


def clean_text(text):
    """
    Curata doar spatiile tehnice.
    
    NU interpreteaza continutul.
    NU identifica titluri.
    NU identifica autori.
    NU identifica afilieri.
    NU identifica keywords.
    """

    if not text:
        return ""

    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def element_text(element):
    """
    Returneaza tot textul continut de element,
    inclusiv textul elementelor copil.

    Continutul este pastrat in ordinea XML.
    """

    if element is None:
        return ""

    return clean_text(
        "".join(
            element.itertext()
        )
    )


# =========================================================
# XML → ELEMENTE
# =========================================================

def extract_xml_elements(root):
    """
    Extrage elementele relevante din XML in ORDINEA EXACTA
    in care apar in document.

    Parserul NU interpreteaza continutul.

    El transmite doar:

        tag
        text

    catre builder.
    """

    elements = []

    for element in root.iter():

        tag = tag_name(element)

        # -------------------------------------------------
        # Pastram doar elementele care ne intereseaza
        # pentru afisarea articolului.
        # -------------------------------------------------

        if tag not in (
            "H1",
            "H2",
            "H3",
            "H4",
            "H5",
            "P",
            "Footnote",
            "L",
            "LI",
            "Lbl",
            "LBody"
        ):
            continue

        text = element_text(element)

        if not text:
            continue

        # -------------------------------------------------
        # Pentru fiecare element pastram exact:
        #
        # tag
        # text
        #
        # Nu cream title_en.
        # Nu cream title_ro.
        # Nu cream authors.
        # Nu cream affiliations.
        # Nu cream keywords.
        # -------------------------------------------------

        elements.append({
            "tag": tag,
            "text": text
        })

    return elements


# =========================================================
# PARSER PRINCIPAL
# =========================================================

def parse_simple_xml(xml_path):
    """
    Parser pentru ARTICOLE SIMPLE.

    IMPORTANT:

    Parserul NU interpreteaza structura articolului.

    Nu incearca sa stabileasca:
        - care este titlul
        - care este titlul RO
        - care sunt autorii
        - care sunt afilierile
        - care este continutul
        - care sunt keywords

    El doar citeste XML-ul si transmite elementele
    in ordinea in care apar.

    Interpretarea si formatarea se fac exclusiv
    in simple_builder.py.
    """

    try:

        tree = ET.parse(
            xml_path
        )

        root = tree.getroot()

    except ET.ParseError as exc:

        raise ValueError(
            f"XML invalid sau imposibil de procesat: {exc}"
        ) from exc


    # =====================================================
    # EXTRAGEM TOT IN ORDINEA XML
    # =====================================================

    elements = extract_xml_elements(
        root
    )


    # =====================================================
    # REZULTAT
    # =====================================================

    return {
        "type": "simple",

        "elements": elements
    }
