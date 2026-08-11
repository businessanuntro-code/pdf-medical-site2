import re
from html import escape

def clean_text(text):
"""Normalizeaza spatiile dintr-un text."""
if not text:
return ""

```
text = text.replace("\xa0", " ")
text = re.sub(r"\s+", " ", text)

return text.strip()
```

def escape_html(text):
"""Protejeaza textul pentru HTML."""
return escape(clean_text(text))

def format_author_numbers(text):
"""
Transforma numerele asociate autorilor in superscript.

```
Exemple:
    Autor1
    Autor1,2
    Autor1,2,3

Devine:
    Autor<sup>1</sup>
    Autor<sup>1,2</sup>
    Autor<sup>1,2,3</sup>

Regula se aplica DOAR in zona autorilor.
"""

if not text:
    return ""

text = escape_html(text)

# Grup de numere aflat imediat dupa numele autorului.
text = re.sub(
    r"(?<=[A-Za-zÀ-ÖØ-öø-ÿĂăÂâÎîȘșŞşȚțŢţ\-])"
    r"(\d+(?:\s*,\s*\d+)*)",
    lambda match: f"<sup>{match.group(1)}</sup>",
    text
)

return text
```

def format_authors(authors):
"""
Afiseaza autorii cu bold si numerele asociate in superscript.
"""

```
if not authors:
    return ""

formatted = format_author_numbers(authors)

return f'<div class="simple-authors"><strong>{formatted}</strong></div>'
```

def format_affiliations(affiliations):
"""
Formateaza afilierile.

```
Numerotarea este pornita de la 1 pentru fiecare articol.

Chiar daca XML-ul contine alte valori in Lbl,
builderul foloseste propria numerotare consecutiva.
"""

if not affiliations:
    return ""

html = ['<div class="simple-affiliations">']

for index, affiliation in enumerate(affiliations, start=1):

    text = affiliation.get("text", "")
    text = escape_html(text)

    if not text:
        continue

    html.append(
        f'<div class="simple-affiliation">'
        f'<span class="affiliation-number">{index}.</span> '
        f'{text}'
        f'</div>'
    )

html.append("</div>")

return "\n".join(html)
```

def format_keywords(keywords):
"""
Formateaza Keywords.

```
'Keywords:' este bold.
Se adauga spatiu/br dupa zona de keywords.
"""

if not keywords:
    return ""

keywords = escape_html(keywords)

return (
    '<p class="simple-keywords">'
    '<strong>Keywords:</strong> '
    f'{keywords}'
    '</p>'
    '<br>'
)
```

def format_paragraphs(paragraphs):
"""
Transforma paragrafele articolului in <p>.
"""

```
if not paragraphs:
    return ""

html = []

for paragraph in paragraphs:

    paragraph = clean_text(paragraph)

    if not paragraph:
        continue

    # Keywords nu trebuie sa ajunga aici.
    if re.match(
        r"^(?:Keywords|Cuvinte\s+cheie)\s*:",
        paragraph,
        flags=re.IGNORECASE
    ):
        continue

    html.append(
        f'<p class="simple-paragraph">{escape_html(paragraph)}</p>'
    )

return "\n".join(html)
```

def build_simple_article(article):
"""
Construieste HTML-ul pentru un singur articol simplu.
"""

```
if not article:
    return ""

title_en = clean_text(article.get("title_en", ""))
title_ro = clean_text(article.get("title_ro", ""))

authors = article.get("authors", "")
affiliations = article.get("affiliations", [])
paragraphs = article.get("paragraphs", [])
keywords = article.get("keywords", "")

html = []

html.append('<article class="simple-article">')

# ---------------------------------------------------------
# TITLU EN
# ---------------------------------------------------------

if title_en:
    html.append(
        f'<h4 class="simple-title-en">'
        f'{escape_html(title_en)}'
        f'</h4>'
    )

# ---------------------------------------------------------
# TITLU RO
# ---------------------------------------------------------

if title_ro:
    html.append(
        f'<h4 class="simple-title-ro">'
        f'{escape_html(title_ro)}'
        f'</h4>'
    )

# ---------------------------------------------------------
# AUTORI
# ---------------------------------------------------------

if authors:
    html.append(format_authors(authors))

# ---------------------------------------------------------
# AFILIERI
# ---------------------------------------------------------

if affiliations:
    html.append(format_affiliations(affiliations))

# ---------------------------------------------------------
# CONTINUT
# ---------------------------------------------------------

content_html = format_paragraphs(paragraphs)

if content_html:
    html.append(content_html)

# ---------------------------------------------------------
# KEYWORDS
# ---------------------------------------------------------

keywords_html = format_keywords(keywords)

if keywords_html:
    html.append(keywords_html)

html.append("</article>")

return "\n".join(html)
```

def build_simple_html(data):
"""
Builder principal pentru articole simple.

```
NU foloseste build_html() din builder.py.
NU foloseste functiile pentru articole stiintifice.

Proceseaza exclusiv datele produse de simple_parser.py.
"""

if not data:
    return ""

articles = data.get("articles", [])

if not articles:
    # Compatibilitate cu eventuale date simple
    # care contin un singur articol.
    articles = [data]

html = []

html.append('<div class="simple-articles">')

for article in articles:

    article_html = build_simple_article(article)

    if not article_html:
        continue

    html.append(article_html)

html.append("</div>")

return "\n".join(html)
```
