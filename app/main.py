import os
import uuid

from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Body
from fastapi.responses import JSONResponse

from app.parser import parse_xml
from app.builder import build_html
from app.api_client import publish_article


# =========================================================
# ARTICOLE SIMPLE
# =========================================================

from app.simple_main import router as simple_router


app = FastAPI()


# =========================================================
# ROUTER - ARTICOLE SIMPLE
# =========================================================

app.include_router(simple_router)


templates = Jinja2Templates(directory="templates")


UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"


os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# =========================================================
# STATIC FILES
# =========================================================

app.mount(
    "/static",
    StaticFiles(directory="uploads"),
    name="static"
)


# =========================================================
# HOME PAGE
# =========================================================

@app.get(
    "/",
    response_class=HTMLResponse
)
def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )


# =========================================================
# UPLOAD XML
# =========================================================

@app.post("/upload/")
async def upload(file: UploadFile):

    try:

        # =================================================
        # ID UNIC
        # =================================================

        file_id = str(
            uuid.uuid4()
        )


        # =================================================
        # 1. SALVARE XML
        # =================================================

        xml_path = (
            f"{UPLOAD_DIR}/{file_id}.xml"
        )


        content = await file.read()


        with open(
            xml_path,
            "wb"
        ) as f:

            f.write(content)


        # =================================================
        # 2. PARSE XML
        # =================================================

        data = parse_xml(
            xml_path
        )


        # =================================================
        # 3. GENERARE HTML
        # =================================================

        html = build_html(
            data
        )


        # =================================================
        # 4. ADAUGARE HTML IN DATA
        # =================================================

        data["continut_html"] = html


        # =================================================
        # 5. PUBLICARE ARTICOL
        # =================================================

        publish_article(
            data
        )


        # =================================================
        # 6. SALVARE HTML LOCAL
        # =================================================

        html_path = (
            f"{OUTPUT_DIR}/{file_id}.html"
        )


        with open(
            html_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(html)


        # =================================================
        # 7. RASPUNS JSON
        #
        # NU MAI FACEM REDIRECT
        # CATRE /article/{file_id}
        # =================================================

        return JSONResponse(
            {
                "success": True,
                "file_id": file_id,
                "message": "Articol procesat cu succes."
            }
        )


    except Exception as e:

        # =================================================
        # EROARE
        # =================================================

        return JSONResponse(
            {
                "success": False,
                "message": str(e)
            },
            status_code=500
        )


# =========================================================
# ARTICLE PAGE
#
# RAMANE NEMODIFICATA
# =========================================================

@app.get(
    "/article/{file_id}",
    response_class=HTMLResponse
)
def article(file_id: str):

    path = (
        f"{OUTPUT_DIR}/{file_id}.html"
    )


    if not os.path.exists(path):

        return HTMLResponse(
            "<h1>Article not found</h1>",
            status_code=404
        )


    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return HTMLResponse(
            f.read()
        )


# =========================================================
# REGENERATE
#
# RAMANE NEMODIFICAT
# =========================================================

@app.post("/regenerate")
async def regenerate(
    data: dict = Body(...)
):

    html = build_html(
        data
    )


    return JSONResponse(
        {

            "success": True,

            "continut_html": html

        }
    )
