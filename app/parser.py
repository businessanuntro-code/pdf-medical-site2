from lxml import etree
import re
from collections import Counter


# =========================================================
# FUNCȚIE GENERALĂ
# =========================================================


def _text(el):

    if el is None:
        return ""

    return " ".join(
        el.itertext()
    ).strip()


# =========================================================
# =========================================================
# ARTICOLE ȘTIINȚIFICE
# PARSER EXISTENT
# =========================================================


def parse_xml(path):

    tree = etree.parse(path)
    root = tree.getroot()

    data = {
        "titlu": "",
        "english_title": "",
        "autor": "",
        "abstract": "",
        "keywords_eng": "",
        "rezumat": "",
        "keywords_rom": "",
        "continut_articol": "",
        "corespondent": "",
        "primit": "",
        "acceptat": "",
        "conflict": "",
        "financial_support": "",
        "cc_by": "",
        "bibliografie": "",
    }

    # =====================================================
    # CAMPURI SIMPLE
    # =====================================================

    if root.find(".//TITLU") is not None:

        data["titlu"] = _text(
            root.find(".//TITLU")
        )

    if root.find(".//English_Title") is not None:

        data["english_title"] = _text(
            root.find(".//English_Title")
        )

    if root.find(".//Autor") is not None:

        autori = []

        for a in root.findall(".//Autor"):

            t = _text(a)

            if t:
                autori.append(t)

        data["autor"] = ", ".join(
            autori
        )

    if root.find(".//Abstract") is not None:

        data["abstract"] = _text(
            root.find(".//Abstract")
        )

    if root.find(".//Keywords_ENG") is not None:

        data["keywords_eng"] = _text(
            root.find(".//Keywords_ENG")
        )

    if root.find(".//Rezumat") is not None:

        data["rezumat"] = _text(
            root.find(".//Rezumat")
        )

    if root.find(".//Keywords_ROM") is not None:

        data["keywords_rom"] = _text(
            root.find(".//Keywords_ROM")
        )

    # =====================================================
    # CORESPONDENT / PRIMIT / ACCEPTAT
    # =====================================================

    for c in root.findall(".//Corespondent"):

        txt = _text(c)

        if txt.startswith("Primit"):

            data["primit"] = txt

            continue

        if txt.startswith("Acceptat"):

            data["acceptat"] = txt

            continue

        if not data["corespondent"]:

            data["corespondent"] = txt

    # =====================================================
    # CONTINUT ARTICOL
    # =====================================================

    stories = root.findall(".//Story")

    collecting = False

    body = []

    for story in stories:

        xml = etree.tostring(
            story,
            encoding="unicode"
        )

        if "<Keywords_ROM>" in xml:

            collecting = True

            continue

        if not collecting:

            continue

        if "<Corespondent>Primit:" in xml:

            break

        body.append(xml)

    data["continut_articol"] = "\n".join(
        body
    )

    # =====================================================
    # BIBLIOGRAFIE
    # =====================================================

    collecting = False

    refs = []

    for story in stories:

        xml = etree.tostring(
            story,
            encoding="unicode"
        )

        if (
            "<_No_paragraph_style_>Bibliografie"
            "</_No_paragraph_style_>"
            in xml
        ):

            collecting = True

            continue

        if not collecting:

            continue

        if "<Sect>" in xml:

            break

        if "<LBody>" in xml:

            node = etree.fromstring(
                xml
            )

            for ref in node.findall(
                ".//LBody"
            ):

                txt = _text(ref)

                if txt:

                    refs.append(txt)

    data["bibliografie"] = "\n".join(
        refs
    )

    # =====================================================
    # CONFLICT DE INTERESE /
    # SUPORT FINANCIAR / CC-BY
    # =====================================================

    for story in stories:

        xml = etree.tostring(
            story,
            encoding="unicode"
        )

        if "<NormalParagraphStyle>" not in xml:

            continue

        node = etree.fromstring(
            xml
        )

        for p in node.findall(
            ".//NormalParagraphStyle"
        ):

            txt = _text(p)

            if (
                txt.startswith(
                    "CONFLICT DE INTERESE"
                )
                or
                txt.startswith(
                    "Conflict of interest"
                )
            ):

                data["conflict"] = txt

            elif (
                txt.startswith(
                    "SUPORT FINANCIAR"
                )
                or
                txt.startswith(
                    "Financial support"
                )
            ):

                data["financial_support"] = txt

            elif "CC-BY" in txt:

                data["cc_by"] = txt

    return data


# =========================================================
# =========================================================
# ARTICOLE SIMPLE
# FUNCȚII SPECIFICE
# =========================================================


