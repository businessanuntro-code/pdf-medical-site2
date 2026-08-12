import re
import xml.etree.ElementTree as ET


# =========================================================
# FUNCTII GENERALE
# =========================================================

def clean_text(text):
    """
    Curata textul fara sa modifice ordinea sau continutul
    semantic al XML-ului.
    """

    if not text:
        return ""

    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def get_tag(element):
    """
    Returneaza numele tag-ului fara namespace.
    """

    if element is None:
        return ""

    return element.tag.split("}")[-1]


def element_text(element):
    """
    Returneaza tot textul continut de element,
    inclusiv textul elementelor copil.
    """

    if element is None:
        return ""

    text = "".join(element.itertext())

    return clean_text(text)


# =========================================================
# EXTRAGERE STRUCTURA XML
# =========================================================

def parse_element(element):
    """
    Transforma un element XML intr-o structura simpla.

    IMPORTANT:
    Nu interpreteaza continutul.
    Pastreaza tag-ul si textul in ordinea XML-ului.
    """

    tag = get_tag(element)

    # Ignoram elementele tehnice foarte mari
    # care nu contin informatie editoriala utila.
    ignored_tags = {
        "TaggedPDF-doc",
        "Document",
        "Sect",
        "Part",
        "xmpmeta",
        "RDF",
        "Description",
        "History",
        "Seq",
        "li",
    }

    text = element_text(element)

    # -----------------------------------------------------
    # ELEMENTE CU CONTINUT TEXT
    # -----------------------------------------------------

    if text and tag not in ignored_tags:

        return {
            "tag": tag,
            "text": text
        }

    return None


def extract_xml_elements(root):
    """
    Extrage elementele editoriale din XML in EXACTA
    ordine in care apar.

    Nu incearca sa stabileasca:
        - ce este continut
        - ce este autor
        - ce este afiliere
        - ce este titlu

    Aceste reguli vor fi aplicate in simple_builder.py.
    """

    elements = []

    # Tag-uri care ne intereseaza pentru articole simple.
    allowed_tags = {
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
    }

    for element in root.iter():

        tag = get_tag(element)

        if tag not in allowed_tags:
            continue

        # -------------------------------------------------
        # L si LI sunt tratate separat
        # -------------------------------------------------

        if tag in {"L", "LI"}:

            # Pentru L nu extragem textul complet aici,
            # deoarece poate contine LI + Lbl + LBody.
            if tag == "L":
                items = []

                for child in list(element):

                    if get_tag(child) != "LI":
                        continue

                    item_text = element_text(child)

                    if item_text:
                        items.append({
                            "tag": "LI",
                            "text": item_text
                        })

                if items:
                    elements.append({
                        "tag": "L",
                        "items": items
                    })

                continue

            # LI este deja inclus in L.
            continue

        # -------------------------------------------------
        # Lbl / LBody sunt deja incluse in LI
        # -------------------------------------------------

        if tag in {"Lbl", "LBody"}:
            continue

        parsed = parse_element(element)

        if parsed:
            elements.append(parsed)

    return elements


# =========================================================
# EXTRAGERE INFORMATII PENTRU COMPATIBILITATE
# =========================================================

def find_first(elements, tag):
    """
    Gaseste primul element cu tag-ul indicat.
    """

    for element in elements:

        if element.get("tag") == tag:

            text = element.get("text", "")

            if text:
                return text

    return ""


def extract_titles(elements):
    """
    Extrage titlurile doar pentru compatibilitate.

    Nu este folosita pentru a decide structura XML-ului.
    """

    titles = []

    for element in elements:

        if element.get("tag") not in {
            "H1",
            "H2",
            "H4"
        }:
            continue

        text = element.get("text", "")

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


def extract_authors(elements):
    """
    Extrage autorii pentru compatibilitate.

    Prioritatea este H3/H5.

    Daca acestea nu exista, cauta un text care
    seamana cu o lista de autori.
    """

    # -----------------------------------------------------
    # Prima varianta: H3 / H5
    # -----------------------------------------------------

    for element in elements:

        if element.get("tag") not in {
            "H3",
            "H5"
        }:
            continue

        text = clean_text(
            element.get("text", "")
        )

        if text:
            return text

    return ""


def extract_affiliations(elements):
    """
    Extrage afilierile pentru compatibilitate.

    Sunt pastrate elementele Footnote si L.
    """

    affiliations = []

    for element in elements:

        tag = element.get("tag")

        # -------------------------------------------------
        # Footnote
        # -------------------------------------------------

        if tag == "Footnote":

            text = clean_text(
                element.get("text", "")
            )

            if text:

                number_match = re.match(
                    r"^\s*(\d+)\s*\.\s*(.*)$",
                    text
                )

                if number_match:

                    affiliations.append({
                        "number": number_match.group(1),
                        "text": clean_text(
                            number_match.group(2)
                        )
                    })

                else:

                    affiliations.append({
                        "number": "",
                        "text": text
                    })

        # -------------------------------------------------
        # L
        # -------------------------------------------------

        elif tag == "L":

            for item in element.get(
                "items",
                []
            ):

                text = clean_text(
                    item.get("text", "")
                )

                if not text:
                    continue

                number_match = re.match(
                    r"^\s*(\d+)\s*\.\s*(.*)$",
                    text
                )

                if number_match:

                    affiliations.append({
                        "number": number_match.group(1),
                        "text": clean_text(
                            number_match.group(2)
                        )
                    })

                else:

                    affiliations.append({
                        "number": "",
                        "text": text
                    })

    return affiliations


