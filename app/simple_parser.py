import re
import xml.etree.ElementTree as ET


# =========================================================
# FUNCTII GENERALE
# =========================================================

def clean_text(text):
    """
    Normalizeaza textul extras din XML.
    """

    if not text:
        return ""

    text = text.replace("\xa0", " ")
    text = text.replace("\u200b", "")
    text = text.replace("\ufeff", "")

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
    Returneaza tot textul continut de un element.
    """

    if element is None:
        return ""

    return clean_text(
        "".join(element.itertext())
    )


# =========================================================
# KEYWORDS
# =========================================================

def is_keywords_text(text):
    """
    Verifica daca textul incepe cu:

    Keywords:
    Keywords :
    Cuvinte cheie:
    Cuvinte cheie :
    """

    if not text:
        return False

    text = clean_text(text)

    return bool(
        re.match(
            r"^(?:Keywords|Cuvinte\s+cheie)\s*:",
            text,
            flags=re.IGNORECASE
        )
    )


def split_keywords_from_text(text):
    """
    Separa continutul de Keywords chiar daca apar
    in acelasi paragraf.

    Exemplu:

    Text articol. Keywords: cancer, radiotherapy

    devine:

    continut:
        Text articol.

    keywords:
        cancer, radiotherapy
    """

    if not text:
        return "", ""

    text = clean_text(text)

    match = re.search(
        r"(?:Keywords|Cuvinte\s+cheie)\s*:",
        text,
        flags=re.IGNORECASE
    )

    if not match:
        return text, ""

    before = clean_text(
        text[:match.start()]
    )

    after = clean_text(
        text[match.end():]
    )

    return before, after


# =========================================================
# AUTORI
# =========================================================

def looks_like_authors(text):
    """
    Verifica daca textul pare sa fie o lista de autori.

    Exemple:

    C. Achiroaei1,2, Diana-Ioana Panaite1,2, C. Volovăț1,2

    Ancuța-Elena Baciu1, Irina-Maria Dumitru1,2

    Eugen Brătucu, Claudiu Daha, Laurenţiu Simion
    """

    if not text:
        return False

    text = clean_text(text)

    if not text:
        return False

    if len(text) > 600:
        return False

    if is_keywords_text(text):
        return False

    # Un paragraf normal de continut este de regula
    # mult mai lung.
    if len(text.split()) > 60:
        return False

    # Autorii sunt separati de regula prin virgula.
    parts = [
        part.strip()
        for part in text.split(",")
        if part.strip()
    ]

    if len(parts) < 2:
        return False

    # Daca apar semne specifice de propozitie,
    # este mai probabil continut.
    if text.count(".") > 8:
        return False

    valid_parts = 0

    for part in parts:

        # Eliminam eventualele numere de afiliere.
        clean_part = re.sub(
            r"\s*\d+(?:\s*,\s*\d+)*\s*$",
            "",
            part
        ).strip()

        if not clean_part:
            continue

        # Trebuie sa existe litere.
        if re.search(
            r"[A-Za-zÀ-ÖØ-öø-ÿĂăÂâÎîȘșŞşȚțŢţ]",
            clean_part
        ):
            valid_parts += 1

    return valid_parts >= 2


def normalize_authors(text):
    """
    Curata textul autorilor fara sa elimine numerele
    de afiliere.

    Exemplu:

    C. Achiroaei1,2, Diana-Ioana Panaite1,2

    ramane neschimbat logic.
    """

    return clean_text(text)


# =========================================================
# AFILIERI
# =========================================================

def looks_like_affiliation(text):
    """
    Identifica o afiliere dupa continut.

    Exemple:

    Institute of Oncology, Bucharest, Romania

    Faculty of Physics, University of Bucharest, Romania

    Fundeni Clinical Institute, Bucharest, Romania
    """

    if not text:
        return False

    text = clean_text(text)

    if not text:
        return False

    if len(text) > 600:
        return False

    lower = text.lower()

    affiliation_terms = [
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
        "clinic",
        "laborator",
        "departament",
        "centru",
        "românia",
    ]

    for term in affiliation_terms:

        if term in lower:
            return True

    # Afiliere numerotata.
    if re.match(
        r"^\s*\d+\.",
        text
    ):
        return True

    return False


def clean_affiliation(text):
    """
    Elimina numarul de afiliere de la inceput.
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


# =========================================================
# TITLURI
# =========================================================

