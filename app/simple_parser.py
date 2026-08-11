import re
import xml.etree.ElementTree as ET


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


def get_direct_children(element, tag_name):
    """
    Returneaza copiii directi cu tag-ul specificat.
    """
    return [
        child
        for child in list(element)
        if child.tag.split("}")[-1] == tag_name
    ]


def get_all_children(element, tag_name):
    """
    Returneaza toate elementele descendente cu tag-ul specificat.
    """
    result = []

    for child in element.iter():
        if child.tag.split("}")[-1] == tag_name:
            result.append(child)

    return result


def extract_authors(element):
    """
    Extrage autorii din H5.

    Exemplu:
        Ancuța-Elena Baciu1, Irina-Maria Dumitru1,2

    Numerele raman in text pentru moment.
    Formatarea superscript/bold va fi facuta in simple_builder.py.
    """

    h5 = None

    for child in element.iter():
        if child.tag.split("}")[-1] == "H5":
            text = element_text(child)

            if text:
                h5 = text
                break

    return h5 or ""


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

    Returneaza o lista de dictionare:
    [
        {
            "number": "1",
            "text": "Institute..."
        }
    ]
    """

    affiliations = []

    for list_element in element.iter():

        if list_element.tag.split("}")[-1] != "L":
            continue

        for li in list_element:

            if li.tag.split("}")[-1] != "LI":
                continue

            number = ""
            body = ""

            for child in li:

                tag = child.tag.split("}")[-1]

                if tag == "Lbl":
                    number = element_text(child)

                elif tag == "LBody":
                    body = element_text(child)

            number = re.sub(r"[^\d]", "", number)

            body = clean_text(body)

            if body:
                affiliations.append({
                    "number": number,
                    "text": body
                })

    return affiliations


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


def extract_paragraphs(element):
    """
    Extrage paragrafele P din articol.

    Keywords sunt scoase separat.
    """

    paragraphs = []
    keywords = ""

    for p in element.iter():

        if p.tag.split("}")[-1] != "P":
            continue

        text = element_text(p)

        if not text:
            continue

        if is_keywords(text):
            keywords = extract_keywords(text)
        else:
            paragraphs.append(text)

    return paragraphs, keywords


def extract_titles(element):
    """
    Extrage titlurile H4.

    In mod normal:
        primul H4 = titlu EN
        al doilea H4 = titlu RO

    Daca exista un singur H4:
        acesta este folosit ca titlu.
    """

    titles = []

    for child in element.iter():

        if child.tag.split("}")[-1] != "H4":
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


def find_article_sections(part):
    """
    Identifica sectiunile care contin articole.

    Un articol simplu este identificat prin prezenta unui H4.

    Nu presupunem ca fiecare Sect are exact aceeasi structura.
    """

    articles = []

    for sect in part.iter():

        if sect.tag.split("}")[-1] != "Sect":
            continue

        h4s = get_all_children(sect, "H4")

        if not h4s:
            continue

        titles = []

        for h4 in h4s:
            text = element_text(h4)

            if text:
                titles.append(text)

        if not titles:
            continue

        articles.append(sect)

    return articles


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

    # ---------------------------------------------------------
    # Gasim toate Part-urile
    # ---------------------------------------------------------

    parts = []

    for element in root.iter():

        if element.tag.split("}")[-1] == "Part":
            parts.append(element)

    # Daca XML-ul nu are Part, folosim root-ul.
    if not parts:
        parts = [root]

    articles = []

    # ---------------------------------------------------------
    # Procesam fiecare Part
    # ---------------------------------------------------------

    for part in parts:

        # H2 poate reprezenta titlul sectiunii/conferintei
        section_title = ""

        for child in part.iter():

            if child.tag.split("}")[-1] == "H2":
                text = element_text(child)

                if text:
                    section_title = text
                    break

        article_sections = find_article_sections(part)

        for section in article_sections:

            article = parse_article_section(section)

            # Ignoram sectiunile fara continut real
            if not (
                article["title_en"]
                or article["title_ro"]
                or article["authors"]
                or article["paragraphs"]
            ):
                continue

            article["section_title"] = section_title

            articles.append(article)

    # ---------------------------------------------------------
    # Rezultatul final
    # ---------------------------------------------------------

    return {
        "type": "simple",

        "articles": articles,

        # Pentru compatibilitate cu fluxul existent
        # putem folosi primul articol ca articol principal.
        "title_en": articles[0]["title_en"] if articles else "",
        "title_ro": articles[0]["title_ro"] if articles else "",
        "authors": articles[0]["authors"] if articles else "",
        "affiliations": articles[0]["affiliations"] if articles else [],
        "keywords": articles[0]["keywords"] if articles else "",
        "content": articles[0]["content"] if articles else [],
        "content_text": (
            articles[0]["content_text"]
            if articles
            else ""
        )
    }
