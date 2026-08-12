import re
import xml.etree.ElementTree as ET


# =========================================================
# FUNCTII GENERALE
# =========================================================

def clean_text(text):
    """
    Curata si normalizeaza textul extras din XML.
    """

    if not text:
        return ""

    text = text.replace("\xa0", " ")
    text = text.replace("\u200b", "")
    text = text.replace("\ufeff", "")

    # Normalizeaza liniile multiple
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def get_tag(element):
    """
    Returneaza numele tagului fara namespace.
    """

    if element is None:
        return ""

    return element.tag.split("}")[-1]


def element_text(element):
    """
    Returneaza tot textul unui element,
    inclusiv textul elementelor copil.
    """

    if element is None:
        return ""

    text = "".join(element.itertext())

    return clean_text(text)


def is_text_element(element):
    """
    Verifica daca elementul poate contine text util.
    """

    return get_tag(element) in {
        "H1",
        "H2",
        "H3",
        "H4",
        "H5",
        "P",
        "Footnote",
        "LBody",
        "Lbl",
    }


# =========================================================
# KEYWORDS
# =========================================================

def is_keywords_text(text):
    """
    Verifica daca un text reprezinta Keywords.

    Accepta:

        Keywords:
        Keywords :
        Cuvinte cheie:
        Cuvinte cheie :
    """

    if not text:
        return False

    normalized = clean_text(text).lower()

    return bool(
        re.match(
            r"^(keywords|cuvinte\s+cheie)\s*:",
            normalized,
            flags=re.IGNORECASE
        )
    )


def extract_keywords(text):
    """
    Extrage continutul de dupa Keywords:
    sau Cuvinte cheie:
    """

    if not text:
        return ""

    text = clean_text(text)

    match = re.match(
        r"^(?:keywords|cuvinte\s+cheie)\s*:\s*(.*)$",
        text,
        flags=re.IGNORECASE
    )

    if match:
        return clean_text(match.group(1))

    return text


# =========================================================
# AUTORI
# =========================================================

def looks_like_author_text(text):
    """
    Verifica daca un text seamana cu o lista de autori.

    Exemple acceptate:

        C. Achiroaei1,2, Diana-Ioana Panaite1,2, C. Volovăț1,2

        Ancuța-Elena Baciu1, Irina-Maria Dumitru1,2

        Eugen Brătucu, Claudiu Daha, Laurenţiu Simion
    """

    if not text:
        return False

    text = clean_text(text)

    if len(text) > 500:
        return False

    # Nu este autor daca pare continut de articol
    if is_keywords_text(text):
        return False

    # Excludem propozitii lungi
    if text.count(".") > 10:
        return False

    # Separare clara prin virgule
    parts = [
        part.strip()
        for part in text.split(",")
        if part.strip()
    ]

    if len(parts) < 2:
        return False

    # Daca avem prea multe cuvinte, probabil este continut
    words = text.split()

    if len(words) > 80:
        return False

    # Verificam daca elementele contin nume plauzibile
    author_like = 0

    for part in parts:

        # Eliminam eventualele numere de afiliere
        clean_part = re.sub(r"\d+(?:\s*,\s*\d+)*$", "", part)
        clean_part = clean_part.strip()

        if not clean_part:
            continue

        # Nume cu litere
        if re.search(
            r"[A-Za-zÀ-ÖØ-öø-ÿĂăÂâÎîȘșŞşȚțŢţ]",
            clean_part
        ):
            author_like += 1

    return author_like >= 2


def extract_authors_from_element(element):
    """
    Extrage autorii din H3/H5 sau dintr-un P
    atunci cand P contine o lista de autori.
    """

    text = element_text(element)

    if not text:
        return ""

    if looks_like_author_text(text):
        return text

    return ""


# =========================================================
# AFILIERI
# =========================================================

def is_affiliation_text(text):
    """
    Verifica daca textul seamana cu o afiliere.

    Exemple:

        1. Institute of Oncology, Bucharest, Romania

        Faculty of Physics, University of Bucharest, Romania

        Fundeni Clinical Institute, Bucharest, Romania
    """

    if not text:
        return False

    text = clean_text(text)

    if len(text) > 500:
        return False

    # Afilierea poate incepe cu numar
    if re.match(r"^\d+\.", text):
        return True

    affiliation_words = [
        "institute",
        "university",
        "faculty",
        "hospital",
        "clinical",
        "center",
        "centre",
        "laboratory",
        "department",
        "association",
        "bucharest",
        "romania",
        "medical",
        "school",
        "clinic",
        "institut",
        "universitate",
        "facultate",
        "spital",
        "laborator",
        "departament",
        "centru",
        "românia",
    ]

    lower = text.lower()

    score = 0

    for word in affiliation_words:
        if word in lower:
            score += 1

    return score >= 1


