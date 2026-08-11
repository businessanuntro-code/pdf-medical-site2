```python
import re
import xml.etree.ElementTree as ET


# =========================================================
# UTILITARE GENERALE
# =========================================================

def clean_text(text):
    """
    Curata textul extras din XML:
    - elimina spatiile inutile
    - normalizeaza spatiile
    - elimina caracterele non-breaking space
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

    text = "".join(element.itertext())

    return clean_text(text)


def tag_name(element):
    """
    Returneaza numele tagului fara namespace.
    """
    return element.tag.split("}")[-1]


def get_direct_children(element, tag_name_value):
    """
    Returneaza copiii directi cu tag-ul specificat.
    """
    return [
        child
        for child in list(element)
        if tag_name(child) == tag_name_value
    ]


def get_all_children(element, tag_name_value):
    """
    Returneaza toate elementele descendente cu tag-ul specificat.
    """
    result = []

    for child in element.iter():

        if tag_name(child) == tag_name_value:
            result.append(child)

    return result


# =========================================================
# AUTORI
# =========================================================

def extract_authors(element):
    """
    Extrage autorii din H5.

    Exemplu:
        Ancuța-Elena Baciu1, Irina-Maria Dumitru1,2

    Numerele raman in text pentru moment.
    Formatarea superscript/bold va fi facuta
    in simple_builder.py.
    """

    for child in element.iter():

        if tag_name(child) != "H5":
            continue

        text = element_text(child)

        if text:
            return text

    return ""


# =========================================================
# AFILIERI
# =========================================================

def extract_affiliations(element):
    """
    Extrage afilierile din listele XML.

    Exemplu:

    <L>
        <LI>
            <Lbl>1.</Lbl>
            <LBody>Institute...</LBody>
        </LI>
    </L>

    Returneaza:
    [
        {
            "number": "1",
            "text": "Institute..."
        }
    ]
    """

    affiliations = []

    for list_element in element.iter():

        if tag_name(list_element) != "L":
            continue

        for li in list_element:

            if tag_name(li) != "LI":
                continue

            number = ""
            body = ""

            for child in li:

                child_tag = tag_name(child)

                if child_tag == "Lbl":
                    number = element_text(child)

                elif child_tag == "LBody":
                    body = element_text(child)

            number = re.sub(r"[^\d]", "", number)
            body = clean_text(body)

            if body:

                affiliations.append({
                    "number": number,
                    "text": body
                })

    return affiliations


# =========================================================
# KEYWORDS
# =========================================================

def is_keywords(text):
    """
    Verifica daca textul este un paragraf de keywords.
    """

    if not text:
        return False

    normalized = text.lower().strip()

    return (
        normalized.startswith("keywords:")
        or normalized.startswith("keywords :")
        or normalized.startswith("cuvinte cheie:")
        or normalized.startswith("cuvinte cheie :")
    )


def extract_keywords(text):
    """
    Extrage continutul de dupa Keywords:
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
# PARAGRAFE
# =========================================================

def extract_paragraphs(element):
    """
    Extrage paragrafele P din articol.

    Keywords sunt scoase separat.
    """

    paragraphs = []
    keywords = ""

    for p in element.iter():

        if tag_name(p) != "P":
            continue

        text = element_text(p)

        if not text:
            continue

        if is_keywords(text):

            keywords = extract_keywords(text)

        else:

            paragraphs.append(text)

    return paragraphs, keywords


# =========================================================
# TITLURI
# =========================================================

def extract_titles(element):
    """
    Extrage titlurile H4.

    In mod normal:
        primul H4 = titlu EN
        al doilea H4 = titlu RO

    Daca exista un singur H4:
        acesta este folosit ca titlu.

    IMPORTANT:
    Nu mai luam H4 din sectiuni copil
    care reprezinta de fapt acelasi articol.
    """

    titles = []

    for child in element.iter():

        if tag_name(child) != "H4":
            continue

        text = element_text(child)

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

def is_article_section(section):
    """
    Verifica daca un Sect reprezinta efectiv inceputul
    unui articol.

    Un articol trebuie sa aiba un H4 DIRECT.

    Aceasta este diferenta importanta fata de versiunea
    anterioara.

    Nu mai consideram articol orice Sect care are un H4
    undeva in interiorul sau.
    """

    direct_h4s = get_direct_children(section, "H4")

    return len(direct_h4s) > 0


def find_article_sections(part):
    """
    Identifica sectiunile care reprezinta articole.

    IMPORTANT:

    XML-ul are Sect-uri imbricate:

        Sect
          H4
          Sect
            H4
            Sect
              H5
              P
              P

    Versiunea veche folosea:

        get_all_children(sect, "H4")

    Astfel, acelasi articol era identificat de mai multe
    ori.

    Acum verificam DOAR H4 DIRECT in Sect.

    Astfel:

        Sect cu H4 direct = articol

        Sect fara H4 direct = continut al articolului,
        nu articol nou.
    """

    articles = []

    for sect in part.iter():

        if tag_name(sect) != "Sect":
            continue

        if not is_article_section(sect):
            continue

        articles.append(sect)

    return articles


# =========================================================
# PROCESARE ARTICOL
# =========================================================

def parse_article_section(section):
    """
    Proceseaza un singur articol simplu.
    """

    titles = extract_titles(section)

    authors = extract_authors(section)

    affiliations = extract_affiliations(section)

    paragraphs, keywords = extract_paragraphs(section)

    return {
        "title_en": titles["title_en"],
        "title_ro": titles["title_ro"],
        "titles": titles["titles"],

        "authors": authors,

        "affiliations": affiliations,

        "paragraphs": paragraphs,

        "keywords": keywords,

        "content": paragraphs,

        "content_text": "\n\n".join(paragraphs)
    }


# =========================================================
# PARSER PRINCIPAL - ARTICOLE SIMPLE
# =========================================================

def parse_simple_xml(xml_path):
    """
    Parser principal pentru articole simple.

    IMPORTANT:
    Aceasta functie este independenta de parser.py
    si este folosita exclusiv pentru articole simple.
    """

    try:

        tree = ET.parse(xml_path)
        root = tree.getroot()

    except ET.ParseError as exc:

        raise ValueError(
            f"XML invalid sau imposibil de procesat: {exc}"
        ) from exc

    # -----------------------------------------------------
    # GASIM TOATE PART-URILE
    # -----------------------------------------------------

    parts = []

    for element in root.iter():

        if tag_name(element) == "Part":
            parts.append(element)

    # Daca XML-ul nu are Part, folosim root-ul.
    if not parts:
        parts = [root]

    articles = []

    # -----------------------------------------------------
    # PROCESAM FIECARE PART
    # -----------------------------------------------------

    for part in parts:

        # -------------------------------------------------
        # TITLUL SECTIUNII / CONFERINTEI
        # -------------------------------------------------

        section_title = ""

        for child in part:

            if tag_name(child) != "H2":
                continue

            text = element_text(child)

            if text:

                section_title = text
                break

        # -------------------------------------------------
        # GASIM ARTICOLELE
        # -------------------------------------------------

        article_sections = find_article_sections(part)

        # -------------------------------------------------
        # PROCESAM FIECARE ARTICOL O SINGURA DATA
        # -------------------------------------------------

        for section in article_sections:

            article = parse_article_section(section)

            # ---------------------------------------------
            # IGNORAM SECTIUNILE FARA CONTINUT REAL
            # ---------------------------------------------

            if not (
                article["title_en"]
                or article["title_ro"]
                or article["authors"]
                or article["paragraphs"]
            ):
                continue

            article["section_title"] = section_title

            articles.append(article)

    # -----------------------------------------------------
    # REZULTAT FINAL
    # -----------------------------------------------------

    return {
        "type": "simple",

        "articles": articles,

        # Pentru compatibilitate cu fluxul existent
        # folosim primul articol ca articol principal.

        "title_en": (
            articles[0]["title_en"]
            if articles
            else ""
        ),

        "title_ro": (
            articles[0]["title_ro"]
            if articles
            else ""
        ),

        "authors": (
            articles[0]["authors"]
            if articles
            else ""
        ),

        "affiliations": (
            articles[0]["affiliations"]
            if articles
            else []
        ),

        "keywords": (
            articles[0]["keywords"]
            if articles
            else ""
        ),

        "content": (
            articles[0]["content"]
            if articles
            else []
        ),

        "content_text": (
            articles[0]["content_text"]
            if articles
            else ""
        )
    }
```
