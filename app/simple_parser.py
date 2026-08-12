import re
import xml.etree.ElementTree as ET


# =========================================================
# FUNCTII GENERALE
# =========================================================

def tag_name(element):
    """
    Returneaza numele tagului XML fara namespace.
    """

    return element.tag.split("}")[-1]


def clean_text(text):
    """
    Curata textul extras din XML.

    - elimina non-breaking space
    - normalizeaza spatiile
    - elimina spatiile de la inceput si sfarsit
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

    return clean_text(
        "".join(element.itertext())
    )


# =========================================================
# KEYWORDS
# =========================================================

def is_keywords(text):
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

    return (
        normalized.startswith("keywords:")
        or normalized.startswith("keywords :")
        or normalized.startswith("cuvinte cheie:")
        or normalized.startswith("cuvinte cheie :")
    )


def extract_keywords(text):
    """
    Extrage doar continutul de dupa:

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
        return clean_text(
            match.group(1)
        )

    return clean_text(text)


# =========================================================
# EXTRAGERE BLOCURI XML
# =========================================================

def xml_to_blocks(element):
    """
    Citeste XML-ul in ordinea in care apare.

    Nu extrage separat toate H4/H5/P din document.

    Pastreaza ordinea reala a blocurilor.

    Blocuri recunoscute:

        H2
        H4
        H5
        AFFILIATION
        P
        KEYWORDS
    """

    blocks = []

    def walk(node):

        current_tag = tag_name(node)

        # -------------------------------------------------
        # H2
        # -------------------------------------------------

        if current_tag == "H2":

            text = element_text(node)

            if text:

                blocks.append({
                    "type": "H2",
                    "text": text
                })

            return

        # -------------------------------------------------
        # H4
        # -------------------------------------------------

        if current_tag == "H4":

            text = element_text(node)

            if text:

                blocks.append({
                    "type": "H4",
                    "text": text
                })

            return

        # -------------------------------------------------
        # H5
        # -------------------------------------------------

        if current_tag == "H5":

            text = element_text(node)

            if text:

                blocks.append({
                    "type": "H5",
                    "text": text
                })

            return

        # -------------------------------------------------
        # P
        # -------------------------------------------------

        if current_tag == "P":

            text = element_text(node)

            if not text:
                return

            # Keywords sunt separate de continut.

            if is_keywords(text):

                blocks.append({
                    "type": "KEYWORDS",
                    "text": extract_keywords(text),
                    "raw_text": text
                })

            else:

                blocks.append({
                    "type": "P",
                    "text": text
                })

            return

        # -------------------------------------------------
        # L = AFILIERI
        # -------------------------------------------------

        if current_tag == "L":

            for li in list(node):

                if tag_name(li) != "LI":
                    continue

                number = ""
                body = ""

                for child in list(li):

                    child_tag = tag_name(child)

                    if child_tag == "Lbl":

                        number = clean_text(
                            element_text(child)
                        )

                    elif child_tag == "LBody":

                        body = clean_text(
                            element_text(child)
                        )

                # Pastram doar cifra.

                number = re.sub(
                    r"[^\d]",
                    "",
                    number
                )

                if body:

                    blocks.append({
                        "type": "AFFILIATION",
                        "number": number,
                        "text": body
                    })

            return

        # -------------------------------------------------
        # ALTE TAGURI
        # -------------------------------------------------

        for child in list(node):

            walk(child)

    walk(element)

    return blocks


# =========================================================
# IDENTIFICARE ARTICOLE
# =========================================================

def split_into_articles(blocks):
    """
    Imparte blocurile in articole.

    REGULA PRINCIPALA:

    Un articol incepe cu primul H4.

    Urmatorul H4 incepe un articol nou numai
    daca articolul curent are deja continut.

    Astfel putem avea:

        H4
        H4
        H5
        AFFILIATION
        P
        KEYWORDS

    pentru un singur articol.

    Dupa KEYWORDS, urmatorul H4
    incepe urmatorul articol.
    """

    articles = []

    current = []

    has_content = False

    for block in blocks:

        block_type = block.get("type")

        # -------------------------------------------------
        # H4
        # -------------------------------------------------

        if block_type == "H4":

            # Daca avem deja un articol care contine
            # informatii, H4-ul nou incepe alt articol.

            if current and has_content:

                articles.append(current)

                current = []

                has_content = False

            current.append(block)

            continue

        # -------------------------------------------------
        # CONTINUT ARTICOL
        # -------------------------------------------------

        if current:

            current.append(block)

            if block_type in (
                "H5",
                "AFFILIATION",
                "P",
                "KEYWORDS"
            ):

                has_content = True

    # -----------------------------------------------------
    # ULTIMUL ARTICOL
    # -----------------------------------------------------

    if current:

        articles.append(current)

    return articles


# =========================================================
# EXTRAGERE DATE ARTICOL
# =========================================================

