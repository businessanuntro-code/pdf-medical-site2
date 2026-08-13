import re
from html import escape


# =========================================================
# FUNCTII GENERALE
# =========================================================

def clean_text(text):
    """
    Normalizeaza doar spatiile.
    Nu modifica informatia primita din parser.
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

    return escape(
        clean_text(text)
    )


# =========================================================
# AUTORI - NUMERE SUPERSCRIPT
# =========================================================

def format_author_numbers(text):
    """
    Transforma numerele de afiliere aflate imediat dupa
    numele autorilor in superscript.

    Exemple:

    Achiroaei1
    ->
    Achiroaei<sup>1</sup>

    Achiroaei1,2
    ->
    Achiroaei<sup>1,2</sup>

    Achiroaei1,2,3
    ->
    Achiroaei<sup>1,2,3</sup>
    """

    if not text:
        return ""

    text = escape_html(text)

    return re.sub(
        r"(?<=[A-Za-zÀ-ÖØ-öø-ÿĂăÂâÎîȘșŞşȚțŢţ\-])"
        r"(\d+(?:\s*,\s*\d+)*)",
        lambda match:
            f"<sup>{match.group(1)}</sup>",
        text
    )


# =========================================================
# AUTORI
# =========================================================

def format_authors(text):
    """
    Afiseaza autorii cu bold.

    Numerele asociate autorilor sunt superscript.
    """

    if not text:
        return ""

    formatted = format_author_numbers(
        text
    )

    return (
        '<div class="simple-authors">'
        f"<strong>{formatted}</strong>"
        "</div>"
    )


# =========================================================
# IDENTIFICARE AUTORI
# =========================================================

def looks_like_author_block(text):
    """
    Identifica un bloc care seamana cu o lista de autori.

    Exemple acceptate:

    C. Achiroaei1,2, Diana-Ioana Panaite1,2, C. Volovăț1,2

    Claudiu Daha, Ciprian Cirimbei, Şerban Marinescu

    Regula este intentionat conservatoare.
    """

    if not text:
        return False

    text = clean_text(text)

    # -----------------------------------------------------
    # Autorii sunt de obicei separati prin virgule.
    # -----------------------------------------------------

    parts = [
        clean_text(part)
        for part in text.split(",")
        if clean_text(part)
    ]

    if len(parts) < 2:
        return False

    # -----------------------------------------------------
    # Nu consideram continut lung drept lista de autori.
    # -----------------------------------------------------

    if len(text) > 300:
        return False

    # -----------------------------------------------------
    # Cuvinte care indica o afiliere/institutie.
    # -----------------------------------------------------

    institution_words = (
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
        "bucharest",
        "romania",
        "medical",
        "oncology",
    )

    lower_text = text.lower()

    if any(
        word in lower_text
        for word in institution_words
    ):
        return False

    # -----------------------------------------------------
    # Cel putin doua segmente trebuie sa semene cu nume.
    # -----------------------------------------------------

    name_like = 0

    for part in parts:

        part_without_numbers = re.sub(
            r"\d+(?:\s*,\s*\d+)*$",
            "",
            part
        ).strip()

        words = part_without_numbers.split()

        if len(words) >= 2:
            name_like += 1

    if name_like < 2:
        return False

    return True


# =========================================================
# CONTINUT
# =========================================================

def format_content(text):
    """
    Regula pentru continut:

    - text normal
    - fara bold
    - fara italic
    - fara superscript
    """

    if not text:
        return ""

    return (
        '<p class="simple-paragraph" '
        'style="font-weight: normal !important; '
        'font-style: normal !important;">'
        f"{escape_html(text)}"
        "</p>"
    )


# =========================================================
# BUILDER
# =========================================================

def build_simple_html(data):
    """
    Builder pentru articole simple.

    Pentru moment avem doar doua reguli:

    1. Autorii:
       - bold
       - numerele de afiliere superscript

    2. Continutul:
       - normal

    Restul elementelor sunt afisate fara stilizare.
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

    # -----------------------------------------------------
    # Pastram contextul pentru identificarea autorilor.
    # -----------------------------------------------------

    previous_elements = []

    for element in elements:

        if not isinstance(element, dict):
            continue

        tag = element.get(
            "tag",
            ""
        )

        text = element.get(
            "text",
            ""
        )

        if not text:
            continue

        text_clean = clean_text(text)

        if not text_clean:
            continue

        # =================================================
        # AUTORI
        # =================================================

        if looks_like_author_block(
            text_clean
        ):

            # Evitam sa tratam un paragraf normal,
            # mai ales daca este mai lung.
            if tag in (
                "H3",
                "H4",
                "H5",
                "P"
            ):

                html.append(
                    format_authors(
                        text_clean
                    )
                )

                previous_elements.append(
                    element
                )

                continue

        # =================================================
        # CONTINUT
        # =================================================

        if tag == "P":

            html.append(
                format_content(
                    text_clean
                )
            )

        # =================================================
        # RESTUL
        # =================================================

        else:

            html.append(
                escape_html(
                    text_clean
                )
            )

        previous_elements.append(
            element
        )

    html.append(
        "</div>"
    )

    return "\n".join(
        html
    )