def clean_affiliation_number(text):
    """
    Elimina numarul de afiliere de la inceput.

    Exemplu:

        1. Institute...
        
    devine:

        Institute...
    """

    if not text:
        return ""

    text = clean_text(text)

    text = re.sub(
        r"^\s*\d+\.\s*",
        "",
        text
    )

    return clean_text(text)


def add_affiliation(affiliations, text):
    """
    Adauga o afiliere daca nu exista deja.
    """

    text = clean_affiliation_number(text)

    if not text:
        return

    if text in affiliations:
        return

    affiliations.append(text)


# =========================================================
# TITLURI
# =========================================================

def extract_titles(elements):
    """
    Extrage titlurile din H1/H2.

    Prioritate:

        H1 = title_en
        H2 = title_ro

    Daca exista un singur H2:
        title_en = H2

    Daca exista doua titluri separate:
        primul = EN
        al doilea = RO
    """

    titles = []

    for element in elements:

        tag = get_tag(element)

        if tag not in {"H1", "H2"}:
            continue

        text = element_text(element)

        if not text:
            continue

        titles.append({
            "tag": tag,
            "text": text
        })

    title_en = ""
    title_ro = ""

    # -----------------------------------------------------
    # H1 + H2
    # -----------------------------------------------------

    h1_titles = [
        item["text"]
        for item in titles
        if item["tag"] == "H1"
    ]

    h2_titles = [
        item["text"]
        for item in titles
        if item["tag"] == "H2"
    ]

    if h1_titles:

        title_en = h1_titles[0]

        if h2_titles:
            title_ro = h2_titles[0]

    else:

        if len(h2_titles) >= 2:

            title_en = h2_titles[0]
            title_ro = h2_titles[1]

        elif len(h2_titles) == 1:

            title_en = h2_titles[0]

    return {
        "title_en": clean_text(title_en),
        "title_ro": clean_text(title_ro),
        "titles": [
            item["text"]
            for item in titles
        ]
    }


# =========================================================
# IDENTIFICAREA ARTICOLELOR
# =========================================================

def get_all_sects(root):
    """
    Returneaza toate Sect-urile din document.
    """

    return [
        element
        for element in root.iter()
        if get_tag(element) == "Sect"
    ]


def has_article_title(section):
    """
    Verifica daca un Sect pare sa fie un articol.

    Cautam H1 sau H2.
    """

    for element in section.iter():

        if get_tag(element) in {"H1", "H2"}:

            if element_text(element):
                return True

    return False


def has_author_block(section):
    """
    Verifica daca Sect contine un bloc de autori.
    """

    for element in section.iter():

        tag = get_tag(element)

        if tag in {"H3", "H5"}:

            text = element_text(element)

            if text:
                return True

    return False


def find_article_sections(root):
    """
    Identifica Sect-urile principale care reprezinta articole.

    Nu luam fiecare Sect imbricat separat.

    Un articol este considerat Sect-ul care contine
    un titlu si un bloc de autori.
    """

    all_sections = get_all_sects(root)

    candidates = []

    for section in all_sections:

        if not has_article_title(section):
            continue

        if not has_author_block(section):
            continue

        candidates.append(section)

    # -----------------------------------------------------
    # Eliminam Sect-urile imbricate care fac parte
    # din acelasi articol.
    # -----------------------------------------------------

    result = []

    candidate_ids = {
        id(section)
        for section in candidates
    }

    for section in candidates:

        is_nested_candidate = False

        # Cautam daca exista un alt candidat parinte
        for possible_parent in candidates:

            if possible_parent is section:
                continue

            found = False

            for child in possible_parent.iter():

                if child is section:
                    found = True
                    break

            if found:
                is_nested_candidate = True
                break

        if not is_nested_candidate:
            result.append(section)

    return result


# =========================================================
# COLECTARE BLOCURI TEXT
# =========================================================