def extract_article_data(blocks):
    """
    Extrage STRICT urmatoarele informatii:

        1. primul H4  -> title_en
        2. al doilea H4 -> title_ro
        3. autorii
        4. afilierile
        5. continutul
        6. keywords

    Ordinea XML este pastrata.
    """

    # -----------------------------------------------------
    # TITLURI
    # -----------------------------------------------------

    h4s = []

    # -----------------------------------------------------
    # AUTORI
    # -----------------------------------------------------

    authors_parts = []

    # -----------------------------------------------------
    # AFILIERI
    # -----------------------------------------------------

    affiliations = []

    # -----------------------------------------------------
    # CONTINUT
    # -----------------------------------------------------

    paragraphs = []

    # -----------------------------------------------------
    # KEYWORDS
    # -----------------------------------------------------

    keywords = ""

    # -----------------------------------------------------
    # STAREA ARTICOLULUI
    # -----------------------------------------------------

    titles_finished = False
    authors_finished = False
    affiliations_started = False
    content_started = False

    for block in blocks:

        block_type = block.get("type")

        text = clean_text(
            block.get("text", "")
        )

        # =================================================
        # TITLURI
        # =================================================

        if block_type == "H4":

            if len(h4s) < 2:

                h4s.append(text)

            continue

        # =================================================
        # AUTORI
        # =================================================

        if block_type == "H5":

            if text:

                authors_parts.append(text)

                titles_finished = True

            continue

        # =================================================
        # AFILIERI
        # =================================================

        if block_type == "AFFILIATION":

            affiliations_started = True
            authors_finished = True

            affiliation_text = clean_text(
                block.get("text", "")
            )

            if affiliation_text:

                affiliations.append({
                    "number": clean_text(
                        block.get("number", "")
                    ),
                    "text": affiliation_text
                })

            continue

        # =================================================
        # KEYWORDS
        # =================================================

        if block_type == "KEYWORDS":

            keywords = clean_text(
                block.get("text", "")
            )

            continue

        # =================================================
        # CONTINUT
        # =================================================

        if block_type == "P":

            if text:

                content_started = True

                paragraphs.append(text)

            continue

    # =====================================================
    # TITLE EN
    # =====================================================

    title_en = ""

    if len(h4s) >= 1:

        title_en = h4s[0]

    # =====================================================
    # TITLE RO
    # =====================================================

    title_ro = ""

    if len(h4s) >= 2:

        title_ro = h4s[1]

    # =====================================================
    # AUTORI
    # =====================================================

    authors = ", ".join(
        part
        for part in authors_parts
        if part
    )

    # =====================================================
    # REZULTAT
    # =====================================================

    return {

        # Titluri
        "title_en": title_en,
        "title_ro": title_ro,

        # Pastram si lista pentru compatibilitate
        "titles": h4s,

        # Autori
        "authors": authors,

        # Afilieri
        "affiliations": affiliations,

        # Continut
        "paragraphs": paragraphs,

        "content": paragraphs,

        "content_text": "\n\n".join(
            paragraphs
        ),

        # Keywords
        "keywords": keywords
    }


# =========================================================
# PARSER PRINCIPAL - ARTICOLE SIMPLE
# =========================================================

def parse_simple_xml(xml_path):
    """
    Parser principal pentru ARTICOLE SIMPLE.

    IMPORTANT:

    Acest parser este complet separat de:

        parser.py

    si este folosit exclusiv pentru:

        articole simple
    """

    # =====================================================
    # CITIRE XML
    # =====================================================

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
    # GASIM PART-URILE
    # =====================================================

    parts = []

    for element in root.iter():

        if tag_name(element) == "Part":

            parts.append(element)

    # Daca XML-ul nu are Part,
    # procesam documentul complet.

    if not parts:

        parts = [root]

    # =====================================================
    # LISTA ARTICOLE
    # =====================================================

    articles = []

    # =====================================================
    # PROCESARE PART
    # =====================================================

    for part in parts:

        # -------------------------------------------------
        # H2 - TITLU SECTIUNE
        # -------------------------------------------------

        section_title = ""

        for child in list(part):

            if tag_name(child) != "H2":
                continue

            text = element_text(
                child
            )

            if text:

                section_title = text

                break

        # -------------------------------------------------
        # XML → BLOCKS
        # -------------------------------------------------

        blocks = xml_to_blocks(
            part
        )

        # -------------------------------------------------
        # H2 NU ESTE CONTINUTUL ARTICOLULUI
        # -------------------------------------------------

        article_blocks = [

            block

            for block in blocks

            if block.get("type") != "H2"

        ]

        # -------------------------------------------------
        # IMPARTIM IN ARTICOLE
        # -------------------------------------------------

        article_groups = split_into_articles(
            article_blocks
        )

        # -------------------------------------------------
        # PROCESAM FIECARE ARTICOL
        # -------------------------------------------------

        for group in article_groups:

            if not group:
                continue

            article = extract_article_data(
                group
            )

            # -------------------------------------------------
            # PASTRAM BLOCKURILE ORIGINALE
            # -------------------------------------------------

            article["blocks"] = group

            # -------------------------------------------------
            # TITLU SECTIUNE
            # -------------------------------------------------

            article["section_title"] = (
                section_title
            )

            # -------------------------------------------------
            # IGNORAM GRUPURILE GOALE
            # -------------------------------------------------

            if not (
                article["title_en"]
                or article["title_ro"]
                or article["authors"]
                or article["paragraphs"]
                or article["keywords"]
            ):

                continue

            articles.append(
                article
            )

    # =====================================================
    # PRIMUL ARTICOL
    # =====================================================

    first_article = (
        articles[0]
        if articles
        else {}
    )

    # =====================================================
    # REZULTAT FINAL
    # =====================================================

    return {

        "type": "simple",

        # Lista completa
        "articles": articles,

        # Primul articol
        # pentru compatibilitate

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

        "blocks": first_article.get(
            "blocks",
            []
        )
    }
