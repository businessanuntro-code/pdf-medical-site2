import re
import xml.etree.ElementTree as ET


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
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def get_tag(element):
    """
    Returneaza numele simplu al tagului XML.
    """

    if element is None:
        return ""

    return element.tag.split("}")[-1]


def element_text(element):
    """
    Extrage tot textul continut de element,
    inclusiv textul elementelor copil.
    """

    if element is None:
        return ""

    return clean_text(
        "".join(element.itertext())
    )


# =========================================================
# IDENTIFICARE KEYWORDS
# =========================================================

def is_keywords(text):
    """
    Identifica un bloc Keywords indiferent de tagul XML.

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
    Extrage doar continutul de dupa:

    Keywords:
    Cuvinte cheie:
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

    return ""


# =========================================================
# IDENTIFICARE AUTORI
# =========================================================

def looks_like_author_block(text):
    """
    Verifica daca un bloc pare sa contina autori.

    Exemple acceptate:

    C. Achiroaei1,2, Diana-Ioana Panaite1,2, C. Volovăț1,2

    Ancuța-Elena Baciu1, Irina-Maria Dumitru1,2

    Eugen Brătucu, Claudiu Daha, Laurenţiu Simion
    """

    if not text:
        return False

    text = clean_text(text)

    # Prea lung pentru a fi in mod normal o lista de autori.
    if len(text) > 600:
        return False

    # Nu trebuie sa fie Keywords.
    if is_keywords(text):
        return False

    # Daca exista prea multe propozitii, probabil este continut.
    if len(re.findall(r"[.!?]", text)) > 3:
        return False

    # Prezenta virgulelor este un indicator puternic.
    has_commas = "," in text

    # Nume cu cifra de afiliere:
    # Achiroaei1,2
    has_author_numbers = bool(
        re.search(
            r"[A-Za-zÀ-ÖØ-öø-ÿĂăÂâÎîȘșŞşȚțŢţ\-]"
            r"\d+(?:\s*,\s*\d+)*",
            text
        )
    )

    # Verificam prezenta unor structuri de nume.
    words = text.split()

    # Un bloc de autori are de obicei mai multe cuvinte.
    enough_words = len(words) >= 2

    if has_author_numbers:
        return True

    if has_commas and enough_words:
        return True

    return False


def extract_authors_from_text(text):
    """
    Curata si returneaza textul autorilor.

    Formatarea bold/superscript este facuta
    ulterior in simple_builder.py.
    """

    if not text:
        return ""

    return clean_text(text)


# =========================================================
# IDENTIFICARE AFILIERI
# =========================================================

def looks_like_affiliation(text):
    """
    Verifica daca un bloc pare sa fie o afiliere.

    Exemple:

    Institute of Oncology, Bucharest, Romania

    Faculty of Physics, University of Bucharest, Romania

    Fundeni Clinical Institute, Bucharest, Romania
    """

    if not text:
        return False

    text = clean_text(text)

    if len(text) < 5:
        return False

    if is_keywords(text):
        return False

    # Indicatori frecventi pentru institutii.
    affiliation_words = [
        "university",
        "universitatea",
        "institute",
        "institut",
        "faculty",
        "facultatea",
        "hospital",
        "spital",
        "clinical",
        "clinic",
        "center",
        "centre",
        "medical",
        "laboratory",
        "laborator",
        "academy",
        "academia",
        "department",
        "departament",
        "college",
        "association",
        "asocia",
        "bucharest",
        "bucuresti",
        "romania",
    ]

    lower = text.lower()

    score = 0

    for word in affiliation_words:
        if word in lower:
            score += 1

    # Prezenta unei tari/oras este un indicator foarte bun.
    if re.search(
        r"\b(romania|bucharest|bucuresti)\b",
        lower
    ):
        score += 2

    return score >= 1


# =========================================================
# EXTRAGERE AFILIERI
# =========================================================

def extract_affiliations_from_list(element):
    """
    Extrage afilierile din structuri de tip:

    <L>
        <LI>
            <Lbl>1.</Lbl>
            <LBody>...</LBody>
        </LI>
    </L>
    """

    affiliations = []

    for child in element.iter():

        if get_tag(child) != "L":
            continue

        for li in list(child):

            if get_tag(li) != "LI":
                continue

            number = ""
            body = ""

            for item in list(li):

                tag = get_tag(item)

                if tag == "Lbl":
                    number = element_text(item)

                elif tag == "LBody":
                    body = element_text(item)

            body = clean_text(body)

            if body:
                number = re.sub(
                    r"[^\d]",
                    "",
                    number
                )

                affiliations.append(
                    {
                        "number": number,
                        "text": body
                    }
                )

    return affiliations


# =========================================================
# TITLURI
# =========================================================

def extract_titles(section):
    """
    Primul H4 = title_en
    Al doilea H4 = title_ro

    Nu folosim continutul H4 ca altceva.
    """

    titles = []

    for element in section.iter():

        if get_tag(element) != "H4":
            continue

        text = element_text(element)

        if not text:
            continue

        # Keywords nu poate fi titlu.
        if is_keywords(text):
            continue

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
# GASIRE BLOCURI REALE ALE ARTICOLULUI
# =========================================================

def get_content_elements(section):
    """
    Returneaza elementele textuale importante din articol.

    Nu ne bazam exclusiv pe P/H5/H4.
    """

    elements = []

    for element in section.iter():

        tag = get_tag(element)

        if tag not in (
            "H2",
            "H4",
            "H5",
            "P",
            "L",
            "LI",
            "LBody",
            "Lbl"
        ):
            continue

        text = element_text(element)

        if not text:
            continue

        elements.append(
            {
                "element": element,
                "tag": tag,
                "text": text
            }
        )

    return elements


# =========================================================
# DETECTARE AUTORI
# =========================================================

def find_authors(section, title_elements):
    """
    Cauta autorii dupa cele doua titluri.

    Ordinea de cautare:

    1. H5
    2. P
    3. alte blocuri textuale scurte

    Ne oprim la prima potrivire.
    """

    elements = get_content_elements(section)

    title_indexes = []

    for index, item in enumerate(elements):

        if item["tag"] == "H4":
            title_indexes.append(index)

    start_index = 0

    if title_indexes:
        start_index = title_indexes[-1] + 1

    candidates = []

    for item in elements[start_index:]:

        tag = item["tag"]
        text = item["text"]

        if is_keywords(text):
            break

        if tag == "L":
            continue

        if tag == "LBody":
            continue

        if tag == "Lbl":
            continue

        if tag == "LI":
            continue

        candidates.append(item)

        # H5 este cel mai puternic indicator.
        if tag == "H5" and looks_like_author_block(text):
            return extract_authors_from_text(text)

    # Daca autorii sunt in P.
    for item in candidates:

        if item["tag"] != "P":
            continue

        text = item["text"]

        if looks_like_author_block(text):

            # Evitam sa luam afilierea drept autori.
            if looks_like_affiliation(text):
                continue

            return extract_authors_from_text(text)

    # Fallback general.
    for item in candidates:

        text = item["text"]

        if looks_like_author_block(text):

            if looks_like_affiliation(text):
                continue

            return extract_authors_from_text(text)

    return ""


# =========================================================
# DETECTARE KEYWORDS IN ORICE TAG
# =========================================================

def find_keywords(section):
    """
    Cauta Keywords in ORICE element XML.

    Nu conteaza daca este:

    <P>
    <H5>
    <H4>
    sau alt element textual.
    """

    elements = get_content_elements(section)

    for item in elements:

        text = item["text"]

        if is_keywords(text):

            return extract_keywords(text)

    return ""


# =========================================================
# DETECTARE CONTINUT
# =========================================================

def find_content(section):
    """
    Extrage continutul articolului.

    Regula principala:

    continutul incepe dupa zona de autori/afiliere
    si se termina inainte de Keywords.

    Pentru moment folosim P ca principala sursa
    de continut, dar verificam Keywords indiferent
    de tag.
    """

    elements = get_content_elements(section)

    paragraphs = []

    keywords_found = False

    # -----------------------------------------------------
    # Gasim pozitia Keywords
    # -----------------------------------------------------

    keyword_index = None

    for index, item in enumerate(elements):

        if is_keywords(item["text"]):

            keyword_index = index
            break

    # -----------------------------------------------------
    # Stabilim limita de cautare
    # -----------------------------------------------------

    end_index = (
        keyword_index
        if keyword_index is not None
        else len(elements)
    )

    # -----------------------------------------------------
    # Extragem P-urile de continut
    # -----------------------------------------------------

    for index in range(end_index):

        item = elements[index]

        tag = item["tag"]
        text = item["text"]

        if not text:
            continue

        # Titlurile nu sunt continut.
        if tag in ("H2", "H4", "H5"):
            continue

        # Structurile listelor de afiliere nu sunt continut.
        if tag in ("L", "LI", "Lbl", "LBody"):
            continue

        # Keywords nu este continut.
        if is_keywords(text):
            continue

        # Daca este afiliere, o ignoram.
        if looks_like_affiliation(text):
            continue

        # P este principala sursa pentru continut.
        if tag == "P":

            # Daca este autor, il ignoram.
            if looks_like_author_block(text):
                continue

            paragraphs.append(text)

    return paragraphs


# =========================================================
# PROCESARE UN ARTICOL
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

    authors = find_authors(
        section,
        titles
    )

    # -----------------------------------------------------
    # AFILIERI
    # -----------------------------------------------------

    affiliations = extract_affiliations_from_list(
        section
    )

    # -----------------------------------------------------
    # KEYWORDS
    # -----------------------------------------------------

    keywords = find_keywords(section)

    # -----------------------------------------------------
    # CONTINUT
    # -----------------------------------------------------

    paragraphs = find_content(section)

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

        "content_text": "\n\n".join(
            paragraphs
        )
    }


# =========================================================
# IDENTIFICARE ARTICOLE
# =========================================================

def find_article_sections(part):
    """
    Identifica sectiunile care contin articole.

    Un articol este identificat prin prezenta
    unuia sau mai multor H4.
    """

    articles = []

    for sect in part.iter():

        if get_tag(sect) != "Sect":
            continue

        h4s = []

        for element in sect.iter():

            if get_tag(element) == "H4":

                text = element_text(element)

                if text and not is_keywords(text):
                    h4s.append(text)

        if not h4s:
            continue

        articles.append(sect)

    return articles


# =========================================================
# PARSER PRINCIPAL - ARTICOLE SIMPLE
# =========================================================

def parse_simple_xml(xml_path):
    """
    Parser principal pentru articole simple.

    IMPORTANT:

    Parserul NU se bazeaza rigid pe tagurile XML.

    Identifica informatiile in principal dupa:

    - continut
    - pozitie
    - pattern-uri
    - fallback-uri

    Astfel poate suporta XML-uri in care:

    Keywords = P
    Keywords = H5
    Keywords = H4

    Autori = H5
    Autori = P

    etc.
    """

    try:

        tree = ET.parse(xml_path)
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

        if get_tag(element) == "Part":
            parts.append(element)

    if not parts:
        parts = [root]

    articles = []

    # =====================================================
    # PROCESARE PART
    # =====================================================

    for part in parts:

        section_title = ""

        # -------------------------------------------------
        # H2 = titlul sectiunii
        # -------------------------------------------------

        for element in part.iter():

            if get_tag(element) != "H2":
                continue

            text = element_text(element)

            if text:
                section_title = text
                break

        # -------------------------------------------------
        # IDENTIFICARE ARTICOLE
        # -------------------------------------------------

        article_sections = find_article_sections(
            part
        )

        # -------------------------------------------------
        # PROCESARE ARTICOLE
        # -------------------------------------------------

        for section in article_sections:

            article = parse_article_section(
                section
            )

            # Ignoram blocurile goale.
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

    first_article = (
        articles[0]
        if articles
        else {}
    )

    return {

        "type": "simple",

        "articles": articles,

        # ---------------------------------------------
        # Compatibilitate cu fluxul existent
        # ---------------------------------------------

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
