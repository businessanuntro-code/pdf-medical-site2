# Updated builder.py
import re

def linkify(text):

    if not text:
        return ""


    # protejeaza tagurile HTML existente
    protected = []


    def protect(match):

        protected.append(match.group(0))

        return f"___HTML_{len(protected)-1}___"



    text = re.sub(
        r"<[^>]+>",
        protect,
        text
    )



    # transforma doar URL-urile din text normal

    text = re.sub(
        r'(https?://[^\s]+|www\.[^\s]+)',
        lambda m:
            f'<a href="{"https://"+m.group(0) if m.group(0).startswith("www.") else m.group(0)}" target="_blank">{m.group(0)}</a>',
        text
    )



    # pune tagurile HTML inapoi

    for i, tag in enumerate(protected):

        text = text.replace(
            f"___HTML_{i}___",
            tag
        )


    return text

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
    text = re.sub(
        r"<table.*?</table>",
        "",
        text,
        flags=re.I | re.S
    )

    # elimină figurile
    text = re.sub(
        r"<figure.*?</figure>",
        "",
        text,
        flags=re.I | re.S
    )

    # elimină orice tag imagine XML
    text = re.sub(
        r"<imagine\d+[^>]*\/?>",
        "",
        text,
        flags=re.I
    )

    text = text.replace("\u2029", "\n")

    # =====================================================
    # LISTE (<LI><Lbl>...</Lbl><LBody>...</LBody></LI>)
    # FARA BOLD AUTOMAT
    # =====================================================

    text = re.sub(
        r"<LI>\s*<Lbl>.*?</Lbl>\s*<LBody>(.*?)</LBody>\s*</LI>",
        r"\n__LBODY__&#8226; \1\n",
        text,
        flags=re.I | re.S
    )

    # =====================================================
    # INTERTITLU -> BOLD
    # =====================================================

    text = re.sub(
        r"<Intertitlu>(.*?)</Intertitlu>",
        r"\n<strong>\1</strong>\n",
        text,
        flags=re.I | re.S
    )

    # =====================================================
    # SUB_INTERTITLU -> BOLD + ITALIC
    # =====================================================

    text = re.sub(
        r"<Sub_Intertitlu>(.*?)</Sub_Intertitlu>",
        r"\n<strong><i>\1</i></strong>\n",
        text,
        flags=re.I | re.S
    )

    # =====================================================
    # INTER_STYLE_3 -> BOLD + ITALIC
    # =====================================================

    text = re.sub(
        r"<INTER_Style_3>(.*?)</INTER_Style_3>",
        r"\n<strong><i>\1</i></strong>\n",
        text,
        flags=re.I | re.S
    )

    # =====================================================
    # SEPARARE IN RANDURI
    # =====================================================

    lines = [
        x.strip()
        for x in text.splitlines()
        if x.strip()
    ]

    html = []

    # =====================================================
    # PROCESARE RANDURI
    # =====================================================

    for i, line in enumerate(lines):

        # verificăm dacă provine din LBody
        is_lbody = line.startswith("__LBODY__")

        if is_lbody:
            line = line.replace(
                "__LBODY__",
                "",
                1
            )

        # linkuri
        processed = linkify(line)

        # referinte intre paranteze -> superscript
        processed = superscript_refs(processed)

        # simboluri
        processed = superscript_symbols(processed)

        # text curat pentru numararea cuvintelor
        clean = re.sub(
            r"<[^>]+>",
            "",
            processed
        )

        words = len(clean.split())

        # verificam daca urmatorul paragraf este lung
        next_long = False

        if i + 1 < len(lines):

            next_clean = re.sub(
                r"<[^>]+>",
                "",
                lines[i + 1].replace(
                    "__LBODY__",
                    ""
                )
            )

            next_long = (
                len(next_clean.split()) > 8
            )

        # =================================================
        # LISTA
        # =================================================

        if is_lbody:

            html.append(
                f"<p>{processed}</p>"
            )

        # =================================================
        # TITLU / INTERTITLU AUTOMAT
        # =================================================

        elif 1 <= words <= 8 and next_long:

            html.append(
                f"<p><strong>{processed}</strong></p>"
            )

        # =================================================
        # PARAGRAF NORMAL
        # =================================================

        else:

            html.append(
                f"<p>{processed}</p>"
            )

    return "\n".join(html)

def format_bibliography(text):
    if not text:return ""
    html="<ol>"
    for r in [x.strip() for x in text.splitlines() if x.strip()]:
        html+=f"<li>{linkify(r)}</li>"
    return html+"</ol>"

