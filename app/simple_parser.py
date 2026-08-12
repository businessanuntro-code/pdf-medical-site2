import re
import xml.etree.ElementTree as ET


# =========================================================
# FUNCTII GENERALE - ARTICOLE SIMPLE
# =========================================================

def clean_text(text):
    """
    Curata textul extras din XML:

    - elimina spatiile inutile
    - normalizeaza spatiile
    - elimina caracterele non-breaking space
    """

    if not text:
        return ""

    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def element_text(element):
    """
    Returneaza tot textul continut de un element XML,
    inclusiv textul elementelor copil.
    """

    if element is None:
        return ""

    text = "".join(element.itertext())

    return clean_text(text)


def get_direct_children(element, tag_name):
    """
    Returneaza copiii directi cu tag-ul specificat.
    """

    return [
        child
        for child in list(element)
        if child.tag.split("}")[-1] == tag_name
    ]


def get_all_children(element, tag_name):
    """
    Returneaza toate elementele descendente
    cu tag-ul specificat.
    """

    result = []

    for child in element.iter():

        if child.tag.split("}")[-1] == tag_name:
            result.append(child)

    return result


# =========================================================
# KEYWORDS
# =========================================================

def is_keywords(text):
    """
    Verifica daca textul este un paragraf de Keywords.
    """

    if not text:
        return False

    normalized = text.lower().strip()

    return (
        normalized.startswith("keywords:")
        or normalized.startswith("keywords :")
        or normalized.startswith("cuvinte cheie:")
        or normalized.startswith("cuvinte cheie :")
    )


def extract_keywords(text):
    """
    Extrage continutul de dupa:

        Keywords:

    sau:

        Cuvinte cheie:
    """

    if not text:
        return ""

    match = re.match(
        r"^\s*(?:keywords|cuvinte\s+cheie)\s*:\s*(.*)$",
        text,
        flags=re.IGNORECASE
    )

    if match:
        return clean_text(match.group(1))

    return clean_text(text)


# =========================================================
# AUTORI
# =========================================================

