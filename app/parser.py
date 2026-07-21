from lxml import etree


def _text(el):
    if el is None:
        return ""
    return " ".join(el.itertext()).strip()


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
        data["titlu"] = _text(root.find(".//TITLU"))

    if root.find(".//English_Title") is not None:
        data["english_title"] = _text(root.find(".//English_Title"))

    if root.find(".//Autor") is not None:
        autori = []
        for a in root.findall(".//Autor"):
            t = _text(a)
            if t:
                autori.append(t)
        data["autor"] = ", ".join(autori)

    if root.find(".//Abstract") is not None:
        data["abstract"] = _text(root.find(".//Abstract"))

    if root.find(".//Keywords_ENG") is not None:
        data["keywords_eng"] = _text(root.find(".//Keywords_ENG"))

    if root.find(".//Rezumat") is not None:
        data["rezumat"] = _text(root.find(".//Rezumat"))

    if root.find(".//Keywords_ROM") is not None:
        data["keywords_rom"] = _text(root.find(".//Keywords_ROM"))

    # =====================================================
    # CORESPONDENT (autor + primit + acceptat)
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
    # Tot ce urmeaza dupa Keywords_ROM
    # pana la primul Corespondent (Primit)
    # =====================================================

    stories = root.findall(".//Story")

    collecting = False
    body = []

    for story in stories:

        xml = etree.tostring(story, encoding="unicode")

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

        xml = etree.tostring(story, encoding="unicode")

        if "<_No_paragraph_style_>Bibliografie</_No_paragraph_style_>" in xml:
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

    return data
