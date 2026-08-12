import re
import xml.etree.ElementTree as ET


# =========================================================
# SIMPLE PARSER
# =========================================================
#
# Parser exclusiv pentru ARTICOLE SIMPLE.
#
# NU modifica parser.py pentru articolele stiintifice.
#
# Obiectiv:
#
# 1. TITLU EN
# 2. TITLU RO
# 3. AUTORI
# 4. AFILIERI
# 5. CONTINUT
# 6. KEYWORDS
#
# Parserul NU se bazeaza rigid pe H1/H2/H3/H4/H5.
# Tag-urile XML sunt folosite doar ca indicii.
#
# Identificarea se face in principal dupa:
# - pozitia informatiei
# - continutul textului
# - tipul blocului
# =========================================================


# =========================================================
# FUNCTII GENERALE
# =========================================================

def clean_text(text):
    """
    Curata si normalizeaza textul.
    """

    if not text:
        return ""

    text = text.replace("\xa0", " ")
    text = text.replace("\u200b", "")
    text = text.replace("\ufeff", "")

    # Normalizeaza whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def element_text(element):
    """
    Returneaza tot textul continut de un element,
    inclusiv textul elementelor copil.
    """

    if element is None:
        return ""

    text = "".join(element.itertext())

    return clean_text(text)