def is_likely_author_paragraph(text):
    """
    Verifica daca un paragraf <P> pare sa contina autori.

    Exemple:

        C. Achiroaei1,2, Diana-Ioana Panaite1,2,
        C. Volovăț1,2

        Ion Popescu1, Maria Ionescu2

    Nu considera autori:

        Keywords: ...

        Cuvinte cheie: ...

        afilieri / institutii

        paragrafe normale de continut
    """

    if not text:
        return False

    text = clean_text(text)

    # -----------------------------------------------------
    # Keywords nu pot fi autori
    # -----------------------------------------------------

    if is_keywords(text):
        return False

    # -----------------------------------------------------
    # Un paragraf foarte lung este aproape sigur continut
    # -----------------------------------------------------

    if len(text) > 300:
        return False

    # -----------------------------------------------------
    # Daca exista semne clare de paragraf normal
    # -----------------------------------------------------

    if text.endswith(".") and "," not in text:
        return False

    # -----------------------------------------------------
    # Lista de autori trebuie sa aiba de regula virgule
    # -----------------------------------------------------

    if "," not in text:
        return False

    # -----------------------------------------------------
    # Cuvinte specifice afilierilor
    # -----------------------------------------------------

    affiliation_words = (
        "university",
        "universitatea",
        "institute",
        "institut",
        "hospital",
        "spital",
        "clinic",
        "clinical",
        "department",
        "departament",
        "faculty",
        "facultatea",
        "center",
        "centre",
        "bucharest",
        "bucuresti",
        "romania",
    )

    text_lower = text.lower()

    for word in affiliation_words:

        if word in text_lower:
            return False

    # -----------------------------------------------------
    # Impartim textul dupa virgule
    # -----------------------------------------------------

    parts = [
        part.strip()
        for part in text.split(",")
        if part.strip()
    ]

    if len(parts) < 2:
        return False

    # -----------------------------------------------------
    # Pattern pentru nume de autori
    #
    # Sunt permise:
    #
    # C.
    # Ion
    # Ion Popescu
    # Diana-Ioana Panaite1
    # C. Achiroaei1
    #
    # precum si numerele de afiliere:
    #
    # 1
    # 1,2
    # 1,2,3
    # -----------------------------------------------------

    author_pattern = re.compile(
        r"^[A-Za-zÀ-ÖØ-öø-ÿĂăÂâÎîȘșŞşȚțŢţ"
        r"\-.'’]+"
        r"(?:\s+[A-Za-zÀ-ÖØ-öø-ÿĂăÂâÎîȘșŞşȚțŢţ"
        r"\-.'’]+)*"
        r"\d*"
        r"(?:\s*,\s*\d+)*$"
    )

    valid_parts = 0

    for part in parts:

        part = part.strip()

        if author_pattern.match(part):
            valid_parts += 1

    # -----------------------------------------------------
    # Majoritatea elementelor trebuie sa semene cu nume
    # -----------------------------------------------------

    return valid_parts >= max(2, len(parts) // 2)


def extract_authors(element):
    """
    Extrage autorii.

    PRIORITATE:

    1. <H5>
    2. <P> cu aspect de lista de autori

    Exemple:

        <H5>
            Ancuța-Elena Baciu1,
            Irina-Maria Dumitru1,2
        </H5>

    sau:

        <P>
            C. Achiroaei1,2,
            Diana-Ioana Panaite1,2,
            C. Volovăț1,2
        </P>

    Numerele raman in text.

    Formatarea bold + superscript
    va fi facuta in simple_builder.py.
    """

    if element is None:
        return ""

    # =====================================================
    # 1. PRIORITATE - H5
    # =====================================================

    for child in element.iter():

        if child.tag.split("}")[-1] != "H5":
            continue

        text = element_text(child)

        if text:
            return text

    # =====================================================
    # 2. FALLBACK - P CU ASPECT DE AUTORI
    # =====================================================

    for child in element.iter():

        if child.tag.split("}")[-1] != "P":
            continue

        text = element_text(child)

        if not text:
            continue

        if is_likely_author_paragraph(text):
            return text

    return ""


# =========================================================
# AFILIERI
# =========================================================

def extract_affiliations(element):
    """
    Extrage afilierile din listele XML.

    Exemplu:

    <L>
        <LI>
            <Lbl>1.</Lbl>
            <LBody>
                Institute...
            </LBody>
        </LI>
    </L>

    Returneaza:

    [
        {
            "number": "1",
            "text": "Institute..."
        }
    ]
    """

    affiliations = []

    for list_element in element.iter():

        if list_element.tag.split("}")[-1] != "L":
            continue

        for li in list_element:

            if li.tag.split("}")[-1] != "LI":
                continue

            number = ""
            body = ""

            for child in li:

                tag = child.tag.split("}")[-1]

                if tag == "Lbl":
                    number = element_text(child)

                elif tag == "LBody":
                    body = element_text(child)

            number = re.sub(r"[^\d]", "", number)

            body = clean_text(body)

            if body:
                affiliations.append({
                    "number": number,
                    "text": body
                })

    return affiliations


# =========================================================
# PARAGRAFE
# =========================================================

def extract_paragraphs(element):
    """
    Extrage paragrafele <P> din articol.

    Keywords sunt scoase separat.
    """

    paragraphs = []
    keywords = ""

    for p in element.iter():

        if p.tag.split("}")[-1] != "P":
            continue

        text = element_text(p)

        if not text:
            continue

        # -------------------------------------------------
        # Keywords
        # -------------------------------------------------

        if is_keywords(text):

            keywords = extract_keywords(text)

        else:

            paragraphs.append(text)

    return paragraphs, keywords


# =========================================================
# TITLURI
# =========================================================

def extract_titles(element):
    """
    Extrage titlurile H4.

    Regula:

        primul H4  = title_en
        al doilea H4 = title_ro

    Daca exista un singur H4,
    acesta este folosit ca title_en.
    """

    titles = []

    for child in element.iter():

        if child.tag.split("}")[-1] != "H4":
            continue

        text = element_text(child)

        if text:
            titles.append(text)

    title_en = ""
    title_ro = ""

    if len(titles) >= 1:
        title_en = titles[0]

    if len(titles) >= 2:
        title_ro = titles[1]

    return {
        "title_en": title_en,
        "title_ro": title_ro,
        "titles": titles
    }


# =========================================================
# IDENTIFICARE ARTICOLE
# =========================================================

def find_article_sections(part):
    """
    Identifica sectiunile care contin articole.

    Un articol simplu este identificat
    prin prezenta unui H4.

    Nu presupunem ca fiecare Sect
    are exact aceeasi structura.
    """

    articles = []

    for sect in part.iter():

        if sect.tag.split("}")[-1] != "Sect":
            continue

        h4s = get_all_children(
            sect,
            "H4"
        )

        if not h4s:
            continue

        titles = []

        for h4 in h4s:

            text = element_text(h4)

            if text:
                titles.append(text)

        if not titles:
            continue

        articles.append(sect)

    return articles


# =========================================================
# PROCESARE ARTICOL
# =========================================================

def parse_article_section(section):
    """
    Proceseaza un singur articol simplu.
    """

    # -----------------------------------------------------
    # TITLURI
    # -----------------------------------------------------

    titles = extract_titles(section)

    # -----------------------------------------------------
    # AUTORI
    # -----------------------------------------------------

    authors = extract_authors(section)

    # -----------------------------------------------------
    # AFILIERI
    # -----------------------------------------------------

    affiliations = extract_affiliations(section)

    # -----------------------------------------------------
    # CONTINUT + KEYWORDS
    # -----------------------------------------------------

    paragraphs, keywords = extract_paragraphs(section)

    # -----------------------------------------------------
    # REZULTAT
    # -----------------------------------------------------

    return {
        "title_en": titles["title_en"],
        "title_ro": titles["title_ro"],
        "titles": titles["titles"],

        "authors": authors,

        "affiliations": affiliations,

        "paragraphs": paragraphs,

        "keywords": keywords,

        "content": paragraphs,

        "content_text": "\n\n".join(paragraphs)
    }


# =========================================================
# PARSER PRINCIPAL - ARTICOLE SIMPLE
# =========================================================

def parse_simple_xml(xml_path):
    """
    Parser principal pentru articole simple.

    Acest parser este independent de parser.py
    si este folosit exclusiv pentru articole simple.
    """

    # =====================================================
    # CITIRE XML
    # =====================================================

    try:

        tree = ET.parse(xml_path)
        root = tree.getroot()

    except ET.ParseError as exc:

        raise ValueError(
            f"XML invalid sau imposibil de procesat: {exc}"
        ) from exc

    # =====================================================
    # GASIM TOATE PART-URILE
    # =====================================================

    parts = []

    for element in root.iter():

        if element.tag.split("}")[-1] == "Part":

            parts.append(element)

    # -----------------------------------------------------
    # Daca XML-ul nu are Part,
    # folosim root-ul.
    # -----------------------------------------------------

    if not parts:

        parts = [root]

    articles = []

    # =====================================================
    # PROCESAM FIECARE PART
    # =====================================================

    for part in parts:

        # -------------------------------------------------
        # H2 = TITLU SECTIUNE / CONFERINTA
        # -------------------------------------------------

        section_title = ""

        for child in part.iter():

            if child.tag.split("}")[-1] == "H2":

                text = element_text(child)

                if text:

                    section_title = text
                    break

        # -------------------------------------------------
        # IDENTIFICAM ARTICOLELE
        # -------------------------------------------------

        article_sections = find_article_sections(part)

        # -------------------------------------------------
        # PROCESAM ARTICOLELE
        # -------------------------------------------------

        for section in article_sections:

            article = parse_article_section(section)

            # ---------------------------------------------
            # Ignoram sectiunile fara continut real
            # ---------------------------------------------

            if not (
                article["title_en"]
                or article["title_ro"]
                or article["authors"]
                or article["paragraphs"]
            ):
                continue

            article["section_title"] = section_title

            articles.append(article)

    # =====================================================
    # REZULTAT FINAL
    # =====================================================

    return {
        "type": "simple",

        "articles": articles,

        # -------------------------------------------------
        # Compatibilitate cu un singur articol
        # -------------------------------------------------

        "title_en": (
            articles[0]["title_en"]
            if articles
            else ""
        ),

        "title_ro": (
            articles[0]["title_ro"]
            if articles
            else ""
        ),

        "authors": (
            articles[0]["authors"]
            if articles
            else ""
        ),

        "affiliations": (
            articles[0]["affiliations"]
            if articles
            else []
        ),

        "keywords": (
            articles[0]["keywords"]
            if articles
            else ""
        ),

        "content": (
            articles[0]["content"]
            if articles
            else []
        ),

        "content_text": (
            articles[0]["content_text"]
            if articles
            else ""
        )
    }
