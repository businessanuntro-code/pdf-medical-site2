import re
from html import escape


# =========================================================
# FUNCTII GENERALE
# =========================================================

def clean_text(text):
    """
    Normalizeaza doar spatiile tehnice.
    Nu modifica ordinea sau continutul informational.
    """

    if not text:
        return ""

    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def escape_html(text):
    """
    Protejeaza textul pentru HTML.
    """

    return escape(clean_text(text))


# =========================================================
# DETECTARE - KEYWORDS
# =========================================================

def is_keywords(text):
    """
    Detecteaza un bloc de Keywords.

    Accepta:
        Keywords:
        Keywords :
        Cuvinte cheie:
        Cuvinte cheie :
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


# =========================================================
# DETECTARE - NUMERE AUTORI
# =========================================================

def format_author_numbers(text):
    """
    Transforma numerele atasate numelor de autori
    in superscript.

    Exemple:

    Achiroaei1
        ->
    Achiroaei<sup>1</sup>

    Achiroaei1,2
        ->
    Achiroaei<sup>1,2</sup>

    Regula se aplica numai dupa ce blocul
    a fost identificat ca fiind bloc de autori.
    """

    if not text:
        return ""

    text = escape_html(text)

    return re.sub(
        r"(?<=[A-Za-zÀ-ÖØ-öø-ÿĂăÂâÎîȘșŞşȚțŢţĂăÂâÎî\-])"
        r"(\d+(?:\s*,\s*\d+)*)",
        lambda match: f"<sup>{match.group(1)}</sup>",
        text
    )


# =========================================================
# DETECTARE - NUME DE PERSOANE
# =========================================================

def looks_like_person_name(name):
    """
    Verifica daca un segment seamana cu un nume de persoana.

    Nu trebuie sa fie perfect.
    Este doar una dintre regulile folosite
    la identificarea blocului de autori.
    """

    if not name:
        return False

    name = clean_text(name)

    # Eliminam eventualele numere de afiliere.
    name_without_numbers = re.sub(
        r"\d+(?:\s*,\s*\d+)*$",
        "",
        name
    ).strip()

    if not name_without_numbers:
        return False

    words = name_without_numbers.split()

    # Un nume trebuie sa aiba cel putin doua componente.
    if len(words) < 2:
        return False

    # Nu consideram propozitii lungi drept nume.
    if len(name_without_numbers) > 80:
        return False

    # Evitam evidente cuvinte de institutie.
    institution_words = (
        "institute",
        "university",
        "hospital",
        "center",
        "centre",
        "clinic",
        "department",
        "laboratory",
        "association",
        "faculty",
        "medical",
        "bucharest",
        "romania"
    )

    lower_name = name_without_numbers.lower()

    for word in institution_words:
        if word in lower_name:
            return False

    return True


# =========================================================
# DETECTARE - AUTORI
# =========================================================

def author_block_score(text, position, previous_blocks):
    """
    Calculeaza un scor pentru probabilitatea ca un bloc
    sa contina autori.

    Nu folosim o singura regula.

    Mai multe indicii = scor mai mare.
    """

    if not text:
        return 0

    text = clean_text(text)

    score = 0

    # -----------------------------------------------------
    # Bloc relativ scurt
    # -----------------------------------------------------

    if len(text) <= 250:
        score += 1

    if len(text) <= 180:
        score += 1

    # -----------------------------------------------------
    # Mai multe segmente separate prin virgula
    # -----------------------------------------------------

    parts = [
        clean_text(part)
        for part in text.split(",")
        if clean_text(part)
    ]

    if len(parts) >= 2:
        score += 2

    if len(parts) >= 3:
        score += 1

    # -----------------------------------------------------
    # Verificam daca segmentele seamana cu nume
    # -----------------------------------------------------

    if parts:

        name_like_count = sum(
            1
            for part in parts
            if looks_like_person_name(part)
        )

        if name_like_count >= 2:
            score += 3

        if name_like_count >= 3:
            score += 1

    # -----------------------------------------------------
    # Exista numere de afiliere dupa nume
    # -----------------------------------------------------

    if re.search(
        r"[A-Za-zÀ-ÖØ-öø-ÿĂăÂâÎîȘșŞşȚțŢţ\-]"
        r"\d+(?:\s*,\s*\d+)*",
        text
    ):
        score += 3

    # -----------------------------------------------------
    # Pozitie apropiata de inceput
    # -----------------------------------------------------

    if position <= 5:
        score += 1

    # -----------------------------------------------------
    # Bloc anterior este heading
    # -----------------------------------------------------

    if previous_blocks:

        previous_tag = previous_blocks[-1].get(
            "tag",
            ""
        )

        if previous_tag in (
            "H1",
            "H2",
            "H3",
            "H4",
            "H5"
        ):
            score += 2

    return score


def is_author_block(
    text,
    position,
    previous_blocks
):
    """
    Decide daca textul este probabil un bloc de autori.

    Pragul este intentionat conservator.
    """

    score = author_block_score(
        text,
        position,
        previous_blocks
    )

    return score >= 6


# =========================================================
# DETECTARE - AFILIERE
# =========================================================

def affiliation_score(text, position, previous_blocks):
    """
    Calculeaza probabilitatea ca un bloc sa fie afiliere.
    """

    if not text:
        return 0

    text = clean_text(text)

    score = 0

    # -----------------------------------------------------
    # Numerotare afiliere
    # -----------------------------------------------------

    if re.match(
        r"^\s*\d+\s*[\.\)]",
        text
    ):
        score += 4

    # -----------------------------------------------------
    # Cuvinte frecvente in institutii
    # -----------------------------------------------------

    institution_words = [
        "institute",
        "university",
        "hospital",
        "clinic",
        "center",
        "centre",
        "faculty",
        "department",
        "laboratory",
        "association",
        "medical",
        "oncology",
        "bucharest",
        "romania"
    ]

    lower_text = text.lower()

    matches = sum(
        1
        for word in institution_words
        if word in lower_text
    )

    if matches >= 1:
        score += 2

    if matches >= 2:
        score += 2

    # -----------------------------------------------------
    # Afilierea este de obicei relativ scurta
    # -----------------------------------------------------

    if len(text) <= 300:
        score += 1

    # -----------------------------------------------------
    # Pozitionare dupa autori
    # -----------------------------------------------------

    if previous_blocks:

        previous_text = clean_text(
            previous_blocks[-1].get(
                "text",
                ""
            )
        )

        if is_author_block(
            previous_text,
            max(position - 1, 0),
            previous_blocks[:-1]
        ):
            score += 3

    return score


def is_affiliation_block(
    text,
    position,
    previous_blocks
):
    """
    Decide daca textul este probabil o afiliere.
    """

    score = affiliation_score(
        text,
        position,
        previous_blocks
    )

    return score >= 5


# =========================================================
# DETECTARE - TITLU
# =========================================================

def is_title_tag(tag):
    """
    Verifica daca tag-ul este heading.
    """

    return tag in (
        "H1",
        "H2",
        "H3",
        "H4",
        "H5"
    )


def title_score(
    tag,
    text,
    position
):
    """
    Scor simplu pentru titlu.
    """

    if not text:
        return 0

    score = 0

    if is_title_tag(tag):
        score += 4

    if position <= 4:
        score += 2

    if len(text) <= 400:
        score += 1

    return score


# =========================================================
# FORMATARE - TITLU
# =========================================================

def format_title(
    text,
    title_number
):
    """
    Primele doua titluri sunt tratate astfel:

    primul  = EN -> bold
    al doilea = RO -> bold + italic

    Dupa primele doua, heading-ul este pastrat
    fara o interpretare agresiva.
    """

    text = escape_html(text)

    if title_number == 1:

        return (
            '<h2 class="simple-title-en">'
            f"<strong>{text}</strong>"
            "</h2>"
        )

    if title_number == 2:

        return (
            '<h3 class="simple-title-ro">'
            f"<strong><em>{text}</em></strong>"
            "</h3>"
        )

    return (
        '<div class="simple-heading">'
        f"{text}"
        "</div>"
    )


# =========================================================
# FORMATARE - AUTORI
# =========================================================

def format_authors(text):
    """
    Autori:
        - bold
        - numere superscript
    """

    formatted = format_author_numbers(
        text
    )

    return (
        '<div class="simple-authors">'
        f"<strong>{formatted}</strong>"
        "</div>"
    )


# =========================================================
# FORMATARE - AFILIERE
# =========================================================

def format_affiliation(
    text,
    affiliation_number
):
    """
    Afilierea este italic.

    Daca textul nu are deja numerotare,
    builderul poate afisa numarul identificat.
    """

    text = clean_text(text)

    # -----------------------------------------------------
    # Verificam daca textul are deja numar.
    # -----------------------------------------------------

    has_number = bool(
        re.match(
            r"^\s*\d+\s*[\.\)]",
            text
        )
    )

    formatted_text = escape_html(
        text
    )

    if has_number:

        return (
            '<div class="simple-affiliation">'
            f"<em>{formatted_text}</em>"
            "</div>"
        )

    return (
        '<div class="simple-affiliation">'
        f'<span class="affiliation-number">'
        f"{affiliation_number}."
        f"</span> "
        f"<em>{formatted_text}</em>"
        "</div>"
    )


# =========================================================
# FORMATARE - KEYWORDS
# =========================================================

def format_keywords(text):
    """
    Keywords:
        doar eticheta este bold.
    """

    text = clean_text(text)

    match = re.match(
        r"^(Keywords|Cuvinte\s+cheie)\s*:\s*(.*)$",
        text,
        flags=re.IGNORECASE
    )

    if not match:
        return (
            '<p class="simple-keywords">'
            f"{escape_html(text)}"
            "</p>"
        )

    label = match.group(1)
    content = match.group(2)

    return (
        '<p class="simple-keywords">'
        f"<strong>{escape_html(label)}:</strong>"
        f" {escape_html(content)}"
        "</p>"
    )


# =========================================================
# FORMATARE - CONTINUT
# =========================================================

def format_content(text):
    """
    Continut normal.
    """

    return (
        '<p class="simple-paragraph">'
        f"{escape_html(text)}"
        "</p>"
    )


# =========================================================
# CLASIFICARE BLOC
# =========================================================

def classify_block(
    element,
    position,
    previous_blocks
):
    """
    Clasifica un element primit de parser.

    Categorii:

        TITLE
        AUTHORS
        AFFILIATION
        KEYWORDS
        CONTENT
        OTHER
    """

    tag = element.get(
        "tag",
        ""
    )

    text = clean_text(
        element.get(
            "text",
            ""
        )
    )

    if not text:
        return "OTHER"

    # =====================================================
    # 1. KEYWORDS
    # =====================================================

    if is_keywords(text):

        return "KEYWORDS"

    # =====================================================
    # 2. TITLURI
    # =====================================================

    if is_title_tag(tag):

        # Primele heading-uri de la inceput sunt considerate
        # titluri.
        if position <= 4:

            return "TITLE"

    # =====================================================
    # 3. AUTORI
    # =====================================================

    if is_author_block(
        text,
        position,
        previous_blocks
    ):

        return "AUTHORS"

    # =====================================================
    # 4. AFILIERI
    # =====================================================

    if is_affiliation_block(
        text,
        position,
        previous_blocks
    ):

        return "AFFILIATION"

    # =====================================================
    # 5. CONTINUT
    # =====================================================

    if tag == "P":

        return "CONTENT"

    # =====================================================
    # 6. HEADING CARE NU A FOST IDENTIFICAT
    # =====================================================

    if is_title_tag(tag):

        return "TITLE"

    # =====================================================
    # 7. FALLBACK
    # =====================================================

    return "OTHER"


# =========================================================
# BUILDER PRINCIPAL
# =========================================================

def build_simple_html(data):
    """
    Builder inteligent pentru articole simple.

    IMPORTANT:

    simple_parser.py transmite XML-ul in forma:

        {
            "tag": "...",
            "text": "..."
        }

    Builderul interpreteaza aceste blocuri
    si incearca sa identifice:

        TITLE
        AUTHORS
        AFFILIATION
        CONTENT
        KEYWORDS

    Regulile sunt intentionat conservatoare.

    Daca un bloc nu poate fi identificat sigur,
    este pastrat ca text si NU este sters.
    """

    if not data:
        return ""

    elements = data.get(
        "elements",
        []
    )

    if not elements:
        return ""

    html = []

    html.append(
        '<div class="simple-articles">'
    )

    previous_blocks = []

    title_number = 0

    affiliation_number = 0

    # =====================================================
    # PARCURGEM TOATE ELEMENTELE IN ORDINEA XML
    # =====================================================

    for position, element in enumerate(
        elements
    ):

        tag = element.get(
            "tag",
            ""
        )

        text = clean_text(
            element.get(
                "text",
                ""
            )
        )

        if not text:
            continue

        # -------------------------------------------------
        # Clasificare
        # -------------------------------------------------

        category = classify_block(
            element,
            position,
            previous_blocks
        )

        # =================================================
        # TITLE
        # =================================================

        if category == "TITLE":

            title_number += 1

            html.append(
                format_title(
                    text,
                    title_number
                )
            )

        # =================================================
        # AUTHORS
        # =================================================

        elif category == "AUTHORS":

            html.append(
                format_authors(
                    text
                )
            )

        # =================================================
        # AFFILIATION
        # =================================================

        elif category == "AFFILIATION":

            affiliation_number += 1

            html.append(
                format_affiliation(
                    text,
                    affiliation_number
                )
            )

        # =================================================
        # KEYWORDS
        # =================================================

        elif category == "KEYWORDS":

            html.append(
                format_keywords(
                    text
                )
            )

        # =================================================
        # CONTENT
        # =================================================

        elif category == "CONTENT":

            html.append(
                format_content(
                    text
                )
            )

        # =================================================
        # OTHER
        # =================================================

        else:

            # Nu pierdem informatia.
            # Pentru elementele neidentificate pastram
            # textul intr-un div simplu.

            html.append(
                '<div class="simple-other">'
                f"{escape_html(text)}"
                "</div>"
            )

        # -------------------------------------------------
        # Pastram contextul pentru urmatorul bloc.
        # -------------------------------------------------

        previous_blocks.append(
            {
                "tag": tag,
                "text": text,
                "category": category
            }
        )

    html.append(
        "</div>"
    )

    return "\n".join(
        html
    )
