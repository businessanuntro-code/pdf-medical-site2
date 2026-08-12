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


def tag_name(element):
    """
    Returneaza numele simplu al tagului XML.
    Functioneaza si pentru XML cu namespace.
    """

    if element is None:
        return ""

    return element.tag.split("}")[-1]


def element_text(element):
    """
    Returneaza tot textul continut de un element,
    inclusiv textul elementelor copil.
    """

    if element is None:
        return ""

    text = "".join(element.itertext())

    return clean_text(text)


# =========================================================
# IDENTIFICARE KEYWORDS
# =========================================================

def is_keywords_text(text):
    """
    Verifica daca un text reprezinta zona Keywords.

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
    Extrage continutul de dupa:

    Keywords:

    sau

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
# IDENTIFICARE AUTORI
# =========================================================

def looks_like_author_line(text):
    """
    Verifica daca un text pare sa fie o lista de autori.

    Exemple acceptate:

    C. Achiroaei1,2, Diana-Ioana Panaite1,2, C. Volovăț1,2

    Ancuța-Elena Baciu1, Irina-Maria Dumitru1,2

    Eugen Brătucu, Claudiu Daha, Laurenţiu Simion

    IMPORTANT:
    Functia este intentionat toleranta.
    Nu cere obligatoriu cifre dupa autori.
    """

    if not text:
        return False

    text = clean_text(text)

    if len(text) > 500:
        return False

    # Nu este autor daca este clar Keywords
    if is_keywords_text(text):
        return False

    # Nu consideram textul propriu-zis al articolului drept autori.
    beginning_words = [
        "introduction.",
        "objective.",
        "materials and method.",
        "materials and methods.",
        "results.",
        "conclusions.",
        "background.",
        "aim.",
        "purpose."
    ]

    lower = text.lower()

    for word in beginning_words:

        if lower.startswith(word):
            return False

    # Daca exista virgule intre mai multe nume,
    # este un indiciu puternic de lista de autori.
    comma_parts = [
        part.strip()
        for part in text.split(",")
        if part.strip()
    ]

    if len(comma_parts) >= 2:

        # Evitam frazele lungi care contin virgule.
        if len(text.split()) <= 45:
            return True

    # Caz cu un singur autor.
    # Acceptam linii relativ scurte care contin o forma
    # tipica de nume.
    if len(comma_parts) == 1 and len(text.split()) <= 8:

        if re.search(
            r"\b[A-ZĂÂÎȘȚ][a-zăâîșț]+",
            text
        ):
            return True

    return False


def extract_author_text(text):
    """
    Normalizeaza textul autorilor.

    Nu modifica numele si nu elimina cifrele.
    Cifrele vor fi transformate in superscript
    in simple_builder.py.
    """

    return clean_text(text)


# =========================================================
# IDENTIFICARE AFILIERI
# =========================================================

AFFILIATION_KEYWORDS = [
    "institute",
    "university",
    "faculty",
    "hospital",
    "clinical",
    "clinic",
    "medical center",
    "medical centre",
    "center",
    "centre",
    "laboratory",
    "laboratories",
    "department",
    "school",
    "college",
    "academy",
    "association",
    "bucharest",
    "romania",
    "nuclearelectrica",
    "institute of oncology",
    "fundeni",
    "faculty of physics"
]


def looks_like_affiliation(text):
    """
    Verifica daca un text pare sa fie o afiliere.

    Nu ne bazam exclusiv pe tagul XML.
    """

    if not text:
        return False

    text = clean_text(text)

    lower = text.lower()

    for keyword in AFFILIATION_KEYWORDS:

        if keyword in lower:
            return True

    return False


# =========================================================
# AFILIERI DIN <L>
# =========================================================

def extract_list_affiliations(section):
    """
    Extrage afilierile atunci cand XML-ul foloseste:

    <L>
        <LI>
            <Lbl>1.</Lbl>
            <LBody>...</LBody>
        </LI>
    </L>
    """

    affiliations = []

    for element in section.iter():

        if tag_name(element) != "L":
            continue

        for li in list(element):

            if tag_name(li) != "LI":
                continue

            number = ""
            text = ""

            for child in list(li):

                child_tag = tag_name(child)

                if child_tag == "Lbl":

                    number = clean_text(
                        element_text(child)
                    )

                elif child_tag == "LBody":

                    text = clean_text(
                        element_text(child)
                    )

            if text:

                number = re.sub(
                    r"[^\d]",
                    "",
                    number
                )

                affiliations.append(
                    {
                        "number": number,
                        "text": text
                    }
                )

    return affiliations


# =========================================================
# EXTRAGERE ELEMENTE TEXT
# =========================================================

def get_text_elements(section):
    """
    Returneaza elementele textuale in ordinea in care apar
    in XML.

    Nu presupune ca informatia este in acelasi tag.

    Sunt luate in calcul:

    H2
    H4
    H5
    P
    LBody
    """

    elements = []

    allowed_tags = {
        "H2",
        "H4",
        "H5",
        "P",
        "LBody"
    }

    for element in section.iter():

        current_tag = tag_name(element)

        if current_tag not in allowed_tags:
            continue

        text = element_text(element)

        if not text:
            continue

        elements.append(
            {
                "tag": current_tag,
                "text": text,
                "element": element
            }
        )

    return elements


# =========================================================
# IDENTIFICARE TITLURI
# =========================================================

def extract_titles(section):
    """
    Extrage primele doua titluri H4.

    primul H4  = title_en
    al doilea H4 = title_ro
    """

    titles = []

    for element in section.iter():

        if tag_name(element) != "H4":
            continue

        text = element_text(element)

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
    Identifica sectiunile care reprezinta articole.

    Un articol trebuie sa contina cel putin un H4.

    IMPORTANT:

    XML-ul poate avea multe Sect imbricate.

    Alegem doar Sect-ul exterior al articolului,
    pentru a evita dublarea continutului.
    """

    articles = []

    for sect in part.iter():

        if tag_name(sect) != "Sect":
            continue

        h4s = [
            element
            for element in sect.iter()
            if tag_name(element) == "H4"
            and element_text(element)
        ]

        if not h4s:
            continue

        # Daca exista un parinte Sect care are deja H4,
        # acest Sect este o subsectiune a aceluiasi articol.
        is_nested_article = False

        for possible_parent in part.iter():

            if possible_parent is sect:
                continue

            if tag_name(possible_parent) != "Sect":
                continue

            descendants = list(
                possible_parent.iter()
            )

            if sect not in descendants:
                continue

            parent_has_h4 = any(
                tag_name(x) == "H4"
                and element_text(x)
                for x in possible_parent.iter()
            )

            if parent_has_h4:

                is_nested_article = True
                break

        if is_nested_article:
            continue

        articles.append(sect)

    return articles