def collect_titles(elements):
    """
    Identifica titlurile din fluxul XML.

    Prioritate:

    H1 = title EN
    H2 = title RO

    Daca avem doua H2 consecutive:

    H2 = title EN
    H2 = title RO
    """

    titles = []

    for item in elements:

        tag = item["tag"]
        text = item["text"]

        if tag not in {"H1", "H2"}:
            continue

        if not text:
            continue

        titles.append({
            "tag": tag,
            "text": text
        })

    title_en = ""
    title_ro = ""

    h1 = [
        item["text"]
        for item in titles
        if item["tag"] == "H1"
    ]

    h2 = [
        item["text"]
        for item in titles
        if item["tag"] == "H2"
    ]

    if h1:

        title_en = h1[0]

        if h2:
            title_ro = h2[0]

    elif len(h2) >= 2:

        title_en = h2[0]
        title_ro = h2[1]

    elif len(h2) == 1:

        # In unele XML-uri titlul EN si RO sunt
        # lipite in acelasi H2.
        title_en = h2[0]

    return title_en, title_ro


# =========================================================
# FLUX XML
# =========================================================

def flatten_xml(root):
    """
    Creeaza o lista liniara cu elementele importante
    exact in ordinea in care apar in XML.

    Nu depinde de structura Sect.
    """

    result = []

    for element in root.iter():

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

        result.append({
            "element": element,
            "tag": tag,
            "text": text
        })

    return result


# =========================================================
# DETECTARE TITLU ARTICOL
# =========================================================

def is_article_start(item):
    """
    Un articol nou incepe de regula cu H1 sau H2.
    """

    return item["tag"] in {
        "H1",
        "H2"
    }


# =========================================================
# PARSARE UN BLOC DE ARTICOL
# =========================================================

def parse_article_block(block):
    """
    Proceseaza un articol din fluxul liniar.

    Ordinea:

        TITLU
        AUTORI
        AFILIERI
        CONTINUT
        KEYWORDS
    """

    if not block:
        return None

    # =====================================================
    # TITLURI
    # =====================================================

    title_en, title_ro = collect_titles(
        block
    )

    # =====================================================
    # AUTORI
    # =====================================================

    authors = ""

    author_index = -1

    # Mai intai H3 / H5.
    for index, item in enumerate(block):

        if item["tag"] not in {
            "H3",
            "H5"
        }:
            continue

        text = item["text"]

        if looks_like_authors(text):

            authors = normalize_authors(
                text
            )

            author_index = index

            break

    # Daca nu exista H3/H5,
    # cautam in P.
    if not authors:

        for index, item in enumerate(block):

            if item["tag"] != "P":
                continue

            text = item["text"]

            if looks_like_authors(text):

                authors = normalize_authors(
                    text
                )

                author_index = index

                break

    # =====================================================
    # AFILIERI
    # =====================================================

    affiliations = []

    affiliation_end = author_index

    # Dupa autori cautam afilierile.
    for index in range(
        author_index + 1,
        len(block)
    ):

        item = block[index]

        tag = item["tag"]
        text = item["text"]

        # Keywords inseamna ca am trecut de afiliere.
        if is_keywords_text(text):
            break

        if tag == "Footnote":

            affiliation = clean_affiliation(
                text
            )

            if affiliation and affiliation not in affiliations:

                affiliations.append(
                    affiliation
                )

                affiliation_end = index

            continue

        if tag == "LBody":

            affiliation = clean_affiliation(
                text
            )

            if affiliation and looks_like_affiliation(
                affiliation
            ):

                if affiliation not in affiliations:

                    affiliations.append(
                        affiliation
                    )

                affiliation_end = index

            continue

        if tag == "H4":

            affiliation = clean_affiliation(
                text
            )

            if affiliation and looks_like_affiliation(
                affiliation
            ):

                if affiliation not in affiliations:

                    affiliations.append(
                        affiliation
                    )

                affiliation_end = index

            continue

    # =====================================================
    # CONTINUT + KEYWORDS
    # =====================================================

    paragraphs = []

    keywords = ""

    content_started = False

    # Continutul incepe dupa afiliere.
    start_index = max(
        affiliation_end + 1,
        author_index + 1
    )

    for index in range(
        start_index,
        len(block)
    ):

        item = block[index]

        tag = item["tag"]
        text = item["text"]

        if not text:
            continue

        # -------------------------------------------------
        # TITLURI
        # -------------------------------------------------

        if tag in {
            "H1",
            "H2"
        }:
            continue

        # -------------------------------------------------
        # AUTORI
        # -------------------------------------------------

        if tag in {
            "H3",
            "H5"
        }:

            if text == authors:
                continue

        # -------------------------------------------------
        # AFILIERI
        # -------------------------------------------------

        if tag in {
            "H4",
            "Footnote",
            "LBody",
            "Lbl"
        }:

            if clean_affiliation(text) in affiliations:
                continue

        # -------------------------------------------------
        # Keywords in acelasi P cu continutul
        # -------------------------------------------------

        if tag == "P":

            content_part, keyword_part = (
                split_keywords_from_text(text)
            )

            # Avem text inainte de Keywords.
            if content_part:

                paragraphs.append(
                    content_part
                )

                content_started = True

            # Am gasit Keywords.
            if keyword_part:

                keywords = keyword_part
                break

            # P normal.
            if content_part and not keyword_part:

                continue

        # -------------------------------------------------
        # Daca apare Keywords in alt element
        # -------------------------------------------------

        if is_keywords_text(text):

            keywords = extract_keywords(
                text
            )

            break

        # -------------------------------------------------
        # Alte elemente text dupa continut
        # -------------------------------------------------

        if content_started:

            if tag not in {
                "H1",
                "H2",
                "H3",
                "H4",
                "H5",
                "Footnote",
                "LBody",
                "Lbl"
            }:

                paragraphs.append(
                    clean_text(text)
                )

    # =====================================================
    # ELIMINARE DUPLICATE
    # =====================================================

    final_paragraphs = []

    for paragraph in paragraphs:

        paragraph = clean_text(
            paragraph
        )

        if not paragraph:
            continue

        if final_paragraphs:

            if paragraph == final_paragraphs[-1]:
                continue

        final_paragraphs.append(
            paragraph
        )

    paragraphs = final_paragraphs

    # =====================================================
    # CONTINUT FINAL
    # =====================================================

    content_text = "\n\n".join(
        paragraphs
    )

    # =====================================================
    # REZULTAT
    # =====================================================

    return {
        "title_en": clean_text(
            title_en
        ),

        "title_ro": clean_text(
            title_ro
        ),

        "titles": [
            title
            for title in [
                title_en,
                title_ro
            ]
            if title
        ],

        "authors": authors,

        "affiliations": affiliations,

        "paragraphs": paragraphs,

        "keywords": clean_text(
            keywords
        ),

        "content": paragraphs,

        "content_text": content_text,
    }


