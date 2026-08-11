import os
import uuid

from fastapi import FastAPI, UploadFile, Request, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


# =========================================================
# =========================================================
# IMPORTURI - ARTICOLE STIINTIFICE
# =========================================================
# =========================================================

from app.parser import parse_xml
from app.builder import build_html
from app.api_client import publish_article


# =========================================================
# =========================================================
# IMPORTURI - ARTICOLE SIMPLE
# =========================================================
# =========================================================

from app.simple_parser import parse_simple_xml
from app.simple_builder import build_simple_html


# =========================================================
# =========================================================
# CONFIGURARE APLICATIE
# =========================================================
# =========================================================

app = FastAPI()

templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================================================
# STATIC FILES - COMUN
# =========================================================

app.mount(
    "/static",
    StaticFiles(directory="uploads"),
    name="static"
)


# =========================================================
# =========================================================
# HOME PAGE - COMUN
# =========================================================
# =========================================================

@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


# =========================================================
# =========================================================
# ARTICOLE STIINTIFICE
# =========================================================
# =========================================================
#
# XML
#   ↓
# parser.py
#   ↓
# builder.py
#   ↓
# publish_article()
#   ↓
# HTML
#
# ACEASTA ZONA ESTE PENTRU ARTICOLELE STIINTIFICE.
#
# =========================================================

@app.post("/upload/")
async def upload(file: UploadFile):

    # -----------------------------------------------------
    # 1. Salvare XML
    # -----------------------------------------------------

    file_id = str(uuid.uuid4())

    xml_path = f"{UPLOAD_DIR}/{file_id}.xml"

    content = await file.read()

    with open(xml_path, "wb") as f:
        f.write(content)

    # -----------------------------------------------------
    # 2. PARSER - ARTICOL STIINTIFIC
    # -----------------------------------------------------

    data = parse_xml(xml_path)

    # -----------------------------------------------------
    # 3. BUILDER - ARTICOL STIINTIFIC
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


# =========================================================
# =========================================================
# ARTICOLE SIMPLE
# =========================================================
# =========================================================
#
# XML
#   ↓
# simple_parser.py
#   ↓
# simple_builder.py
#   ↓
# HTML
#
# ACEASTA ZONA ESTE COMPLET SEPARATA
# DE FLUXUL ARTICOLELOR STIINTIFICE.
#
# Momentan NU salvam articolul simplu in DB.
# Mai intai testam parserul si builderul.
#
# =========================================================

@app.post("/upload-simple/")
async def upload_simple(file: UploadFile):

    # -----------------------------------------------------
    # 1. Salvare XML
    # -----------------------------------------------------

    file_id = str(uuid.uuid4())

    xml_path = f"{UPLOAD_DIR}/{file_id}.xml"

    content = await file.read()

    with open(xml_path, "wb") as f:
        f.write(content)

    # -----------------------------------------------------
    # 2. PARSER - ARTICOL SIMPLU
    # -----------------------------------------------------

    data = parse_simple_xml(xml_path)

    # -----------------------------------------------------
    # 3. BUILDER - ARTICOL SIMPLU
    # -----------------------------------------------------

    html = build_simple_html(data)

    # -----------------------------------------------------
    # 4. Adaugare HTML in dictionar
    # -----------------------------------------------------

    data["continut_html"] = html

    # -----------------------------------------------------
    # 5. PUBLICARE IN DB
    #
    # DEZACTIVATA MOMENTAN.
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


# =========================================================
# =========================================================
# RUTE COMUNE
# =========================================================
# =========================================================


# =========================================================
# ARTICLE PAGE
# =========================================================

@app.get("/article/{file_id}", response_class=HTMLResponse)
def article(file_id: str):

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


# =========================================================
# REGENERATE - ARTICOLE STIINTIFICE
# =========================================================
#
# Ramane conectat la builder.py.
# Nu folosim simple_builder.py aici.
#
# =========================================================

@app.post("/regenerate")
async def regenerate(data: dict = Body(...)):

    html = build_html(data)

    return JSONResponse({
        "success": True,
        "continut_html": html
    })