# =========================================================
# KEYWORDS
# =========================================================

def is_keywords(text):
    """
    Verifica daca textul este Keywords,
    indiferent daca XML-ul foloseste P, H5, H4 etc.
    """

    if not text:
        return False

    normalized = clean_text(text).lower()

    return (
        normalized.startswith("keywords:")
        or normalized.startswith("keywords :")
        or normalized.startswith("cuvinte cheie:")
        or normalized.startswith("cuvinte cheie :")
    )


def extract_keywords(elements):
    """
    Cauta Keywords indiferent de tag.
    """

    for element in reversed(elements):

        text = clean_text(
            element.get("text", "")
        )

        if not text:
            continue

        if not is_keywords(text):
            continue

        match = re.match(
            r"^\s*(?:keywords|cuvinte\s+cheie)\s*:\s*(.*)$",
            text,
            flags=re.IGNORECASE
        )

        if match:

            return clean_text(
                match.group(1)
            )

        return text

    return ""


# =========================================================
# CONTINUT
# =========================================================

def extract_content(elements):
    """
    Extrage paragrafele de continut pentru compatibilitate.

    IMPORTANT:

    Aceasta functie NU mai este folosita pentru a construi
    structura principala.

    Structura principala ramane elements.
    """

    paragraphs = []

    for element in elements:

        if element.get("tag") != "P":
            continue

        text = clean_text(
            element.get("text", "")
        )

        if not text:
            continue

        if is_keywords(text):
            continue

        paragraphs.append(text)

    return paragraphs


# =========================================================
# ARTICOL SIMPLU
# =========================================================

def parse_article(elements):
    """
    Construieste datele unui articol simplu.

    'elements' reprezinta structura principala si pastreaza
    ordinea originala din XML.
    """

    titles = extract_titles(elements)

    authors = extract_authors(elements)

    affiliations = extract_affiliations(elements)

    keywords = extract_keywords(elements)

    paragraphs = extract_content(elements)

    return {
        # -------------------------------------------------
        # STRUCTURA ORIGINALA
        # -------------------------------------------------

        "elements": elements,

        # -------------------------------------------------
        # CAMPURI PENTRU COMPATIBILITATE
        # -------------------------------------------------

        "title_en": titles["title_en"],

        "title_ro": titles["title_ro"],

        "titles": titles["titles"],

        "authors": authors,

        "affiliations": affiliations,

        "paragraphs": paragraphs,

        "keywords": keywords,

        "content": paragraphs,

        "content_text": "\n\n".join(
            paragraphs
        )
    }


# =========================================================
# IDENTIFICARE ARTICOLE
# =========================================================

def split_articles(elements):
    """
    Imparte XML-ul in articole.

    Pentru XML-urile generate prin AutoTag:
    H1 reprezinta de regula inceputul unui articol.

    Daca exista un singur H1, tot documentul este considerat
    un singur articol.

    Daca exista mai multe H1, fiecare H1 incepe un articol nou.
    """

    articles = []

    current = []

    for element in elements:

        tag = element.get("tag")

        # -------------------------------------------------
        # Un nou H1 poate marca inceputul unui articol
        # -------------------------------------------------

        if tag == "H1" and current:

            articles.append(current)

            current = []

        current.append(element)

    if current:

        articles.append(current)

    return articles


# =========================================================
# PARSER PRINCIPAL
# =========================================================

def parse_simple_xml(xml_path):
    """
    Parser principal pentru articole simple.

    NOUA LOGICA:

    XML
      ↓
    citim elementele
      ↓
    pastram ordinea exacta
      ↓
    trimitem structura catre builder

    Parserul NU mai incearca sa reconstruiasca agresiv
    articolul.
    """

    try:

        tree = ET.parse(xml_path)

        root = tree.getroot()

    except ET.ParseError as exc:

        raise ValueError(
            f"XML invalid sau imposibil de procesat: {exc}"
        ) from exc

    # -----------------------------------------------------
    # EXTRAGEM STRUCTURA XML
    # -----------------------------------------------------

    elements = extract_xml_elements(root)

    if not elements:

        return {
            "type": "simple",
            "articles": [],
            "elements": []
        }

    # -----------------------------------------------------
    # IMPARTIM IN ARTICOLE
    # -----------------------------------------------------

    article_groups = split_articles(
        elements
    )

    articles = []

    for group in article_groups:

        if not group:
            continue

        article = parse_article(
            group
        )

        # Verificam daca exista continut real.

        has_content = any(
            item.get("text")
            for item in group
            if isinstance(item, dict)
        )

        if not has_content:
            continue

        articles.append(
            article
        )

    # -----------------------------------------------------
    # COMPATIBILITATE CU FLUXUL EXISTENT
    # -----------------------------------------------------

    first_article = (
        articles[0]
        if articles
        else {}
    )

    return {
        "type": "simple",

        # Lista completa a articolelor
        "articles": articles,

        # Structura XML completa
        "elements": elements,

        # Campuri compatibilitate
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
        )
    }
