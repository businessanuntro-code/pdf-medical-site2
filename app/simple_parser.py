import re
import fitz  # PyMuPDF


# =========================================================
# SIMPLE PARSER
# PDF -> TEXT STRUCTURAT
#
# IMPORTANT:
# Acest parser este folosit EXCLUSIV pentru articole simple.
#
# Nu foloseste XML.
# Nu foloseste parser.py.
# Nu modifica fluxul articolelor stiintifice.
# =========================================================


# =========================================================
# FUNCTII GENERALE
# =========================================================

def clean_text(text):
    """
    Curata si normalizeaza textul extras din PDF.
    """

    if not text:
        return ""

    text = text.replace("\xa0", " ")
    text = text.replace("\u200b", "")
    text = text.replace("\ufeff", "")

    # Normalizeaza spatiile
    text = re.sub(r"[ \t]+", " ", text)

    # Elimina spatiile inutile de la inceput si sfarsit
    text = text.strip()

    return text


def is_keywords(text):
    """
    Detecteaza blocurile care contin Keywords / Cuvinte cheie.
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


def extract_keywords(text):
    """
    Extrage textul de dupa:

        Keywords:

    sau:

        Cuvinte cheie:
    """

    if not text:
        return ""

    match = re.match(
        r"^\s*(?:Keywords|Cuvinte\s+cheie)\s*:\s*(.*)$",
        text,
        flags=re.IGNORECASE
    )

    if match:
        return clean_text(match.group(1))

    return clean_text(text)


# =========================================================
# EXTRAGERE TEXT DIN PDF
# =========================================================

def extract_pdf_blocks(pdf_path):
    """
    Extrage textul din PDF pastrand ordinea blocurilor.

    Fiecare bloc contine:

        {
            "page": numarul paginii,
            "text": textul blocului
        }

    Nu incercam aici sa decidem daca textul este:
        - titlu
        - autor
        - afiliere
        - continut
        - keywords

    Aceasta decizie va fi facuta ulterior.
    """

    blocks = []

    try:
        document = fitz.open(pdf_path)

    except Exception as exc:
        raise ValueError(
            f"PDF-ul nu poate fi deschis: {exc}"
        ) from exc

    try:

        for page_number, page in enumerate(
            document,
            start=1
        ):

            # Extragem blocurile de text
            page_blocks = page.get_text(
                "blocks"
            )

            # -------------------------------------------------
            # Sortare dupa pozitia din pagina
            #
            # y = pozitia verticala
            # x = pozitia orizontala
            # -------------------------------------------------

            page_blocks = sorted(
                page_blocks,
                key=lambda block: (
                    block[1],
                    block[0]
                )
            )

            for block in page_blocks:

                # Structura PyMuPDF:
                #
                # x0
                # y0
                # x1
                # y1
                # text
                # ...

                if len(block) < 5:
                    continue

                text = block[4]

                if not text:
                    continue

                text = clean_text(text)

                if not text:
                    continue

                blocks.append({
                    "page": page_number,
                    "text": text
                })

    finally:

        document.close()

    return blocks


# =========================================================
# COMBINARE LINII / BLOCURI
# =========================================================

def normalize_blocks(blocks):
    """
    Normalizeaza blocurile extrase din PDF.

    Unele PDF-uri pot sparge un paragraf in mai multe blocuri.
    Pentru moment pastram blocurile separat, deoarece acest lucru
    ne permite sa reconstruim mai fidel ordinea originala.
    """

    result = []

    for block in blocks:

        text = clean_text(
            block.get("text", "")
        )

        if not text:
            continue

        result.append({
            "page": block.get("page", 0),
            "text": text
        })

    return result


# =========================================================
# DETECTARE TITLURI
# =========================================================

def detect_titles(blocks):
    """
    Pentru moment NU presupune ca PDF-ul are H4/H5.

    Primele doua blocuri de continut relevante sunt pastrate
    ca posibile titluri.

    Identificarea poate fi imbunatatita ulterior folosind:
        - marimea fontului
        - pozitia
        - bold
        - stilul fontului
    """

    titles = []

    for block in blocks:

        text = block["text"]

        if not text:
            continue

        if is_keywords(text):
            break

        titles.append(text)

        if len(titles) >= 2:
            break

    return titles


# =========================================================
# DETECTARE KEYWORDS
# =========================================================

def detect_keywords(blocks):
    """
    Cauta Keywords / Cuvinte cheie oriunde in document.
    """

    keywords = ""

    for block in blocks:

        text = block["text"]

        if is_keywords(text):

            keywords = extract_keywords(text)

            break

    return keywords


# =========================================================
# DETECTARE CONTINUT
# =========================================================

def detect_content(blocks, keywords):
    """
    Extrage continutul dintre zona initiala a articolului
    si Keywords.

    IMPORTANT:

    In aceasta versiune pastram textul brut cat mai fidel.
    Nu eliminam continut pe baza tagurilor PDF.
    """

    if not blocks:
        return []

    content = []

    keywords_found = False

    for block in blocks:

        text = block["text"]

        if not text:
            continue

        # Keywords marcheaza sfarsitul articolului
        if is_keywords(text):

            keywords_found = True
            break

        # Daca am ajuns la keywords nu mai continuam
        if keywords_found:
            break

        content.append(text)

    return content


# =========================================================
# ELIMINARE TITLURI DIN CONTINUT
# =========================================================

def remove_titles_from_content(
    content,
    titles
):
    """
    Elimina din continut primele titluri detectate.

    Restul textului ramane neschimbat.
    """

    if not content:
        return []

    if not titles:
        return content

    result = list(content)

    for title in titles:

        if not result:
            break

        if clean_text(result[0]) == clean_text(title):

            result.pop(0)

    return result


# =========================================================
# IDENTIFICARE AUTORI
# =========================================================

def looks_like_authors(text):
    """
    Detecteaza aproximativ un bloc de autori.

    Exemple:

        C. Achiroaei1,2, Diana-Ioana Panaite1,2

        Ancuța-Elena Baciu1, Irina-Maria Dumitru1,2

    Nu este o regula definitiva.
    Este folosita doar pentru prima versiune a parserului.
    """

    if not text:
        return False

    text = clean_text(text)

    # Trebuie sa existe cel putin o virgula
    # sau un numar atasat unui nume.

    has_comma = "," in text

    has_author_number = bool(
        re.search(
            r"[A-Za-zÀ-ÖØ-öø-ÿĂăÂâÎîȘșŞşȚțŢţ\-]\d",
            text
        )
    )

    # Evitam identificarea unor propozitii normale
    has_sentence = bool(
        re.search(
            r"\.\s+[A-Z]",
            text
        )
    )

    if has_author_number:
        return True

    if has_comma and not has_sentence:
        return True

    return False


def extract_authors(blocks, titles):
    """
    Cauta blocul de autori imediat dupa titluri.

    Pentru moment cauta primele blocuri candidate.
    """

    if not blocks:
        return ""

    start_index = 0

    # Sarim peste titlurile detectate
    for title in titles:

        for index in range(
            start_index,
            len(blocks)
        ):

            if clean_text(
                blocks[index]["text"]
            ) == clean_text(title):

                start_index = index + 1
                break

    for index in range(
        start_index,
        min(
            start_index + 5,
            len(blocks)
        )
    ):

        text = blocks[index]["text"]

        if looks_like_authors(text):
            return text

    return ""


# =========================================================
# IDENTIFICARE AFILIERI
# =========================================================

def looks_like_affiliation(text):
    """
    Detecteaza aproximativ o afiliere.

    Nu depindem de XML.

    Exemple:

        Institute of Oncology, Bucharest, Romania

        Faculty of Physics, University of Bucharest

    """

    if not text:
        return False

    text_lower = clean_text(text).lower()

    keywords = [
        "institute",
        "university",
        "faculty",
        "hospital",
        "clinical",
        "center",
        "centre",
        "department",
        "laboratory",
        "medical",
        "bucharest",
        "romania"
    ]

    for word in keywords:

        if word in text_lower:
            return True

    return False


def extract_affiliations(
    blocks,
    authors,
    titles
):
    """
    Extrage blocurile de afiliere aflate dupa autori.

    Afilierile sunt pastrate ca lista de texte.
    """

    if not blocks:
        return []

    start_index = 0

    # -----------------------------------------------------
    # Gasim autorii
    # -----------------------------------------------------

    if authors:

        for index, block in enumerate(blocks):

            if clean_text(
                block["text"]
            ) == clean_text(authors):

                start_index = index + 1
                break

    # -----------------------------------------------------
    # Colectam afilierile
    # -----------------------------------------------------

    affiliations = []

    for index in range(
        start_index,
        len(blocks)
    ):

        text = blocks[index]["text"]

        if not text:
            continue

        # Keywords = sfarsitul zonei de afiliere
        if is_keywords(text):
            break

        # Daca incepe continutul propriu-zis,
        # nu mai cautam afilieri.
        if re.match(
            r"^(Introduction|Objective|Materials|Material|Results|Conclusions|Background)\.",
            text,
            flags=re.IGNORECASE
        ):
            break

        if looks_like_affiliation(text):

            affiliations.append(text)

        else:

            # Prima fraza care nu pare afiliere
            # indica probabil inceputul continutului.
            if affiliations:
                break

    return affiliations


# =========================================================
# PARSARE UN ARTICOL
# =========================================================

def parse_simple_pdf(pdf_path):
    """
    Parseaza un PDF pentru articole simple.

    Returneaza un dictionar compatibil cu simple_builder.py.
    """

    blocks = extract_pdf_blocks(
        pdf_path
    )

    blocks = normalize_blocks(
        blocks
    )

    if not blocks:

        return {
            "type": "simple",
            "articles": [],
            "title_en": "",
            "title_ro": "",
            "authors": "",
            "affiliations": [],
            "keywords": "",
            "content": [],
            "content_text": "",
            "blocks": []
        }

    # -----------------------------------------------------
    # TITLURI
    # -----------------------------------------------------

    titles = detect_titles(
        blocks
    )

    title_en = (
        titles[0]
        if len(titles) >= 1
        else ""
    )

    title_ro = (
        titles[1]
        if len(titles) >= 2
        else ""
    )

    # -----------------------------------------------------
    # AUTORI
    # -----------------------------------------------------

    authors = extract_authors(
        blocks,
        titles
    )

    # -----------------------------------------------------
    # AFILIERI
    # -----------------------------------------------------

    affiliations = extract_affiliations(
        blocks,
        authors,
        titles
    )

    # -----------------------------------------------------
    # KEYWORDS
    # -----------------------------------------------------

    keywords = detect_keywords(
        blocks
    )

    # -----------------------------------------------------
    # CONTINUT
    # -----------------------------------------------------

    content = detect_content(
        blocks,
        keywords
    )

    # Eliminam titlurile
    content = remove_titles_from_content(
        content,
        titles
    )

    # Eliminam autorii
    if authors and content:

        for index, text in enumerate(content):

            if clean_text(text) == clean_text(authors):

                content.pop(index)
                break

    # Eliminam afilierile
    for affiliation in affiliations:

        for index, text in enumerate(content):

            if clean_text(text) == clean_text(
                affiliation
            ):

                content.pop(index)
                break

    # -----------------------------------------------------
    # ELIMINAM eventualul Keywords din continut
    # -----------------------------------------------------

    content = [
        text
        for text in content
        if not is_keywords(text)
    ]

    # -----------------------------------------------------
    # ARTICOL
    # -----------------------------------------------------

    article = {
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

    # -----------------------------------------------------
    # REZULTAT FINAL
    # -----------------------------------------------------

    return {
        "type": "simple",

        "articles": [
            article
        ],

        "title_en": title_en,
        "title_ro": title_ro,

        "authors": authors,

        "affiliations": affiliations,

        "keywords": keywords,

        "content": content,

        "content_text": "\n\n".join(
            content
        ),

        # Pastram si blocurile originale.
        # Sunt foarte utile pentru calibrare ulterioara.
        "blocks": blocks
    }


# =========================================================
# FUNCTIE PRINCIPALA
# =========================================================

def parse_simple_xml(pdf_path):
    """
    MENTINEM NUMELE FUNCTIEI EXISTENTE pentru compatibilitate
    cu simple_main.py.

    IMPORTANT:

    Desi functia se numeste parse_simple_xml(),
    acum NU mai citeste XML.

    Primeste DIRECT un PDF.
    """

    return parse_simple_pdf(
        pdf_path
    )