def build_html(data):

    # =====================================
    # Compatibilitate:
    # XML import vechi + editare DB noua
    # =====================================

    titlu_ro = data.get(
        "titlu_ro",
        data.get("titlu", "")
    )

    titlu_en = data.get(
        "titlu_en",
        data.get("english_title", "")
    )

    autori = data.get(
        "autori",
        data.get("autor", "")
    )

    continut_text = data.get(
        "continut",
        data.get("continut_articol", "")
    )


    continut = format_content(continut_text)



    abstract = superscript_symbols(
        superscript_refs(
            linkify(data.get("abstract", ""))
        )
    )



    keywords = data.get(
        "keywords",
        data.get("keywords_eng", "")
    )


    kwe = superscript_symbols(
        superscript_refs(
            linkify(keywords)
        )
    )



    rez = superscript_symbols(
        superscript_refs(
            linkify(data.get("rezumat", ""))
        )
    )



    cuvinte_cheie = data.get(
        "cuvinte_cheie",
        data.get("keywords_rom", "")
    )


    kwr = superscript_symbols(
        superscript_refs(
            linkify(cuvinte_cheie)
        )
    )



    autor_corespondent = data.get(
        "autor_corespondent",
        data.get("corespondent", "")
    )



    suport = data.get(
        "suport",
        data.get("financial_support", "")
    )



    licenta = data.get(
        "licenta_cc_by",
        data.get("cc_by", "")
    )

    # =====================================
    # Normalizare Primit / Acceptat
    # Pentru afisare ca la Autori:
    # DB = doar data
    # HTML = Primit: data
    # =====================================

    primit = data.get("primit", "")

    if primit.lower().startswith("primit:"):
        primit = primit.split(":", 1)[1].strip()


    acceptat = data.get("acceptat", "")

    if acceptat.lower().startswith("acceptat:"):
        acceptat = acceptat.split(":", 1)[1].strip()

    return f"""<!DOCTYPE html>
<html lang="ro">

<head>

<meta charset="utf-8">

<title>{titlu_ro}</title>

<link rel="stylesheet" href="/static/style.css">

</head>


<body>


<h1>{titlu_ro}</h1>


<h2>{titlu_en}</h2>



<div>
<b>Autori:</b>
{superscript_author_refs(autori)}
</div>



<div>
Data publicării: {data.get('data_publicarii','')}
</div>



<div>
Primit: {primit}
</div>


<div>
Acceptat: {acceptat}
</div>


<div>
Editorial Group: {data.get('editorial_grup','')}
</div>



<div>
DOI: {data.get('doi','')}
</div>



<div>
Descarcă PDF:
<a href="{data.get('descarca_pdf','')}" target="_blank">
Click aici!
</a>
</div>



<hr>



<h2>Abstract</h2>

<p>
<i>{abstract}</i>
</p>



<p>
{kwe}
</p>




<h2>Rezumat</h2>


<p>
<i>{rez}</i>
</p>



<p>
{kwr}
</p>




<h2>Conținut articol</h2>


{continut}




<p>
<b>
{autor_corespondent}
</b>
</p>



<p>
<b>
{data.get('conflict','')}
</b>
</p>



<p>
<b>
{suport}
</b>
</p>



<p>
{licenta}
</p>



<img 
src="https://www.medichub.ro/upload/photos/sigla_cc_by_25101.png"
style="max-width:220px;">




<h2>Bibliografie</h2>


{format_bibliography(data.get('bibliografie',''))}



</body>

</html>"""

# =====================================================
# ARTICOL SIMPLU
# =====================================================

def superscript_simple_author_refs(text):

    if not text:
        return ""

    # Protejam tagurile HTML/XML
    protected = []

    def protect(match):
        protected.append(match.group(0))
        return f"___AUTHOR_HTML_{len(protected) - 1}___"

    text = re.sub(
        r"<[^>]+>",
        protect,
        text
    )

    # Autor + numar:
    # Popescu1 -> Popescu<sup>1</sup>
    # Ionescu2 -> Ionescu<sup>2</sup>
    # Popescu1,2 -> Popescu<sup>1,2</sup>
    text = re.sub(
        r"(?<=[A-Za-zĂÂÎȘȚăâîșț\-])(\d+(?:,\d+)*)",
        r"<sup>\1</sup>",
        text
    )

    # Punem tagurile inapoi
    for i, tag in enumerate(protected):

        text = text.replace(
            f"___AUTHOR_HTML_{i}___",
            tag
        )

    return text

def build_simple_html(data):

    titlu = data.get("titlu", "").strip()

    continut_text = data.get(
        "continut_articol",
        ""
    )

    continut_text = superscript_simple_author_refs(
    continut_text
)

continut = format_content(
    continut_text
)

    # Aplicam linkify si pentru titlu
    titlu_html = superscript_symbols(
        linkify(titlu)
    )

    return f"""<!DOCTYPE html>
<html lang="ro">

<head>

    <meta charset="UTF-8">

    <title>{titlu}</title>

    <style>

        body {{
            font-family: Arial, Helvetica, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 40px auto;
            padding: 0 20px;
            color: #222;
        }}

        h1 {{
            font-size: 28px;
            line-height: 1.3;
            margin-bottom: 30px;
        }}

        p {{
            margin-bottom: 15px;
        }}

        a {{
            color: #0066cc;
        }}

    </style>

</head>

<body>

    <h1>{titlu_html}</h1>

    <div class="continut-articol">

        {continut}

    </div>

</body>

</html>"""