def _simple_clean_text(text):

    """
    Curăță un fragment XML pentru comparații.

    Elimină tagurile XML și normalizează spațiile.
    """

    if not text:
        return ""

    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# ARTICOLE SIMPLE
# ELIMINARE H2
# =========================================================


def _simple_remove_h2(text):

    """
    Elimină COMPLET toate elementele H2
    din articolele simple.

    Exemple acceptate:

    <H2>Text</H2>

    <H2 id="123">Text</H2>

    <H2 class="titlu">Text</H2>

    Inclusiv H2 cu spații sau linii noi.
    """

    if not text:
        return ""

    return re.sub(
        r"<H2\b[^>]*>.*?</H2\s*>",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )


# =========================================================
# ARTICOLE SIMPLE
# AUTORI H5
# =========================================================


def _simple_process_authors(text):

    """
    H5 = autori.

    Reguli:

    - autorii sunt bold;
    - numerele de lângă autori sunt superscript.

    Exemplu:

    Iris-Iuliana Adam1, Alina Ormenișan2

    devine:

    <strong>
    Iris-Iuliana Adam<sup>1</sup>,
    Alina Ormenișan<sup>2</sup>
    </strong>
    """

    if not text:
        return ""

    def replace_h5(match):

        author_text = match.group(1)

        # -------------------------------------------------
        # NUMERELE AUTORILOR
        # -------------------------------------------------

        author_text = re.sub(
            r"(?<=[A-Za-zĂÂÎȘȚăâîșț\-])"
            r"(\d+(?:,\d+)*)"
            r"(?=\s*(?:,|;|$))",
            r"<sup>\1</sup>",
            author_text
        )

        # -------------------------------------------------
        # BOLD
        # -------------------------------------------------

        return (
            "<H5>"
            "<strong>"
            + author_text
            + "</strong>"
            "</H5>"
        )

    return re.sub(
        r"<H5\b[^>]*>(.*?)</H5\s*>",
        replace_h5,
        text,
        flags=re.IGNORECASE | re.DOTALL
    )


# =========================================================
# ARTICOLE SIMPLE
# AFILIERI
# =========================================================


