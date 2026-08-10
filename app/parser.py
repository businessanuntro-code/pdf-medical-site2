from lxml import etree


def _text(el):
    if el is None:
        return ""

    return " ".join(
        el.itertext()
    ).strip()


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

        data["autor"] = ", ".join(autori)

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

    data["continut_articol"] = "\n".join(body)

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

            node = etree.fromstring(xml)

            for ref in node.findall(".//LBody"):

                txt = _text(ref)

                if txt:
                    refs.append(txt)

    data["bibliografie"] = "\n".join(refs)

    # =====================================================
    # CONFLICT DE INTERESE / SUPORT FINANCIAR / CC-BY
    # =====================================================

    for story in stories:

        xml = etree.tostring(
            story,
            encoding="unicode"
        )

        if "<NormalParagraphStyle>" not in xml:
            continue

        node = etree.fromstring(xml)

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
# ARTICOL SIMPLU
# =========================================================
#
# REGULA:
#
# PARAGRAFUL 2 + PRIMUL H TAG
#             ↓
#        TITLU PRINCIPAL
#
# RESTUL CONTINUTULUI
#             ↓
#        CONTINUT ARTICOL
# =========================================================

def parse_simple_xml(path):

    tree = etree.parse(path)
    root = tree.getroot()

    data = {
        "titlu": "",
        "continut_articol": "",
    }

    # =====================================================
    # ELEMENTELE XML
    # =====================================================

    elements = list(root.iter())

    # =====================================================
    # PARAGRAFUL 2
    # =====================================================

    paragraph_elements = []

    for element in elements:

        # IMPORTANT:
        # Unele noduri lxml pot avea .tag ca obiect
        # special, nu ca string XML.
        if not isinstance(element.tag, str):
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

            txt = _text(element)

            if txt:
                paragraph_elements.append(
                    element
                )

    paragraph_2 = None

    if len(paragraph_elements) >= 2:
        paragraph_2 = paragraph_elements[1]

    paragraph_2_text = _text(
        paragraph_2
    )

    # =====================================================
    # PRIMUL H TAG
    # =====================================================

    first_h = None
    first_h_index = None

    for index, element in enumerate(elements):

        if not isinstance(element.tag, str):
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

            txt = _text(element)

            if txt:

                first_h = element
                first_h_index = index

                break

    first_h_text = _text(
        first_h
    )

    # =====================================================
    # CONSTRUIRE TITLUL
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
    # CONTINUT ARTICOL
    # =====================================================

    body = []

    if first_h_index is not None:

        for index, element in enumerate(elements):

            if not isinstance(element.tag, str):
                continue

            if index <= first_h_index:
                continue

            # =================================================
            # Evităm elementele descendente care sunt deja
            # incluse în elementele părinte.
            # =================================================

            parent = element.getparent()

            if parent is not None:

                if parent in elements:

                    parent_index = elements.index(
                        parent
                    )

                    if parent_index > first_h_index:
                        continue

            xml = etree.tostring(
                element,
                encoding="unicode"
            )

            if xml.strip():
                body.append(xml)

    data["continut_articol"] = "\n".join(
        body
    )

    return data
