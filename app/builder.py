# Updated builder.py
import re

def linkify(text):
    if not text: return ""
    return re.sub(r'(https?://[^\s]+|www\.[^\s]+)',
                  lambda m:f'<a href="{"https://"+m.group(0) if m.group(0).startswith("www.") else m.group(0)}" target="_blank">{m.group(0)}</a>',text)

def superscript_refs(text):
    if not text:
        return ""

    def convert(match):
        return f"<sup>{match.group(0)}</sup>"

    return re.sub(
        r'\(\d+(?:\s*,\s*\d+)*\)',
        convert,
        text
    )

# Adauga superscript zona de Autori
def superscript_author_refs(text):
    if not text:
        return ""

    return re.sub(
        r'(?<=[A-Za-zĂÂÎȘȚăâîșț\-])(\d+(?:,\d+)*)',
        r'<sup>\1</sup>',
        text
    )


# Adauga superscript simboluri
def superscript_symbols(text):
    return text.replace("™","<sup>™</sup>").replace("®","<sup>®</sup>") if text else ""

def render_image(url):
    return f'<figure class="img-figure"><img src="{url}" class="article-image"/></figure>'

def format_content(text):

    if not text:
        return ""

    # elimină tagurile XML pe care nu vrem să le afișăm
    text = re.sub(
        r"</?(ContinutArticol|continut_articol|body)[^>]*>",
        "",
        text,
        flags=re.I
    )

    # elimină tabelele
    text = re.sub(r"<table.*?</table>", "", text, flags=re.I | re.S)

    # elimină figurile
    text = re.sub(r"<figure.*?</figure>", "", text, flags=re.I | re.S)

    # elimină orice tag imagine XML
    text = re.sub(r"<imagine\d+[^>]*\/?>", "", text, flags=re.I)

    text = text.replace("\u2029", "\n")

    # ==========================
    # LISTE (<LBody>) - FARA BOLD
    # ==========================
    text = re.sub(
        r"<LI>\s*<Lbl>.*?</Lbl>\s*<LBody>(.*?)</LBody>\s*</LI>",
        r"\n__LBODY__&#8226; \1\n",
        text,
        flags=re.I | re.S
    )

    # Intertitlu -> bold
    text = re.sub(
        r"<Intertitlu>(.*?)</Intertitlu>",
        r"\n<strong>\1</strong>\n",
        text,
        flags=re.I | re.S
    )

    # Sub_Intertitlu -> bold + italic
    text = re.sub(
        r"<Sub_Intertitlu>(.*?)</Sub_Intertitlu>",
        r"\n<strong><i>\1</i></strong>\n",
        text,
        flags=re.I | re.S
    )

    # INTER_Style_3 -> bold + italic
    text = re.sub(
    r"<INTER_Style_3>(.*?)</INTER_Style_3>",
    r"\n<strong><i>\1</i></strong>\n",
    text,
    flags=re.I | re.S
    )

    lines = [x.strip() for x in text.splitlines() if x.strip()]

    html = []

    for i, line in enumerate(lines):

        # verificăm dacă provine din LBody
        is_lbody = line.startswith("__LBODY__")
        if is_lbody:
            line = line.replace("__LBODY__", "", 1)

        processed = linkify(line)
        processed = superscript_refs(processed)
        processed = superscript_symbols(processed)

        clean = re.sub(r"<[^>]+>", "", processed)
        words = len(clean.split())

        next_long = False
        if i + 1 < len(lines):
            next_clean = re.sub(r"<[^>]+>", "", lines[i + 1].replace("__LBODY__", ""))
            next_long = len(next_clean.split()) > 8

        # dacă vine din LBody NU îi aplicăm bold automat
        if is_lbody:
            html.append(f"<p>{processed}</p>")

        elif 1 <= words <= 8 and next_long:
            html.append(f"<p><strong>{processed}</strong></p>")

        else:
            html.append(f"<p>{processed}</p>")

    return "\n".join(html)

    

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

    print(data["bibliografie"])
    return f"""<!DOCTYPE html>
<html lang="ro">

<head>
<meta charset="utf-8">
<title>{data.get('titlu','Articol')}</title>
<link rel="stylesheet" href="/static/style.css">
</head>

<body>

<h1>{data.get('titlu','')}</h1>
<h2>{data.get('english_title','')}</h2>

<div><b>Autori:</b> {superscript_author_refs(data.get("autor", ""))}</div>

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