def collect_text_elements(section):
    """
    Colecteaza toate elementele de text dintr-un articol.

    Ordinea XML este pastrata.
    """

    elements = []

    for element in section.iter():

        tag = get_tag(element)

        if tag not in {
            "H1",
            "H2",
            "H3",
            "H4",
            "H5",
            "P",
            "Footnote",
            "LBody",
            "Lbl"
        }:
            continue

        text = element_text(element)

        if not text:
            continue

        elements.append({
            "element": element,
            "tag": tag,
            "text": text
        })

    return elements


# =========================================================
# PARSAREA UNUI ARTICOL
# =========================================================

def parse_article_section(section):
    """
    Proceseaza un singur articol simplu.

    Ordinea logica:

        TITLU
        ↓
        AUTORI
        ↓
        AFILIERI
        ↓
        CONTINUT
        ↓
        KEYWORDS

    Parserul nu presupune ca fiecare document
    foloseste exact aceleasi taguri XML.
    """

    elements = collect_text_elements(section)

    # =====================================================
    # TITLURI
    # =====================================================

    titles = extract_titles(
        [
            item["element"]
            for item in elements
            if item["tag"] in {"H1", "H2"}
        ]
    )

    # =====================================================
    # AUTORI
    # =====================================================

    authors = ""

    author_index = -1

    # Prioritate H3 / H5
    for index, item in enumerate(elements):

        if item["tag"] in {"H3", "H5"}:

            text = extract_authors_from_element(
                item["element"]
            )

            if text:

                authors = text
                author_index = index
                break

    # Daca nu avem H3/H5, cautam P
    if not authors:

        for index, item in enumerate(elements):

            if item["tag"] != "P":
                continue

            text = extract_authors_from_element(
                item["element"]
            )

            if text:

                authors = text
                author_index = index
                break

    # =====================================================
    # AFILIERI
    # =====================================================

    affiliations = []

    affiliation_started = False
    affiliation_end_index = author_index

    for index, item in enumerate(elements):

        if index <= author_index:
            continue

        tag = item["tag"]
        text = item["text"]

        # -------------------------------------------------
        # Keywords inseamna ca nu mai exista afilieri
        # -------------------------------------------------

        if is_keywords_text(text):
            break

        # -------------------------------------------------
        # Footnote = afiliere
        # -------------------------------------------------

        if tag == "Footnote":

            add_affiliation(
                affiliations,
                text
            )

            affiliation_started = True
            affiliation_end_index = index

            continue

        # -------------------------------------------------
        # LBody = afiliere
        # -------------------------------------------------

        if tag == "LBody":

            if is_affiliation_text(text):

                add_affiliation(
                    affiliations,
                    text
                )

                affiliation_started = True
                affiliation_end_index = index

                continue

        # -------------------------------------------------
        # H4 = afiliere in unele XML-uri
        # -------------------------------------------------

        if tag == "H4":

            if is_affiliation_text(text):

                add_affiliation(
                    affiliations,
                    text
                )

                affiliation_started = True
                affiliation_end_index = index

                continue

        # -------------------------------------------------
        # Dupa ce au inceput afilierile, putem intalni
        # alte blocuri de afiliere.
        # -------------------------------------------------

        if affiliation_started:

            if is_affiliation_text(text):

                add_affiliation(
                    affiliations,
                    text
                )

                affiliation_end_index = index

    # =====================================================
    # CONTINUT + KEYWORDS
    # =====================================================

    paragraphs = []
    keywords = ""

    content_started = False

    # -----------------------------------------------------
    # Continutul incepe dupa ultimul bloc de afiliere.
    # Daca nu exista afiliere, incepe dupa autori.
    # -----------------------------------------------------

    start_index = max(
        author_index + 1,
        affiliation_end_index + 1
    )

    for index in range(
        start_index,
        len(elements)
    ):

        item = elements[index]

        tag = item["tag"]
        text = item["text"]

        if not text:
            continue

        # -------------------------------------------------
        # Keywords
        # -------------------------------------------------

        if is_keywords_text(text):

            keywords = extract_keywords(text)

            # Daca keywords apare lipit la sfarsitul
            # unui paragraf, extragem partea de dinainte.
            prefix_match = re.match(
                r"^(.*?)(?:Keywords|Cuvinte\s+cheie)\s*:",
                text,
                flags=re.IGNORECASE
            )

            if prefix_match:

                prefix = clean_text(
                    prefix_match.group(1)
                )

                if prefix:
                    paragraphs.append(prefix)

            break

        # -------------------------------------------------
        # Lbl este doar numarul afilierii.
        # Nu trebuie sa ajunga in continut.
        # -------------------------------------------------

        if tag == "Lbl":
            continue

        # -------------------------------------------------
        # H1 / H2 = titluri
        # -------------------------------------------------

        if tag in {"H1", "H2"}:
            continue

        # -------------------------------------------------
        # H3 = autori
        # -------------------------------------------------

        if tag in {"H3", "H5"}:

            if text == authors:
                continue

        # -------------------------------------------------
        # H4 care a fost afiliere
        # -------------------------------------------------

        if tag == "H4":

            if text in affiliations:
                continue

        # -------------------------------------------------
        # Footnote = afiliere
        # -------------------------------------------------

        if tag == "Footnote":
            continue

        # -------------------------------------------------
        # LBody = afiliere
        # -------------------------------------------------

        if tag == "LBody":

            if text in affiliations:
                continue

        # -------------------------------------------------
        # Orice P ramas aici este continut.
        # -------------------------------------------------

        if tag == "P":

            content_started = True

            if text:
                paragraphs.append(text)

            continue

        # -------------------------------------------------
        # Pentru robustete:
        # daca apar alte elemente text dupa afilieri,
        # le pastram ca si continut.
        # -------------------------------------------------

        if content_started:

            if text:
                paragraphs.append(text)

    # =====================================================
    # CURATARE CONTINUT
    # =====================================================

    cleaned_paragraphs = []

    for paragraph in paragraphs:

        paragraph = clean_text(paragraph)

        if not paragraph:
            continue

        # Evitam duplicatele consecutive
        if cleaned_paragraphs:
            if paragraph == cleaned_paragraphs[-1]:
                continue

        cleaned_paragraphs.append(
            paragraph
        )

    paragraphs = cleaned_paragraphs

    # =====================================================
    # KEYWORDS DACA NU AU FOST GASITE SEPARAT
    # =====================================================

    if not keywords:

        # Cautam Keywords in toate elementele
        for item in elements:

            text = item["text"]

            if is_keywords_text(text):

                keywords = extract_keywords(text)
                break

    # =====================================================
    # CONTINUT TEXT
    # =====================================================

    content_text = "\n\n".join(
        paragraphs
    )

    # =====================================================
    # REZULTAT
    # =====================================================

    return {
        "title_en": titles["title_en"],
        "title_ro": titles["title_ro"],
        "titles": titles["titles"],

        "authors": authors,

        "affiliations": affiliations,

        "paragraphs": paragraphs,

        "keywords": keywords,

        "content": paragraphs,

        "content_text": content_text,
    }


