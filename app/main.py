import os
import uuid

from fastapi import FastAPI, UploadFile, Request, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# =========================================================

# IMPORTURI - ARTICOLE STIINTIFICE

# =========================================================

from app.parser import parse_xml
from app.builder import build_html
from app.api_client import publish_article

# =========================================================

# IMPORTURI - ARTICOLE SIMPLE

# =========================================================

from app.simple_parser import parse_simple_xml
from app.simple_builder import build_simple_html

# =========================================================

# CONFIGURARE APLICATIE

# =========================================================

app = FastAPI()

templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================================================

# STATIC FILES

# =========================================================

app.mount(
"/static",
StaticFiles(directory="uploads"),
name="static"
)

# =========================================================

# HOME PAGE - COMUN

# =========================================================

@app.get("/", response_class=HTMLResponse)
def home(request: Request):

```
return templates.TemplateResponse(
    "index.html",
    {"request": request}
)
```

# =========================================================

# =========================================================

# ARTICOLE STIINTIFICE

# =========================================================

# =========================================================

#

# Flux:

#

# XML

# ↓

# parser.py

# ↓

# builder.py

# ↓

# publish_article()

# ↓

# HTML

#

# Aceasta zona pastreaza fluxul existent.

# =========================================================

@app.post("/upload/")
async def upload(file: UploadFile):

```
file_id = str(uuid.uuid4())

# -----------------------------------------------------
# 1. Salvare XML
# -----------------------------------------------------

xml_path = f"{UPLOAD_DIR}/{file_id}.xml"

content = await file.read()

with open(xml_path, "wb") as f:
    f.write(content)

# -----------------------------------------------------
# 2. PARSER STIINTIFIC
# -----------------------------------------------------

data = parse_xml(xml_path)

# -----------------------------------------------------
# 3. BUILDER STIINTIFIC
# -----------------------------------------------------

html = build_html(data)

# -----------------------------------------------------
# 4. Adaugare HTML in dictionar
# -----------------------------------------------------

data["continut_html"] = html

# -----------------------------------------------------
# 5. Publicare articol in baza de date
# -----------------------------------------------------

publish_article(data)

# -----------------------------------------------------
# 6. Salvare HTML local
# -----------------------------------------------------

html_path = f"{OUTPUT_DIR}/{file_id}.html"

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

# -----------------------------------------------------
# 7. Redirect catre articol
# -----------------------------------------------------

return RedirectResponse(
    url=f"/article/{file_id}",
    status_code=302
)
```

# =========================================================

# =========================================================

# ARTICOLE SIMPLE

# =========================================================

# =========================================================

#

# Flux:

#

# XML

# ↓

# simple_parser.py

# ↓

# simple_builder.py

# ↓

# HTML

#

# IMPORTANT:

# Acest flux este separat de articolele stiintifice.

#

# Pentru moment NU trimitem articolul simplu in baza de date.

# Mai intai verificam si perfectionam HTML-ul generat.

# =========================================================

@app.post("/upload-simple/")
async def upload_simple(file: UploadFile):

```
file_id = str(uuid.uuid4())

# -----------------------------------------------------
# 1. Salvare XML
# -----------------------------------------------------

xml_path = f"{UPLOAD_DIR}/{file_id}.xml"

content = await file.read()

with open(xml_path, "wb") as f:
    f.write(content)

# -----------------------------------------------------
# 2. PARSER ARTICOL SIMPLU
# -----------------------------------------------------

data = parse_simple_xml(xml_path)

# -----------------------------------------------------
# 3. BUILDER ARTICOL SIMPLU
# -----------------------------------------------------

html = build_simple_html(data)

# -----------------------------------------------------
# 4. Adaugare HTML in dictionar
# -----------------------------------------------------

data["continut_html"] = html

# -----------------------------------------------------
# 5. PUBLICARE IN DB
#
# Momentan este dezactivata intentionat.
# -----------------------------------------------------

# publish_article(data)

# -----------------------------------------------------
# 6. Salvare HTML local
# -----------------------------------------------------

html_path = f"{OUTPUT_DIR}/{file_id}.html"

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

# -----------------------------------------------------
# 7. Redirect catre articol
# -----------------------------------------------------

return RedirectResponse(
    url=f"/article/{file_id}",
    status_code=302
)
```

# =========================================================

# =========================================================

# RUTE COMUNE

# =========================================================

# =========================================================

# ---------------------------------------------------------

# ARTICLE PAGE

# ---------------------------------------------------------

@app.get("/article/{file_id}", response_class=HTMLResponse)
def article(file_id: str):

```
path = f"{OUTPUT_DIR}/{file_id}.html"

if not os.path.exists(path):

    return HTMLResponse(
        "<h1>Article not found</h1>",
        status_code=404
    )

with open(path, "r", encoding="utf-8") as f:

    return HTMLResponse(
        f.read()
    )
```

# ---------------------------------------------------------

# REGENERATE

#

# IMPORTANT:

# Ramane pe builderul articolelor stiintifice.

# Nu modificam acest flux acum.

# ---------------------------------------------------------

@app.post("/regenerate")
async def regenerate(data: dict = Body(...)):

```
html = build_html(data)

return JSONResponse({

    "success": True,

    "continut_html": html

})
```