def get_tag(element):
    """
    Returneaza numele tag-ului fara namespace.
    """

    if element is None:
        return ""

    return element.tag.split("}")[-1]


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

    text = clean_text(text)

    return bool(
        re.match(
            r"^(?:keywords|cuvinte\s+cheie)\s*:",
            text,
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
# DETECTARE AUTORI
# =========================================================

def has_author_superscript(text):
    """
    Verifica daca textul contine numere asociate autorilor.

    Exemple:

    Ancuța-Elena Baciu1
    Irina-Maria Dumitru1,2
    C. Achiroaei1,2
    """

    if not text:
        return False

    return bool(
        re.search(
            r"[A-Za-zÀ-ÖØ-öø-ÿĂăÂâÎîȘșŞşȚțŢţ\)])"
            r"\s*\d+(?:\s*,\s*\d+)*\s*(?=,|$)",
            text
        )
    )


def looks_like_person_name(text):
    """
    Verifica aproximativ daca textul seamana cu o lista de autori.

    Nu incercam sa identificam perfect numele.
    Scopul este sa distingem autorii de afiliere si continut.
    """

    if not text:
        return False

    text = clean_text(text)

    if len(text) > 500:
        return False

    # Nu este afiliere daca are expresii foarte specifice.
    institutional_words = [
        "university",
        "universit",
        "institute",
        "institut",
        "hospital",
        "spital",
        "clinic",
        "clinical",
        "department",
        "departament",
        "center",
        "centre",
        "laboratory",
        "laborator",
        "bucharest",
        "bucurești",
        "romania",
        "faculty",
        "facultatea",
        "medical center",
        "medical centre",
        "association",
        "asociația",
        "division",
        "nuclearelectrica"
    ]

    lowered = text.lower()

    for word in institutional_words:
        if word in lowered:
            return False

    # Autorii sunt de regula separati prin virgule.
    if "," in text:
        parts = [
            clean_text(part)
            for part in text.split(",")
            if clean_text(part)
        ]

        if len(parts) >= 2:
            valid_parts = 0

            for part in parts:

                # eliminam eventualele superscripturi
                name = re.sub(
                    r"\d+(?:\s*,\s*\d+)*$",
                    "",
                    part
                ).strip()

                words = name.split()

                if len(words) >= 2:
                    valid_parts += 1

            if valid_parts >= 2:
                return True

    # Caz cu un singur autor.
    words = text.split()

    if 2 <= len(words) <= 8:

        # Evitam propozitii.
        if not re.search(r"[.!?]", text):
            return True

    return False


# =========================================================
# AFILIERI
# =========================================================

def looks_like_affiliation(text):
    """
    Detecteaza o afiliere pe baza continutului.

    Exemple:

    1. Institute of Oncology, Bucharest, Romania
    Faculty of Physics, University of Bucharest, Romania
    Neolife Medical Center, Bucharest, Romania
    """

    if not text:
        return False

    text = clean_text(text)

    if not text:
        return False

    lowered = text.lower()

    affiliation_words = [
        "university",
        "universit",
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
        "laboratory",
        "laborator",
        "association",
        "asociația",
        "division",
        "bucharest",
        "bucurești",
        "romania",
        "nuclearelectrica",
        "medical",
        "oncology",
        "oncologie"
    ]

    for word in affiliation_words:
        if word in lowered:
            return True

    # Afilierea poate incepe cu:
    # 1.
    # 2.
    # 3.
    if re.match(r"^\d+\.", text):
        return True

    return False


def clean_affiliation_number(text):
    """
    Elimina numarul de afiliere de la inceput.
    """

    if not text:
        return ""

    text = clean_text(text)

    text = re.sub(
        r"^\d+\.\s*",
        "",
        text
    )

    return clean_text(text)


# =========================================================
# EXTRAGERE AFILIERI
# =========================================================

def extract_affiliations_from_element(element):
    """
    Extrage afilierea din Footnote, H4, H5, LBody etc.
    """

    affiliations = []

    tag = get_tag(element)

    text = element_text(element)

    if not text:
        return affiliations

    # -----------------------------------------------------
    # Footnote
    # -----------------------------------------------------

    if tag == "Footnote":

        text = clean_affiliation_number(text)

        if text:
            affiliations.append(text)

        return affiliations

    # -----------------------------------------------------
    # LBody
    # -----------------------------------------------------

    if tag == "LBody":

        text = clean_affiliation_number(text)

        if text:
            affiliations.append(text)

        return affiliations

    # -----------------------------------------------------
    # Alte elemente
    # -----------------------------------------------------

    if looks_like_affiliation(text):

        text = clean_affiliation_number(text)

        if text:
            affiliations.append(text)

    return affiliations


# =========================================================
# TITLURI
# =========================================================

def split_combined_title(text):
    """
    In unele XML-uri cele doua titluri sunt in acelasi element.

    Exemplu:

    Risk of pancreatic fistula after pancreatoduodenectomy –
    a point of view Riscul de fistulă pancreatică după
    pancreatoduodenectomie – un punct de vedere

    Nu exista un separator XML clar.

    Functia incearca sa identifice partea romana.

    Daca nu poate separa sigur, returneaza textul integral
    ca primul titlu.
    """

    if not text:
        return "", ""

    text = clean_text(text)

    # -----------------------------------------------------
    # Incercam sa gasim inceputul partii romanesti.
    # -----------------------------------------------------

    romanian_markers = [
        " Riscul ",
        " Riscurile ",
        " Tratamentul ",
        " Tratamentul ",
        " Evaluarea ",
        " Identificarea ",
        " Standarde ",
        " Dinamica ",
        " Genotipul ",
        " Trasabilitatea ",
        " Trasabilitatea ",
        " Cancerul ",
        " Cancerului ",
        " Utilizarea ",
        " Analiza ",
        " Rezultatele ",
        " Caracteristicile ",
        " Rolul ",
        " Importanța ",
        " Importanta ",
        " Managementul ",
        " Diagnosticul ",
        " Experiența ",
        " Experienta ",
        " Studiul ",
        " Eficiența ",
        " Eficienta ",
        " Perspective "
    ]

    positions = []

    lowered = text.lower()

    for marker in romanian_markers:

        pos = lowered.find(marker.lower())

        if pos > 0:
            positions.append(pos)

    if positions:

        pos = min(positions)

        english = clean_text(text[:pos])
        romanian = clean_text(text[pos:])

        if english and romanian:
            return english, romanian

    return text, ""


def extract_titles_from_block(elements):
    """
    Extrage maximum doua titluri din inceputul articolului.

    Poate procesa:

    H1 + H2
    H2
    H4 + H4
    H2 care contine EN + RO
    """

    title_candidates = []

    for element in elements:

        tag = get_tag(element)

        if tag not in {
            "H1",
            "H2",
            "H4"
        }:
            continue

        text = element_text(element)

        if not text:
            continue

        # Keywords nu este titlu.
        if is_keywords_text(text):
            continue

        title_candidates.append(
            (tag, text)
        )

    if not title_candidates:
        return "", "", []

    # -----------------------------------------------------
    # Primul candidat
    # -----------------------------------------------------

    first_tag, first_text = title_candidates[0]

    title_en = first_text
    title_ro = ""

    # -----------------------------------------------------
    # Daca primul contine doua titluri.
    # -----------------------------------------------------

    combined_en, combined_ro = split_combined_title(
        first_text
    )

    if combined_ro:

        title_en = combined_en
        title_ro = combined_ro

    # -----------------------------------------------------
    # Al doilea candidat
    # -----------------------------------------------------

    if not title_ro and len(title_candidates) >= 2:

        second_tag, second_text = title_candidates[1]

        # Daca al doilea este un titlu separat.
        title_ro = second_text

    return (
        clean_text(title_en),
        clean_text(title_ro),
        title_candidates
    )


# =========================================================
# IDENTIFICAREA ARTICOLULUI
# =========================================================

def find_article_sections(root):
    """
    Identifica blocurile care reprezinta articole.

    In XML-ul AutoTag observat, articolele sunt grupate
    in Sect-uri.

    Incercam sa gasim Sect-ul care contine:
    - un titlu
    - autori
    - continut

    IMPORTANT:
    Nu luam toate Sect-urile imbricate.
    """

    articles = []

    def recursive_search(element):

        if get_tag(element) == "Sect":

            direct_children = list(element)

            tags = [
                get_tag(child)
                for child in direct_children
            ]

            has_title = any(
                tag in {"H1", "H2", "H4"}
                for tag in tags
            )

            if has_title:

                # Verificam daca exista un bloc de text
                # sau autori in interior.
                texts = []

                for child in direct_children:

                    text = element_text(child)

                    if text:
                        texts.append(text)

                joined = " ".join(texts)

                has_content = (
                    len(joined) > 100
                    or looks_like_person_name(joined)
                )

                if has_content:

                    articles.append(element)

                    # Nu mai coboram in Sect-urile copil.
                    return

        for child in list(element):
            recursive_search(child)

    recursive_search(root)

    return articles


# =========================================================
# EXTRAGERE BLOCURI ARTICOL
# =========================================================

def get_article_elements(section):
    """
    Obtine elementele relevante dintr-un articol.

    Se pastreaza ordinea originala din XML.
    """

    elements = []

    for element in section.iter():

        if element is section:
            continue

        tag = get_tag(element)

        if tag in {
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
        }:

            elements.append(element)

    return elements


# =========================================================
# EXTRAGERE AUTORI
# =========================================================

def extract_authors(elements, title_candidates):
    """
    Cauta autorii in blocul de dupa titlu.

    Prioritate:

    1. H3 / H5
    2. P
    3. alte texte scurte care seamana cu o lista de nume
    """

    title_elements = {
        id(element)
        for element in []
    }

    # -----------------------------------------------------
    # Determinam pozitia primului titlu.
    # -----------------------------------------------------

    title_positions = []

    for index, element in enumerate(elements):

        tag = get_tag(element)

        text = element_text(element)

        if tag in {"H1", "H2", "H4"} and text:

            if not is_keywords_text(text):

                title_positions.append(index)

    start_position = 0

    if title_positions:
        start_position = max(title_positions[:2]) + 1

    # -----------------------------------------------------
    # Cautam in primele elemente dupa titlu.
    # -----------------------------------------------------

    candidates = []

    for index in range(
        start_position,
        min(len(elements), start_position + 12)
    ):

        element = elements[index]

        tag = get_tag(element)
        text = element_text(element)

        if not text:
            continue

        if is_keywords_text(text):
            break

        if looks_like_affiliation(text):
            break

        if len(text) > 500:
            break

        # H3/H5 sunt foarte probabile.
        if tag in {"H3", "H5"}:

            candidates.append(text)

            continue

        if tag == "P" and looks_like_person_name(text):

            candidates.append(text)

    if not candidates:
        return ""

    # Primul candidat relevant.
    authors = candidates[0]

    return clean_text(authors)


# =========================================================
# EXTRAGERE AFILIERI
# =========================================================

def extract_affiliations(elements):
    """
    Extrage toate afilierile dintre autori si continut.

    Sunt acceptate:

    Footnote
    LBody
    H4
    H5
    P

    doar daca textul seamana cu o afiliere.
    """

    affiliations = []

    started = False

    for element in elements:

        tag = get_tag(element)

        text = element_text(element)

        if not text:
            continue

        # -------------------------------------------------
        # Keywords = stop
        # -------------------------------------------------

        if is_keywords_text(text):
            break

        # -------------------------------------------------
        # Detectam autorii
        # -------------------------------------------------

        if not started:

            if (
                tag in {"H3", "H5"}
                and looks_like_person_name(text)
            ):
                started = True
                continue

            if tag == "P" and looks_like_person_name(text):
                started = True
                continue

            continue

        # -------------------------------------------------
        # Continutul lung = am iesit din zona afilierilor
        # -------------------------------------------------

        if len(text) > 500:
            break

        # -------------------------------------------------
        # Liste XML
        # -------------------------------------------------

        if tag in {
            "Footnote",
            "LBody"
        }:

            if looks_like_affiliation(text):

                affiliation = clean_affiliation_number(
                    text
                )

                if affiliation:
                    affiliations.append(
                        affiliation
                    )

                continue

        # -------------------------------------------------
        # H4/H5
        # -------------------------------------------------

        if tag in {"H4", "H5"}:

            if looks_like_affiliation(text):

                affiliation = clean_affiliation_number(
                    text
                )

                if affiliation:
                    affiliations.append(
                        affiliation
                    )

                continue

        # -------------------------------------------------
        # P
        # -------------------------------------------------

        if tag == "P":

            if looks_like_affiliation(text):

                affiliation = clean_affiliation_number(
                    text
                )

                if affiliation:
                    affiliations.append(
                        affiliation
                    )

                continue

            # Daca nu mai este afiliere, continuam
            # pentru a permite continutul sa fie identificat.
            if len(text) > 100:
                break

    return affiliations


# =========================================================
# EXTRAGERE CONTINUT
# =========================================================

def extract_content(elements, authors, affiliations):
    """
    Extrage continutul articolului.

    Continutul este textul aflat:
    - dupa titlu
    - dupa autori
    - dupa afilieri
    - inainte de Keywords.

    Nu pierdem paragrafele individuale.
    """

    paragraphs = []

    keywords_found = False

    # -----------------------------------------------------
    # Tinem evidenta daca am trecut de autori/afiliere.
    # -----------------------------------------------------

    content_started = False

    for element in elements:

        tag = get_tag(element)

        text = element_text(element)

        if not text:
            continue

        # -------------------------------------------------
        # Keywords
        # -------------------------------------------------

        if is_keywords_text(text):

            keywords_found = True

            break

        # -------------------------------------------------
        # Ignoram titlurile
        # -------------------------------------------------

        if tag in {"H1", "H2", "H3", "H4", "H5"}:

            if text == authors:
                continue

            # Afiliere
            if any(
                clean_text(text) == clean_text(aff)
                or clean_text(text).endswith(
                    clean_text(aff)
                )
                for aff in affiliations
            ):
                continue

            continue

        # -------------------------------------------------
        # Ignoram Footnote / L / LI / Lbl / LBody
        # -----------------------------------------------------

        if tag in {
            "Footnote",
            "L",
            "LI",
            "Lbl",
            "LBody"
        }:
            continue

        # -------------------------------------------------
        # Continutul este in principal P.
        # -------------------------------------------------

        if tag == "P":

            # Autor
            if clean_text(text) == clean_text(authors):
                continue

            # Afiliere
            is_affiliation = False

            for affiliation in affiliations:

                if clean_text(text) == clean_text(
                    affiliation
                ):
                    is_affiliation = True
                    break

            if is_affiliation:
                continue

            # Keywords
            if is_keywords_text(text):
                break

            paragraphs.append(
                clean_text(text)
            )

            content_started = True

    # -----------------------------------------------------
    # Eliminam duplicatele consecutive.
    # -----------------------------------------------------

    cleaned = []

    for paragraph in paragraphs:

        if not paragraph:
            continue

        if cleaned and paragraph == cleaned[-1]:
            continue

        cleaned.append(paragraph)

    return cleaned


# =========================================================
# EXTRAGERE KEYWORDS
# =========================================================

def extract_keywords_from_elements(elements):
    """
    Cauta Keywords oriunde in blocul articolului.

    Poate fi:

    <P>Keywords: ...</P>

    sau

    <H5>Keywords: ...</H5>

    sau alt element text.
    """

    for element in elements:

        text = element_text(element)

        if not text:
            continue

        if is_keywords_text(text):

            return extract_keywords(text)

    return ""


# =========================================================
# PARSARE UN ARTICOL
# =========================================================

def parse_article_section(section):
    """
    Proceseaza un singur articol simplu.
    """

    elements = get_article_elements(section)

    # -----------------------------------------------------
    # TITLURI
    # -----------------------------------------------------

    title_en, title_ro, title_candidates = (
        extract_titles_from_block(elements)
    )

    # -----------------------------------------------------
    # AUTORI
    # -----------------------------------------------------

    authors = extract_authors(
        elements,
        title_candidates
    )

    # -----------------------------------------------------
    # AFILIERI
    # -----------------------------------------------------

    affiliations = extract_affiliations(
        elements
    )

    # -----------------------------------------------------
    # KEYWORDS
    # -----------------------------------------------------

    keywords = extract_keywords_from_elements(
        elements
    )

    # -----------------------------------------------------
    # CONTINUT
    # -----------------------------------------------------

    paragraphs = extract_content(
        elements,
        authors,
        affiliations
    )

    # -----------------------------------------------------
    # Eliminam eventualele texte care sunt Keywords.
    # -----------------------------------------------------

    paragraphs = [
        paragraph
        for paragraph in paragraphs
        if not is_keywords_text(paragraph)
    ]

    # -----------------------------------------------------
    # Rezultat
    # -----------------------------------------------------

    return {
        "title_en": title_en,
        "title_ro": title_ro,
        "titles": [
            title
            for title in [title_en, title_ro]
            if title
        ],

        "authors": authors,

        "affiliations": [
            {
                "number": str(index),
                "text": affiliation
            }
            for index, affiliation
            in enumerate(affiliations, start=1)
        ],

        "paragraphs": paragraphs,

        "keywords": keywords,

        "content": paragraphs,

        "content_text": "\n\n".join(
            paragraphs
        )
    }


# =========================================================
# PARSER PRINCIPAL
# =========================================================

def parse_simple_xml(xml_path):
    """
    Parser principal pentru ARTICOLE SIMPLE.

    Flux:

    XML
      ↓
    detectare articole
      ↓
    titluri
      ↓
    autori
      ↓
    afilieri
      ↓
    continut
      ↓
    keywords

    Este complet separat de parser.py.
    """

    try:

        tree = ET.parse(xml_path)
        root = tree.getroot()

    except ET.ParseError as exc:

        raise ValueError(
            f"XML invalid sau imposibil de procesat: {exc}"
        ) from exc

    # -----------------------------------------------------
    # Detectam articolele
    # -----------------------------------------------------

    article_sections = find_article_sections(
        root
    )

    articles = []

    # -----------------------------------------------------
    # Procesam fiecare articol
    # -----------------------------------------------------

    for section in article_sections:

        article = parse_article_section(
            section
        )

        # -------------------------------------------------
        # Nu pastram blocuri fara continut real.
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

    # -----------------------------------------------------
    # Compatibilitate cu builderul existent.
    #
    # Primul articol este pastrat si la nivel superior.
    # -----------------------------------------------------

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
        )
    }