# =========================================================
# PARSER PRINCIPAL
# =========================================================

def parse_simple_xml(xml_path):
    """
    Parser principal pentru articole simple.

    Citeste XML-ul de autotag si identifica automat
    articolele indiferent de variatiile moderate
    ale structurii XML.
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
    # IDENTIFICARE ARTICOLE
    # =====================================================

    article_sections = find_article_sections(
        root
    )

    articles = []

    # =====================================================
    # PROCESARE ARTICOLE
    # =====================================================

    for section in article_sections:

        article = parse_article_section(
            section
        )

        # -------------------------------------------------
        # Nu adaugam blocuri goale
        # -------------------------------------------------

        if not (
            article["title_en"]
            or article["title_ro"]
            or article["authors"]
            or article["affiliations"]
            or article["paragraphs"]
            or article["keywords"]
        ):
            continue

        articles.append(
            article
        )

    # =====================================================
    # COMPATIBILITATE CU FLUXUL EXISTENT
    # =====================================================

    first_article = (
        articles[0]
        if articles
        else {}
    )

    return {

        "type": "simple",

        "articles": articles,

        # -------------------------------------------------
        # Primul articol - compatibilitate cu builderul
        # -------------------------------------------------

        "title_en": first_article.get(
            "title_en",
            ""
        ),

        "title_ro": first_article.get(
            "title_ro",
            ""
        ),

        "authors": first_article.get(
            "authors",
            ""
        ),

        "affiliations": first_article.get(
            "affiliations",
            []
        ),

        "keywords": first_article.get(
            "keywords",
            ""
        ),

        "content": first_article.get(
            "content",
            []
        ),

        "content_text": first_article.get(
            "content_text",
            ""
        ),
    }
