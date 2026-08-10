import os
import uuid

from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.parser import parse_xml, parse_simple_xml
from app.builder import build_html, build_simple_html
from app.api_client import publish_article

from fastapi import Body
from fastapi.responses import JSONResponse

app = FastAPI()

templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================
# STATIC FILES
# =========================
app.mount("/static", StaticFiles(directory="uploads"), name="static")


# =========================
# HOME PAGE
# =========================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


# =========================
# UPLOAD XML
# =========================
@app.post("/upload/")
async def upload(file: UploadFile):

    file_id = str(uuid.uuid4())

    # 1. Salvare XML
    xml_path = f"{UPLOAD_DIR}/{file_id}.xml"

    content = await file.read()

    with open(xml_path, "wb") as f:
        f.write(content)

    # 2. Parse XML
    data = parse_xml(xml_path)

    # 3. Generare HTML
    html = build_html(data)

    # 4. Adăugare HTML în dicționarul trimis către API
    data["continut_html"] = html

    # 5. Publicare articol în baza de date
    publish_article(data)

    # 6. Salvare HTML local
    html_path = f"{OUTPUT_DIR}/{file_id}.html"

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    # 7. Redirect către articol
    return RedirectResponse(
        url=f"/article/{file_id}",
        status_code=302
    )


# =========================
# UPLOAD XML - ARTICOL SIMPLU
# =========================

@app.post("/upload-simple/")
async def upload_simple(file: UploadFile):

    file_id = str(uuid.uuid4())

    # 1. Salvare XML
    xml_path = f"{UPLOAD_DIR}/{file_id}.xml"

    content = await file.read()

    with open(xml_path, "wb") as f:
        f.write(content)

    # 2. Parse XML simplu
    data = parse_simple_xml(xml_path)

    # 3. Generare HTML simplu
    html = build_simple_html(data)

    # 4. Salvare HTML local
    html_path = f"{OUTPUT_DIR}/{file_id}.html"

    with open(
        html_path,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(html)

    # 5. Redirect către articol
    return RedirectResponse(
        url=f"/article/{file_id}",
        status_code=302
    )

# =========================
# ARTICLE PAGE
# =========================
@app.get("/article/{file_id}", response_class=HTMLResponse)
def article(file_id: str):

    path = f"{OUTPUT_DIR}/{file_id}.html"

    if not os.path.exists(path):
        return HTMLResponse(
            "<h1>Article not found</h1>",
            status_code=404
        )

    with open(path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.post("/regenerate")
async def regenerate(data: dict = Body(...)):

    html = build_html(data)

    return JSONResponse({

        "success": True,

        "continut_html": html

    })
