
import re
import xml.etree.ElementTree as ET


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
    Curata textul:
    - elimina non-breaking spaces
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
    Returneaza tot textul continut de element,
    inclusiv textul elementelor copil.
    """

    if element is None:
        return ""

    return clean_text("".join(element.itertext()))


# =========================================================
# KEYWORDS
# =========================================================

def is_keywords(text):
    """
    Verifica daca un text reprezinta Keywords.
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
    Extrage textul de dupa Keywords: / Cuvinte cheie:
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
# ELEMENTE XML → STRUCTURA SIMPLA
# =========================================================

def xml_to_blocks(element):
    """
    Transforma continutul XML intr-o lista ordonata de blocuri.

    IMPORTANT:

    Ordinea este pastrata exact asa cum apare in XML.

    Nu mai cautam separat:
        - toate H4
        - toate H5
        - toate P
        - toate L

    ci pastram ordinea documentului.

    Exemple de blocuri:

        {
            "type": "H4",
            "text": "Titlu..."
        }

        {
            "type": "H5",
            "text": "Autor..."
        }

        {
            "type": "P",
            "text": "Text..."
        }

        {
            "type": "AFFILIATION",
            "number": "1",
            "text": "Institute..."
        }

        {
            "type": "KEYWORDS",
            "text": "cervical cancers..."
        }
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
        # L
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
# EXTRAGERE INFORMATII DIN BLOCURI
# =========================================================

def extract_article_data(blocks):
    """
    Creeaza campurile clasice ale articolului pornind
    de la lista ordonata de blocuri.

    Lista blocks ramane principala sursa pentru builder.
    """

    h4s = []
    authors = ""
    affiliations = []
    paragraphs = []
    keywords = ""

    for block in blocks:

        block_type = block.get("type")

        # -------------------------------------------------
        # TITLURI
        # -------------------------------------------------

        if block_type == "H4":

            h4s.append(
                block.get("text", "")
            )

        # -------------------------------------------------
        # AUTORI
        # -------------------------------------------------

        elif block_type == "H5":

            text = block.get("text", "")

            if text:

                if authors:

                    authors += " " + text

                else:

                    authors = text

        # -------------------------------------------------
        # AFILIERI
        # -------------------------------------------------

        elif block_type == "AFFILIATION":

            affiliations.append({
                "number": block.get("number", ""),
                "text": block.get("text", "")
            })

        # -------------------------------------------------
        # PARAGRAFE
        # -------------------------------------------------

        elif block_type == "P":

            text = block.get("text", "")

            if text:

                paragraphs.append(text)

        # -------------------------------------------------
        # KEYWORDS
        # -------------------------------------------------

        elif block_type == "KEYWORDS":

            keywords = block.get("text", "")

    title_en = ""
    title_ro = ""

    if len(h4s) >= 1:

        title_en = h4s[0]

    if len(h4s) >= 2:

        title_ro = " ".join(
            h4s[1:]
        )

    return {
        "title_en": title_en,

        "title_ro": title_ro,

        "titles": h4s,

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

def split_into_articles(blocks):
    """
    Imparte lista ordonata de blocuri in articole.

    REGULA:

    Un articol incepe la un H4.

    Toate H4 consecutive pana la primul H5
    fac parte din titlul articolului.

    Dupa H5, continutul apartine aceluiasi articol.

    Urmatorul H4 dupa ce articolul are deja continut
    incepe un articol nou.

    Astfel nu mai depindem de Sect-urile imbricate.
    """

    articles = []

    current = []

    has_author_or_content = False

    for block in blocks:

        block_type = block.get("type")

        # -------------------------------------------------
        # H4
        # -------------------------------------------------

        if block_type == "H4":

            # Daca avem deja un articol complet,
            # incepe unul nou.
            if (
                current
                and has_author_or_content
            ):

                articles.append(current)

                current = []

                has_author_or_content = False

            current.append(block)

            continue

        # -------------------------------------------------
        # CONTINUT ARTICOL
        # -------------------------------------------------

        if current:

            current.append(block)

            if block_type in (
                "H5",
                "P",
                "KEYWORDS",
                "AFFILIATION"
            ):

                has_author_or_content = True

    # -----------------------------------------------------
    # ULTIMUL ARTICOL
    # -----------------------------------------------------

    if current:

        articles.append(current)

    return articles


# =========================================================
# PARSER PRINCIPAL
# =========================================================

def parse_simple_xml(xml_path):
    """
    Parser principal pentru ARTICOLE SIMPLE.

    IMPORTANT:

    Acest parser nu foloseste parser.py.

    Structura XML este citita in ordinea documentului
    si transformata intr-o lista de blocks.

    Builderul poate decide ulterior cum afiseaza fiecare
    tip de block.
    """

    try:

        tree = ET.parse(xml_path)
        root = tree.getroot()

    except ET.ParseError as exc:

        raise ValueError(
            f"XML invalid sau imposibil de procesat: {exc}"
        ) from exc

    # =====================================================
    # PARCURGEREA PART-URILOR
    # =====================================================

    parts = []

    for element in root.iter():

        if tag_name(element) == "Part":

            parts.append(element)

    # Daca nu exista Part,
    # folosim documentul complet.

    if not parts:

        parts = [root]

    articles = []

    # =====================================================
    # PROCESARE PART
    # =====================================================

    for part in parts:

        # -------------------------------------------------
        # TITLU SECTIUNE / CONFERINTA
        # -------------------------------------------------

        section_title = ""

        for child in list(part):

            if tag_name(child) != "H2":
                continue

            text = element_text(child)

            if text:

                section_title = text
                break

        # -------------------------------------------------
        # XML → BLOCKS
        # -------------------------------------------------

        blocks = xml_to_blocks(part)

        # Eliminam H2 din blocks deoarece este
        # titlul Part-ului, nu continutul articolului.

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

        for article_blocks_group in article_groups:

            # ---------------------------------------------
            # EXTRAGEM DATELE CLASICE
            # ---------------------------------------------

            article_data = extract_article_data(
                article_blocks_group
            )

            # ---------------------------------------------
            # PASTRAM STRUCTURA ORIGINALA
            # ---------------------------------------------

            article_data["blocks"] = (
                article_blocks_group
            )

            article_data["section_title"] = (
                section_title
            )

            # ---------------------------------------------
            # IGNORAM GRUPURILE FARA CONTINUT
            # ---------------------------------------------

            if not (
                article_data["title_en"]
                or article_data["title_ro"]
                or article_data["authors"]
                or article_data["paragraphs"]
            ):

                continue

            articles.append(
                article_data
            )

    # =====================================================
    # REZULTAT FINAL
    # =====================================================

    first_article = (
        articles[0]
        if articles
        else {}
    )

    return {

        "type": "simple",

        # -------------------------------------------------
        # LISTA COMPLETA DE ARTICOLE
        # -------------------------------------------------

        "articles": articles,

        # -------------------------------------------------
        # PRIMUL ARTICOL - COMPATIBILITATE
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

        # -------------------------------------------------
        # BLOCKS PRIMULUI ARTICOL
        # -------------------------------------------------

        "blocks": first_article.get(
            "blocks",
            []
        )
    }

