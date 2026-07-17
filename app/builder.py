# Updated builder.py
import re

def linkify(text):
    if not text: return ""
    return re.sub(r'(https?://[^\s]+|www\.[^\s]+)',
                  lambda m:f'<a href="{"https://"+m.group(0) if m.group(0).startswith("www.") else m.group(0)}" target="_blank">{m.group(0)}</a>',text)

def superscript_refs(text):
    if not text:return ""
    return re.sub(r'\((\d+(?:\s*,\s*\d+)*)\)',lambda m:f"<sup>{m.group(1).replace(', ',',').replace(',',', ')}</sup>",text)

def superscript_symbols(text):
    return text.replace("™","<sup>™</sup>").replace("®","<sup>®</sup>") if text else ""

def render_image(url):
    return f'<figure class="img-figure"><img src="{url}" class="article-image"/></figure>'

def format_content(text):

    if not text:
        return ""

    # elimină tagurile XML pe care nu vrem să le afișăm
    text = re.sub(r"</?(ContinutArticol|continut_articol|body)[^>]*>", "", text, flags=re.I)

    # elimină tabelele
    text = re.sub(r"<table.*?</table>", "", text, flags=re.I | re.S)

    # elimină figurile
    text = re.sub(r"<figure.*?</figure>", "", text, flags=re.I | re.S)

    # elimină orice tag imagine XML
    text = re.sub(r"<imagine\d+[^>]*\/?>", "", text, flags=re.I)

    text = text.replace("\u2029", "\n")

    # înlocuiește markerul de listă cu bullet HTML
text = re.sub(
    r"<Lbl>\s*.*?\s*</Lbl>",
    "&#8226; ",
    text,
    flags=re.I | re.S
)

    lines = [x.strip() for x in text.splitlines() if x.strip()]

    html = []

    for i, line in enumerate(lines):

        processed = linkify(line)
        processed = superscript_refs(processed)
        processed = superscript_symbols(processed)

        clean = re.sub(r"<[^>]+>", "", processed)
        words = len(clean.split())

        next_long = False
        if i + 1 < len(lines):
            next_long = len(lines[i + 1].split()) > 8

        # titluri de capitole/subcapitole
        if 1 <= words <= 8 and next_long:
            html.append(f"<p><strong>{processed}</strong></p>")
        else:
            html.append(f"<p>{processed}</p>")

    return "\n".join(html)

def format_bibliography(text):
    if not text:return ""
    html="<ol>"
    for r in [x.strip() for x in text.splitlines() if x.strip()]:
        html+=f"<li>{linkify(r)}</li>"
    return html+"</ol>"

def build_html(data):
    continut = format_content(data.get("continut_articol", ""))

    abstract = superscript_symbols(
        superscript_refs(
            linkify(data.get("abstract", ""))
        )
    )

    kwe = superscript_symbols(
        superscript_refs(
            linkify(data.get("keywords_eng", ""))
        )
    )

    rez = superscript_symbols(
        superscript_refs(
            linkify(data.get("rezumat", ""))
        )
    )

    kwr = superscript_symbols(
        superscript_refs(
            linkify(data.get("keywords_rom", ""))
        )
    )

    return f"""<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="utf-8">
<title>{data.get('titlu','Articol')}</title>
</head>

<body>

<h1>{data.get('titlu','')}</h1>
<h2>{data.get('english_title','')}</h2>

<div><b>Autori:</b> {data.get('autor','')}</div>

<div>{data.get('corespondent','')}</div>

<hr>

<h2>Abstract</h2>
<p><i>{abstract}</i></p>

<p>{kwe}</p>

<h2>Rezumat</h2>
<p><i>{rez}</i></p>

<p>{kwr}</p>

<h2>Conținut articol</h2>

{continut}

<h2>Bibliografie</h2>

{format_bibliography(data.get('bibliografie',''))}

</body>
</html>"""