def _simple_process_affiliations(text):

    """
    Procesează afiliările din LI/LBody.

    Reguli:

    1. afiliere
    2. afiliere
    3. afiliere

    Numerotarea se resetează la fiecare H5.

    Afilierea este italic.
    """

    if not text:
        return ""

    # -----------------------------------------------------
    # Împărțim documentul după H5.
    #
    # H5-ul marchează începutul unui nou grup
    # de autori și, implicit, resetarea numerotării.
    # -----------------------------------------------------

    parts = re.split(
        r"(<H5\b[^>]*>.*?</H5\s*>)",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    result = []

    counter = 0

    for part in parts:

        # -------------------------------------------------
        # H5
        # -------------------------------------------------

        if re.match(
            r"<H5\b",
            part,
            flags=re.IGNORECASE
        ):

            # RESETARE
            counter = 0

            result.append(
                part
            )

            continue

        # -------------------------------------------------
        # LI / LBody
        # -------------------------------------------------

        def replace_li(match):

            nonlocal counter

            counter += 1

            affiliation_text = (
                match.group(1)
                .strip()
            )

            return (
                "\n"
                "<p>"
                "<i>"
                f"{counter}. "
                f"{affiliation_text}"
                "</i>"
                "</p>"
                "\n"
            )

        part = re.sub(
            r"<LI\b[^>]*>"
            r"\s*"
            r"(?:"
            r"<Lbl\b[^>]*>.*?</Lbl>"
            r"\s*"
            r")?"
            r"<LBody\b[^>]*>"
            r"(.*?)"
            r"</LBody\s*>"
            r"\s*"
            r"</LI\s*>",
            replace_li,
            part,
            flags=re.IGNORECASE | re.DOTALL
        )

        result.append(
            part
        )

    return "".join(
        result
    )


# =========================================================
# ARTICOLE SIMPLE
# KEYWORDS
# =========================================================


def _simple_process_keywords(text):

    """
    Procesează rândurile cu:

    Keywords:
    Cuvinte-cheie:
    Cuvinte cheie:

    Reguli:

    - eticheta este bold;
    - se păstrează conținutul;
    - se introduce <br> DUPĂ rândul Keywords.
    """

    if not text:
        return ""

    # -----------------------------------------------------
    # Cazul în care Keywords este într-un paragraf XML.
    # -----------------------------------------------------

    def replace_paragraph(match):

        opening = match.group(1)

        content = match.group(2)

        closing = match.group(3)

        clean = _simple_clean_text(
            content
        )

        if not re.match(
            r"^(Keywords|Cuvinte[- ]cheie)\s*:?",
            clean,
            flags=re.IGNORECASE
        ):

            return match.group(0)

        # -------------------------------------------------
        # BOLD PENTRU ETICHETĂ
        # -------------------------------------------------

        content = re.sub(
            r"^(Keywords|Cuvinte[- ]cheie)"
            r"(\s*:?)",
            r"<strong>\1\2</strong> ",
            content,
            count=1,
            flags=re.IGNORECASE
        )

        return (
            opening
            + content.strip()
            + closing
            + "<br>"
        )

    text = re.sub(
        r"(<(?:p|P|NormalParagraphStyle)\b[^>]*>)"
        r"(.*?)"
        r"(</(?:p|P|NormalParagraphStyle)\s*>)",
        replace_paragraph,
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    # -----------------------------------------------------
    # Caz de rezervă:
    #
    # dacă Keywords nu a fost împachetat într-un paragraf,
    # îl procesăm și ca linie simplă.
    # -----------------------------------------------------

    lines = text.splitlines()

    processed_lines = []

    for line in lines:

        clean = _simple_clean_text(
            line
        )

        if re.match(
            r"^(Keywords|Cuvinte[- ]cheie)\s*:?",
            clean,
            flags=re.IGNORECASE
        ):

            # Evităm să procesăm din nou dacă
            # deja conține strong.
            if "<strong>" not in line.lower():

                line = re.sub(
                    r"^(Keywords|Cuvinte[- ]cheie)"
                    r"(\s*:?)",
                    r"<strong>\1\2</strong> ",
                    line,
                    count=1,
                    flags=re.IGNORECASE
                )

            line = (
                line
                + "<br>"
            )

        processed_lines.append(
            line
        )

    return "\n".join(
        processed_lines
    )


# =========================================================
# ARTICOLE SIMPLE
# ELIMINARE HEADER-E REPETATE
# =========================================================


def _simple_remove_duplicate_headers(text):

    """
    Elimină header-ele repetate de pagină.

    Regula:

    - identificăm texte scurte;
    - dacă același text apare de cel puțin 2 ori,
      îl considerăm header repetat;
    - îl eliminăm.

    NU procesăm:

    - H5;
    - afiliere;
    - elemente cu strong/sup introduse pentru autori.
    """

    if not text:
        return ""

    # -----------------------------------------------------
    # Extragem paragrafele.
    # -----------------------------------------------------

    paragraph_pattern = (
        r"<(?:p|P|NormalParagraphStyle)\b[^>]*>"
        r"(.*?)"
        r"</(?:p|P|NormalParagraphStyle)\s*>"
    )

    paragraphs = re.findall(
        paragraph_pattern,
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    candidates = []

    for paragraph in paragraphs:

        clean = _simple_clean_text(
            paragraph
        )

        if not clean:
            continue

        # -------------------------------------------------
        # Nu considerăm autorii header.
        # -------------------------------------------------

        if "<H5" in paragraph.upper():
            continue

        # -------------------------------------------------
        # Header-ele sunt de regulă scurte.
        # -------------------------------------------------

        words = clean.split()

        if 1 <= len(words) <= 12:

            candidates.append(
                clean.casefold()
            )

    counter = Counter(
        candidates
    )

    repeated_headers = {
        value
        for value, count in counter.items()
        if count >= 2
    }

    if not repeated_headers:
        return text

    # -----------------------------------------------------
    # Eliminăm paragrafele repetate.
    # -----------------------------------------------------

    def remove_repeated(match):

        content = match.group(1)

        clean = _simple_clean_text(
            content
        )

        if clean.casefold() in repeated_headers:

            return ""

        return match.group(0)

    return re.sub(
        paragraph_pattern,
        remove_repeated,
        text,
        flags=re.IGNORECASE | re.DOTALL
    )


# =========================================================
# ARTICOLE SIMPLE
# NORMALIZARE
# =========================================================


def _simple_normalize(text):

    if not text:
        return ""

    # -----------------------------------------------------
    # Eliminăm spațiile excesive.
    # -----------------------------------------------------

    text = re.sub(
        r"\n[ \t]+",
        "\n",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# =========================================================
# =========================================================
# ARTICOLE SIMPLE
# PARSER
# =========================================================
#
# REGULA DE BAZĂ:
#
# PARAGRAFUL 2 + PRIMUL H TAG
#             ↓
#       TITLU PRINCIPAL
#
# RESTUL
#             ↓
#       CONTINUT ARTICOL
#
# =========================================================


def parse_simple_xml(path):

    tree = etree.parse(
        path
    )

    root = tree.getroot()

    data = {
        "titlu": "",
        "continut_articol": "",
    }

    # =====================================================
    # ELEMENTELE XML
    # =====================================================

    elements = list(
        root.iter()
    )

    # =====================================================
    # PARAGRAFE
    # =====================================================

    paragraph_elements = []

    for element in elements:

        if not isinstance(
            element.tag,
            str
        ):
            continue

        tag = etree.QName(
            element
        ).localname

        tag_lower = tag.lower()

        if tag_lower in (
            "p",
            "paragraph",
            "paragraf",
            "normalparagraphstyle",
        ):

            txt = _text(
                element
            )

            if txt:

                paragraph_elements.append(
                    element
                )

    # =====================================================
    # PARAGRAFUL 2
    # =====================================================

    paragraph_2 = None

    if len(
        paragraph_elements
    ) >= 2:

        paragraph_2 = (
            paragraph_elements[1]
        )

    paragraph_2_text = _text(
        paragraph_2
    )

    # =====================================================
    # PRIMUL H TAG
    # =====================================================

    first_h = None

    first_h_index = None

    for index, element in enumerate(
        elements
    ):

        if not isinstance(
            element.tag,
            str
        ):
            continue

        tag = etree.QName(
            element
        ).localname

        tag_upper = tag.upper()

        if tag_upper in (
            "H1",
            "H2",
            "H3",
            "H4",
            "H5",
            "H6",
            "H",
        ):

            txt = _text(
                element
            )

            if txt:

                first_h = element

                first_h_index = index

                break

    first_h_text = _text(
        first_h
    )

    # =====================================================
    # CONSTRUIRE TITLU
    # =====================================================

    title_parts = []

    if paragraph_2_text:

        title_parts.append(
            paragraph_2_text
        )

    if first_h_text:

        title_parts.append(
            first_h_text
        )

    data["titlu"] = " ".join(
        part.strip()
        for part in title_parts
        if part.strip()
    )

    # =====================================================
    # CONȚINUT ARTICOL
    # =====================================================

    body = []

    if first_h_index is not None:

        for index, element in enumerate(
            elements
        ):

            if not isinstance(
                element.tag,
                str
            ):
                continue

            # -------------------------------------------------
            # Nu includem elementele până la primul H.
            # -------------------------------------------------

            if index <= first_h_index:

                continue

            # -------------------------------------------------
            # Evităm elementele descendente care sunt deja
            # incluse în elementul părinte.
            # -------------------------------------------------

            parent = element.getparent()

            if parent is not None:

                if parent in elements:

                    parent_index = (
                        elements.index(
                            parent
                        )
                    )

                    if parent_index > first_h_index:

                        continue

            # -------------------------------------------------
            # Serializăm elementul.
            # -------------------------------------------------

            xml = etree.tostring(
                element,
                encoding="unicode"
            )

            if xml.strip():

                body.append(
                    xml
                )

    # =====================================================
    # XML BRUT
    # =====================================================

    content = "\n".join(
        body
    )

    # =====================================================
    # REGULA 1
    # ELIMINARE H2
    #
    # ESTE PRIMA REGULĂ APLICATĂ.
    #
    # Deci H2 nu mai poate ajunge în builder.
    # =====================================================

    content = _simple_remove_h2(
        content
    )

    # =====================================================
    # REGULA 2
    # ELIMINARE HEADER-E REPETATE
    # =====================================================

    content = (
        _simple_remove_duplicate_headers(
            content
        )
    )

    # =====================================================
    # REGULA 3
    # H5 = AUTORI
    #
    # - BOLD
    # - NUMERE SUPERSCRIPT
    # =====================================================

    content = (
        _simple_process_authors(
            content
        )
    )

    # =====================================================
    # REGULA 4
    # AFILIERI
    #
    # - 1.
    # - 2.
    # - 3.
    #
    # RESET LA FIECARE H5.
    #
    # ITALIC.
    # =====================================================

    content = (
        _simple_process_affiliations(
            content
        )
    )

    # =====================================================
    # REGULA 5
    # KEYWORDS / CUVINTE-CHEIE
    #
    # - BOLD
    # - SPAȚIERE
    # - <br> DUPĂ RÂND
    # =====================================================

    content = (
        _simple_process_keywords(
            content
        )
    )

    # =====================================================
    # REGULA 6
    # PROTECȚIE FINALĂ
    #
    # Eliminăm H2 încă o dată.
    #
    # Este intenționat.
    #
    # Dacă vreunul dintre pașii anteriori ar păstra
    # accidental un H2, acesta este eliminat aici.
    # =====================================================

    content = _simple_remove_h2(
        content
    )

    # =====================================================
    # NORMALIZARE FINALĂ
    # =====================================================

    content = _simple_normalize(
        content
    )

    # =====================================================
    # SALVARE
    # =====================================================

    data["continut_articol"] = content

    return data
