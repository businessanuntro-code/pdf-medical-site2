import re
import xml.etree.ElementTree as ET


# =========================================================
# SIMPLE PARSER
#
# ARTICOLE SIMPLE
#
# REGULA PRINCIPALA:
#
# Nu ne bazam strict pe H4 / H5 / P.
#
# Interpretam articolul dupa POZITIA informatiei:
#
# 1. KEYWORDS
# 2. CONTINUT
# 3. AFILIERI
# 4. AUTORI
# 5. TITLU / TITLURI
#
# Fluxul articolelor stiintifice NU este afectat.
# =========================================================


# =========================================================
# UTILITARE GENERALE
# =========================================================

def tag_name(element):
    """
    Returneaza numele tagului fara namespace.
    """

    return element.tag.split("}")[-1]


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


def element_text(element):
    """
    Returneaza tot textul continut de element,
    inclusiv elementele copil.
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
    Detecteaza:

        Keywords:

    sau:

        Cuvinte cheie:
    """

    if not text:
        return False

    normalized = clean_text(text).lower()

    return bool(
        re.match(
            r"^(?:keywords|cuvinte\s+cheie)\s*:",
            normalized,
            flags=re.IGNORECASE
        )
    )


def extract_keywords(text):
    """
    Extrage numai continutul de dupa:

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
    Transforma XML-ul intr-o lista ORDONATA de blocuri.

    Nu eliminam informatia in functie de tag.

    Pastram:
        H2
        H4
        H5
        P
        L / LBody
        alte texte relevante

    IMPORTANT:
    Ordinea XML-ului este pastrata.
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

            if text:

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
        #
        # Afiliarile pot fi in:
        #
        # <L>
        #   <LI>
        #       <Lbl>1.</Lbl>
        #       <LBody>...</LBody>
        #   </LI>
        # </L>
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
                        "type": "L",
                        "number": number,
                        "text": body
                    })

            return

        # -------------------------------------------------
        # ALTE ELEMENTE
        #
        # Continuam recursiv.
        # -------------------------------------------------

        for child in list(node):

            walk(child)

    walk(element)

    return blocks


# =========================================================
# ELIMINARE H2
# =========================================================

def remove_h2_blocks(blocks):
    """
    H2 reprezinta de regula titlul sectiunii/conferintei.

    Nu face parte din articol.
    """

    return [
        block
        for block in blocks
        if block.get("type") != "H2"
    ]


# =========================================================
# DETECTARE TEXT MARE
# =========================================================

def text_length(text):
    """
    Lungimea reala a unui bloc de text.
    """

    return len(
        clean_text(text)
    )


def find_keywords_position(blocks):
    """
    Gaseste pozitia ultimului bloc Keywords.

    Folosim ultimul Keywords deoarece un articol
    poate avea mai multe aparitii accidentale.
    """

    position = -1

    for index, block in enumerate(blocks):

        if block.get("type") == "KEYWORDS":

            position = index

    return position


# =========================================================
# DETECTARE CONTINUT
# =========================================================

def find_content_block(blocks, keywords_position):
    """
    Gaseste blocul de continut.

    REGULA PRINCIPALA:

    Continutul este de regula cel mai mare bloc de text
    aflat inainte de Keywords.

    Nu ne intereseaza daca acel bloc este:
        P
        H4
        H5
        sau alt element.

    Conteaza continutul si pozitia.
    """

    if keywords_position <= 0:
        return -1

    candidates = []

    for index in range(
        keywords_position
    ):

        block = blocks[index]

        block_type = block.get(
            "type"
        )

        text = clean_text(
            block.get("text", "")
        )

        if not text:
            continue

        # -------------------------------------------------
        # Nu consideram titlurile
        # -------------------------------------------------

        if block_type == "H2":
            continue

        if block_type == "H4":
            continue

        if block_type == "H5":
            continue

        # -------------------------------------------------
        # Nu consideram L ca fiind continut.
        # L = afiliere
        # -------------------------------------------------

        if block_type == "L":
            continue

        # -------------------------------------------------
        # Keywords nu poate fi continut
        # -------------------------------------------------

        if block_type == "KEYWORDS":
            continue

        # -------------------------------------------------
        # Candidatul trebuie sa fie suficient de mare.
        #
        # Evitam texte foarte scurte.
        # -------------------------------------------------

        if len(text) < 80:
            continue

        candidates.append(
            (
                index,
                len(text)
            )
        )

    if not candidates:
        return -1

    # Cel mai mare bloc
    candidates.sort(
        key=lambda item: item[1],
        reverse=True
    )

    return candidates[0][0]


# =========================================================
# DETECTARE AUTORI
# =========================================================

def looks_like_author_block(text):
    """
    Detecteaza un bloc care seamana cu o lista de autori.

    Exemple:

        C. Achiroaei1,2, Diana-Ioana Panaite1,2, C. Volovăț1,2

        Ancuța-Elena Baciu1, Irina-Maria Dumitru1,2

        Eugen Brătucu, Claudiu Daha, Laurenţiu Simion

    IMPORTANT:

    Nu ne bazam pe H5.

    Putem avea autorii in H5 sau P.
    """

    if not text:
        return False

    text = clean_text(text)

    # -----------------------------------------------------
    # Nu vrem Keywords
    # -----------------------------------------------------

    if is_keywords(text):
        return False

    # -----------------------------------------------------
    # Nu vrem propozitii lungi
    # -----------------------------------------------------

    if len(text) > 700:
        return False

    # -----------------------------------------------------
    # Daca avem prea multe cuvinte,
    # probabil nu sunt autori.
    # -----------------------------------------------------

    words = text.split()

    if len(words) > 80:
        return False

    # -----------------------------------------------------
    # Separare prin virgula
    # -----------------------------------------------------

    has_comma = "," in text

    # -----------------------------------------------------
    # Numar lipit de nume:
    #
    # Achiroaei1
    # Panaite1,2
    # -----------------------------------------------------

    has_superscript_number = bool(
        re.search(
            r"[A-Za-zÀ-ÖØ-öø-ÿĂăÂâÎîȘșŞşȚțŢţ\-]\d",
            text
        )
    )

    # -----------------------------------------------------
    # Cuvinte tipice de afiliere
    # -----------------------------------------------------

    affiliation_words = [
        "institute",
        "university",
        "faculty",
        "hospital",
        "clinical",
        "center",
        "centre",
        "department",
        "laboratory",
        "bucharest",
        "romania",
        "medical",
        "oncology"
    ]

    lower = text.lower()

    if any(
        word in lower
        for word in affiliation_words
    ):
        return False

    # -----------------------------------------------------
    # Structura autorilor
    # -----------------------------------------------------

    if has_superscript_number:
        return True

    if has_comma and len(words) <= 40:
        return True

    # -----------------------------------------------------
    # Un singur autor
    #
    # Ex:
    #
    # Popescu Ion
    # -----------------------------------------------------

    if 2 <= len(words) <= 8:

        # Evitam frazele normale.
        if not re.search(
            r"[.!?]",
            text
        ):
            return True

    return False


def find_authors_block(
    blocks,
    content_position
):
    """
    Cauta autorii in zona aflata inaintea continutului.

    Autorii sunt ultimul bloc relevant inaintea afilierilor.
    """

    if content_position <= 0:
        return -1

    # Cautam de jos in sus.
    for index in range(
        content_position - 1,
        -1,
        -1
    ):

        block = blocks[index]

        block_type = block.get(
            "type"
        )

        text = clean_text(
            block.get("text", "")
        )

        if not text:
            continue

        # Nu vrem lista de afiliere
        if block_type == "L":
            continue

        if looks_like_author_block(text):

            return index

    return -1


# =========================================================
# DETECTARE AFILIERI
# =========================================================

def looks_like_affiliation(text):
    """
    Detecteaza o afiliere.

    Nu ne bazam exclusiv pe L.
    Poate fi si P / H5.
    """

    if not text:
        return False

    text = clean_text(text)

    lower = text.lower()

    affiliation_words = [
        "institute",
        "university",
        "faculty",
        "hospital",
        "clinical",
        "center",
        "centre",
        "department",
        "laboratory",
        "bucharest",
        "romania",
        "medical",
        "oncology",
        "division",
        "school",
        "clinic"
    ]

    for word in affiliation_words:

        if word in lower:
            return True

    return False


def extract_affiliation_blocks(
    blocks,
    authors_position,
    content_position
):
    """
    Extrage afilierile dintre autori si continut.

    Pot fi:
        L
        P
        H5

    si pot exista una sau mai multe.
    """

    affiliations = []

    if authors_position < 0:
        start = 0
    else:
        start = authors_position + 1

    if content_position < 0:
        end = len(blocks)
    else:
        end = content_position

    for index in range(
        start,
        end
    ):

        block = blocks[index]

        block_type = block.get(
            "type"
        )

        text = clean_text(
            block.get("text", "")
        )

        if not text:
            continue

        # -------------------------------------------------
        # Lista L = afiliere aproape sigura
        # -------------------------------------------------

        if block_type == "L":

            affiliations.append({
                "number": block.get(
                    "number",
                    ""
                ),
                "text": text
            })

            continue

        # -------------------------------------------------
        # P / H5 care seamana cu afiliere
        # -------------------------------------------------

        if looks_like_affiliation(text):

            affiliations.append({
                "number": "",
                "text": text
            })

    return affiliations


# =========================================================
# DETECTARE TITLURI
# =========================================================

def extract_titles(
    blocks,
    authors_position
):
    """
    Titlurile sunt imediat inaintea autorilor.

    Regula:

        primul titlu = title_en

        al doilea titlu = title_ro

    Nu ne bazam exclusiv pe H4.

    Cautam blocurile relevante din zona de inceput.
    """

    if not blocks:
        return []

    # -----------------------------------------------------
    # Zona de titluri
    # -----------------------------------------------------

    if authors_position >= 0:

        candidate_end = authors_position

    else:

        candidate_end = min(
            len(blocks),
            6
        )

    candidates = []

    for index in range(
        candidate_end
    ):

        block = blocks[index]

        block_type = block.get(
            "type"
        )

        text = clean_text(
            block.get("text", "")
        )

        if not text:
            continue

        # H2 nu este titlu articol
        if block_type == "H2":
            continue

        # Nu vrem keywords
        if block_type == "KEYWORDS":
            continue

        # Nu vrem afiliere
        if block_type == "L":
            continue

        if looks_like_affiliation(text):
            continue

        if looks_like_author_block(text):
            continue

        # -------------------------------------------------
        # Titlurile sunt de regula texte scurte/medii
        # -------------------------------------------------

        if len(text) > 500:
            continue

        candidates.append(
            text
        )

    # Pastram maxim doua titluri.
    return candidates[:2]


# =========================================================
# CONTINUT
# =========================================================

def extract_content(
    blocks,
    content_position,
    keywords_position
):
    """
    Extrage continutul dintre:

        afilieri

    si:

        Keywords

    Continutul poate fi un singur paragraf mare
    sau mai multe paragrafe.

    IMPORTANT:

    Nu eliminam textul doar pentru ca este P/H5/H4.
    Pozitia este mai importanta decat tagul.
    """

    if content_position < 0:
        return []

    if keywords_position < 0:
        end = len(blocks)
    else:
        end = keywords_position

    content = []

    for index in range(
        content_position,
        end
    ):

        block = blocks[index]

        text = clean_text(
            block.get("text", "")
        )

        if not text:
            continue

        block_type = block.get(
            "type"
        )

        # Nu introducem afilierea in continut
        if block_type == "L":
            continue

        content.append(text)

    return content


# =========================================================
# EXTRAGERE ARTICOL
# =========================================================

def extract_article_data(blocks):
    """
    Extrage cele 5 informatii principale:

    1. keywords
    2. continut
    3. afilieri
    4. autori
    5. titluri
    """

    # -----------------------------------------------------
    # 1. KEYWORDS
    # -----------------------------------------------------

    keywords_position = find_keywords_position(
        blocks
    )

    keywords = ""

    if keywords_position >= 0:

        keywords = clean_text(
            blocks[
                keywords_position
            ].get("text", "")
        )

    # -----------------------------------------------------
    # 2. CONTINUT
    # -----------------------------------------------------

    content_position = find_content_block(
        blocks,
        keywords_position
    )

    # -----------------------------------------------------
    # 3. AUTORI
    # -----------------------------------------------------

    authors_position = find_authors_block(
        blocks,
        content_position
    )

    authors = ""

    if authors_position >= 0:

        authors = clean_text(
            blocks[
                authors_position
            ].get("text", "")
        )

    # -----------------------------------------------------
    # 4. AFILIERI
    # -----------------------------------------------------

    affiliations = extract_affiliation_blocks(
        blocks,
        authors_position,
        content_position
    )

    # -----------------------------------------------------
    # 5. TITLURI
    # -----------------------------------------------------

    titles = extract_titles(
        blocks,
        authors_position
    )

    title_en = ""

    title_ro = ""

    if len(titles) >= 1:
        title_en = titles[0]

    if len(titles) >= 2:
        title_ro = titles[1]

    # -----------------------------------------------------
    # CONTINUT
    # -----------------------------------------------------

    content = extract_content(
        blocks,
        content_position,
        keywords_position
    )

    # -----------------------------------------------------
    # Eliminam eventualele duplicate
    # -----------------------------------------------------

    filtered_content = []

    for text in content:

        if authors and clean_text(text) == authors:
            continue

        if text == title_en:
            continue

        if text == title_ro:
            continue

        if is_keywords(text):
            continue

        filtered_content.append(text)

    content = filtered_content

    # -----------------------------------------------------
    # REZULTAT
    # -----------------------------------------------------

    return {
        "title_en": title_en,

        "title_ro": title_ro,

        "titles": titles,

        "authors": authors,

        "affiliations": affiliations,

        "paragraphs": content,

        "keywords": keywords,

        "content": content,

        "content_text": "\n\n".join(
            content
        )
    }


# =========================================================
# IDENTIFICARE ARTICOLE
# =========================================================

def split_into_articles(blocks):
    """
    Imparte documentul in articole.

    Pentru XML-urile de tip conferinta:

        H4
        H4
        H5
        ...
        Keywords

        H4
        H4
        ...

    folosim H4 ca potential inceput de articol.

    Daca doua H4 apar la inceputul aceluiasi grup,
    ele raman impreuna si reprezinta cele doua titluri.
    """

    articles = []

    current = []

    content_started = False

    for block in blocks:

        block_type = block.get(
            "type"
        )

        # -------------------------------------------------
        # H4
        # -------------------------------------------------

        if block_type == "H4":

            # Daca avem deja continut real,
            # acesta este probabil articol nou.
            if (
                current
                and content_started
            ):

                articles.append(
                    current
                )

                current = []
                content_started = False

            current.append(
                block
            )

            continue

        # -------------------------------------------------
        # Restul continutului
        # -------------------------------------------------

        if current:

            current.append(
                block
            )

            if block_type in (
                "H5",
                "P",
                "L",
                "KEYWORDS"
            ):

                content_started = True

    # -----------------------------------------------------
    # Ultimul articol
    # -----------------------------------------------------

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
    Parser principal pentru ARTICOLE SIMPLE.

    Primeste XML-ul generat din PDF.

    Nu foloseste parser.py.

    Nu foloseste builder.py.

    Extrage informatia in functie de pozitia ei,
    nu doar in functie de tagurile XML.
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
    # PART-URI
    # =====================================================

    parts = []

    for element in root.iter():

        if tag_name(element) == "Part":

            parts.append(
                element
            )

    if not parts:

        parts = [
            root
        ]

    articles = []

    # =====================================================
    # PROCESARE PART
    # =====================================================

    for part in parts:

        # -------------------------------------------------
        # H2 = titlul sectiunii/conferintei
        # -------------------------------------------------

        section_title = ""

        for child in part.iter():

            if tag_name(child) != "H2":
                continue

            text = element_text(
                child
            )

            if text:

                section_title = text

                break

        # -------------------------------------------------
        # XML -> BLOCKS
        # -------------------------------------------------

        blocks = xml_to_blocks(
            part
        )

        # H2 nu este continutul articolului
        blocks = remove_h2_blocks(
            blocks
        )

        # -------------------------------------------------
        # IMPARTIM IN ARTICOLE
        # -------------------------------------------------

        article_groups = split_into_articles(
            blocks
        )

        # -------------------------------------------------
        # PROCESAM FIECARE ARTICOL
        # -------------------------------------------------

        for article_blocks in article_groups:

            if not article_blocks:
                continue

            article_data = extract_article_data(
                article_blocks
            )

            # Pastram blocurile originale
            article_data[
                "blocks"
            ] = article_blocks

            article_data[
                "section_title"
            ] = section_title

            # -------------------------------------------------
            # Verificam daca avem un articol real
            # -------------------------------------------------

            if not (
                article_data["title_en"]
                or article_data["title_ro"]
                or article_data["authors"]
                or article_data["content"]
                or article_data["keywords"]
            ):

                continue

            articles.append(
                article_data
            )

    # =====================================================
    # COMPATIBILITATE
    # =====================================================

    first_article = (
        articles[0]
        if articles
        else {}
    )

    return {
        "type": "simple",

        # -------------------------------------------------
        # TOATE ARTICOLELE
        # -------------------------------------------------

        "articles": articles,

        # -------------------------------------------------
        # PRIMUL ARTICOL
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
        # BLOCKS
        # -------------------------------------------------

        "blocks": first_article.get(
            "blocks",
            []
        )
    }