# =========================================================
# PROCESARE ARTICOL
# =========================================================

def parse_article_section(section):
    """
    Proceseaza un singur articol simplu.

    Ordinea logica este:

    H4
    ↓
    AUTORI
    ↓
    AFILIERI
    ↓
    CONTINUT
    ↓
    KEYWORDS

    Nu presupune ca aceste informatii folosesc
    aceleasi taguri XML in toate documentele.
    """

    titles = extract_titles(section)

    title_en = titles["title_en"]
    title_ro = titles["title_ro"]

    text_elements = get_text_elements(section)

    # -----------------------------------------------------
    # AFILIERI EXPLICITE DIN <L>
    # -----------------------------------------------------

    list_affiliations = extract_list_affiliations(
        section
    )

    affiliations = list_affiliations.copy()

    # -----------------------------------------------------
    # GASIM POZITIA CELUI DE-AL DOILEA H4
    # -----------------------------------------------------

    title_h4_count = 0
    title_end_index = -1

    for index, item in enumerate(text_elements):

        if item["tag"] == "H4":

            title_h4_count += 1

            if title_h4_count == 2:
                title_end_index = index
                break

    # Daca avem un singur H4,
    # acesta reprezinta limita initiala.
    if title_end_index == -1:

        for index, item in enumerate(text_elements):

            if item["tag"] == "H4":

                title_end_index = index
                break

    # -----------------------------------------------------
    # VARIABILE
    # -----------------------------------------------------

    authors = ""

    paragraphs = []

    keywords = ""

    author_found = False
    affiliation_started = False
    content_started = False
    keywords_found = False

    # -----------------------------------------------------
    # PROCESAM TEXTUL DUPA TITLURI
    # -----------------------------------------------------

    for index, item in enumerate(text_elements):

        if index <= title_end_index:
            continue

        tag = item["tag"]
        text = clean_text(item["text"])

        if not text:
            continue

        # -------------------------------------------------
        # KEYWORDS
        # -------------------------------------------------

        if is_keywords_text(text):

            keywords = extract_keywords(text)

            keywords_found = True

            break

        # -------------------------------------------------
        # LBody = AFILIERE
        # -------------------------------------------------

        if tag == "LBody":

            affiliation_started = True

            number = ""

            # Cautam numarul corespunzator,
            # daca exista in structura L.
            parent = item["element"].getparent() if hasattr(
                item["element"],
                "getparent"
            ) else None

            # ElementTree standard nu are getparent().
            # Numarul este preluat separat din
            # extract_list_affiliations().
            if affiliations:

                existing_texts = {
                    aff["text"]
                    for aff in affiliations
                }

                if text not in existing_texts:

                    affiliations.append(
                        {
                            "number": "",
                            "text": text
                        }
                    )

            else:

                affiliations.append(
                    {
                        "number": "",
                        "text": text
                    }
                )

            continue

        # -------------------------------------------------
        # DACA AVEM DEJA CONTINUT,
        # TOT CE URMEAZA RAMANE CONTINUT
        # PANA LA KEYWORDS
        # -------------------------------------------------

        if content_started:

            # Nu mai clasificam ulterior
            # alte elemente drept autori/afiliere.
            paragraphs.append(text)

            continue

        # -------------------------------------------------
        # AUTORI
        # -------------------------------------------------

        if not author_found:

            # H5 dupa titluri este foarte probabil autor.
            if tag == "H5":

                authors = extract_author_text(text)

                author_found = True

                continue

            # Unele XML-uri pun autorii in P.
            if tag == "P" and looks_like_author_line(text):

                authors = extract_author_text(text)

                author_found = True

                continue

        # -------------------------------------------------
        # AFILIERE
        # -------------------------------------------------

        if author_found and not content_started:

            if tag == "P" and looks_like_affiliation(text):

                affiliation_started = True

                already_exists = any(
                    aff.get("text", "") == text
                    for aff in affiliations
                )

                if not already_exists:

                    affiliations.append(
                        {
                            "number": "",
                            "text": text
                        }
                    )

                continue

            # Daca exista deja o lista de afiliere
            # si apareste un P dupa ea, acesta este
            # foarte probabil inceputul continutului.
            if affiliations:

                content_started = True

                paragraphs.append(text)

                continue

            # -------------------------------------------------
            # DACA NU AVEM AFILIERI
            #
            # Primul text care nu este afiliere
            # este considerat continut.
            # -------------------------------------------------

            content_started = True

            paragraphs.append(text)

            continue

        # -------------------------------------------------
        # DACA NU AM IDENTIFICAT AUTORII
        #
        # Dar apare continut, il pastram.
        # -------------------------------------------------

        if not author_found:

            content_started = True

            paragraphs.append(text)

    # -----------------------------------------------------
    # FALLBACK:
    # DACA EXISTA AFILIERI IN L DAR NU AU FOST GASITE
    # IN ORDINEA TEXTULUI, LE PASTRAM.
    # -----------------------------------------------------

    if list_affiliations:

        final_affiliations = []

        for aff in list_affiliations:

            if not any(
                existing.get("text", "") == aff.get("text", "")
                for existing in final_affiliations
            ):

                final_affiliations.append(aff)

        for aff in affiliations:

            if not any(
                existing.get("text", "") == aff.get("text", "")
                for existing in final_affiliations
            ):

                final_affiliations.append(aff)

        affiliations = final_affiliations

    # -----------------------------------------------------
    # CURATARE PARAGRAFE
    # -----------------------------------------------------

    cleaned_paragraphs = []

    for paragraph in paragraphs:

        paragraph = clean_text(paragraph)

        if not paragraph:
            continue

        if is_keywords_text(paragraph):
            continue

        cleaned_paragraphs.append(
            paragraph
        )

    paragraphs = cleaned_paragraphs

    # -----------------------------------------------------
    # REZULTAT ARTICOL
    # -----------------------------------------------------

    return {
        "title_en": title_en,
        "title_ro": title_ro,
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
# PARSER PRINCIPAL - ARTICOLE SIMPLE
# =========================================================

def parse_simple_xml(xml_path):
    """
    Parser principal pentru articole simple.

    IMPORTANT:

    Acest parser este complet separat de parser.py
    pentru articolele stiintifice.

    XML-ul poate avea structuri usor diferite.

    Parserul cauta informatia semantic si dupa ordine,
    nu exclusiv dupa taguri fixe.
    """

    try:

        tree = ET.parse(xml_path)

        root = tree.getroot()

    except ET.ParseError as exc:

        raise ValueError(
            f"XML invalid sau imposibil de procesat: {exc}"
        ) from exc

    # -----------------------------------------------------
    # GASIM PART-URILE
    # -----------------------------------------------------

    parts = []

    for element in root.iter():

        if tag_name(element) == "Part":

            parts.append(element)

    if not parts:

        parts = [root]

    # -----------------------------------------------------
    # PROCESAM ARTICOLELE
    # -----------------------------------------------------

    articles = []

    for part in parts:

        # -------------------------------------------------
        # TITLUL SECTIUNII / CONFERINTEI
        # -------------------------------------------------

        section_title = ""

        for element in part.iter():

            if tag_name(element) != "H2":
                continue

            text = element_text(element)

            if text:

                section_title = text

                break

        # -------------------------------------------------
        # GASIM ARTICOLELE
        # -------------------------------------------------

        article_sections = find_article_sections(
            part
        )

        for section in article_sections:

            article = parse_article_section(
                section
            )

            # -------------------------------------------------
            # IGNORAM SECTIUNILE FARA CONTINUT REAL
            # -------------------------------------------------

            if not (
                article["title_en"]
                or article["title_ro"]
                or article["authors"]
                or article["paragraphs"]
            ):

                continue

            article["section_title"] = (
                section_title
            )

            articles.append(
                article
            )

    # -----------------------------------------------------
    # REZULTAT FINAL
    # -----------------------------------------------------

    first_article = (
        articles[0]
        if articles
        else {}
    )

    return {
        "type": "simple",

        "articles": articles,

        # -------------------------------------------------
        # COMPATIBILITATE CU FLUXUL EXISTENT
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
        )
    }