# =========================================================
# SEPARAREA ARTICOLELOR
# =========================================================

def split_articles(flat_elements):
    """
    Imparte fluxul XML in articole.

    Regula:

    un nou H1/H2 dupa ce avem deja continut
    inseamna inceputul urmatorului articol.

    Important:
    nu folosim Sect.
    """

    articles = []

    current = []

    for item in flat_elements:

        # -------------------------------------------------
        # Primul titlu
        # -------------------------------------------------

        if not current:

            if is_article_start(item):

                current.append(item)

            continue

        # -------------------------------------------------
        # H1/H2 nou
        # -------------------------------------------------

        if is_article_start(item):

            # Daca avem deja un titlu si continut,
            # inchidem articolul anterior.
            has_content = any(
                element["tag"] == "P"
                for element in current
            )

            has_authors = any(
                element["tag"] in {
                    "H3",
                    "H5"
                }
                for element in current
            )

            if has_content or has_authors:

                articles.append(
                    current
                )

                current = [
                    item
                ]

                continue

        current.append(
            item
        )

    # Ultimul articol
    if current:

        articles.append(
            current
        )

    return articles


# =========================================================
# PARSER PRINCIPAL
# =========================================================

def parse_simple_xml(xml_path):
    """
    Parser principal pentru articole simple.

    XML-ul este citit liniar.

    Nu foloseste structura Sect pentru extragerea
    continutului.

    Informatiile sunt extrase astfel:

        1. Titlu/titluri
        2. Autori
        3. Afilieri
        4. Toate blocurile de continut
        5. Keywords
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
    # FLATTEN XML
    # =====================================================

    flat_elements = flatten_xml(
        root
    )

    # =====================================================
    # SEPARARE ARTICOLE
    # =====================================================

    article_blocks = split_articles(
        flat_elements
    )

    articles = []

    # =====================================================
    # PARSARE ARTICOLE
    # =====================================================

    for block in article_blocks:

        article = parse_article_block(
            block
        )

        if not article:
            continue

        # Ignoram blocurile care nu contin
        # absolut nimic relevant.
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
    # COMPATIBILITATE CU BUILDERUL EXISTENT
    # =====================================================

    first_article = (
        articles[0]
        if articles
        else {}
    )

    return {

        "type": "simple",

        "articles": articles,

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
