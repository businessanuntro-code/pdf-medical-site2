from fastapi import APIRouter, UploadFile
from fastapi.responses import RedirectResponse

import os
import uuid
import requests

from app.simple_parser import parse_simple_html
from app.simple_builder import build_simple_html


# =========================================================
# ROUTER - ARTICOLE SIMPLE
# =========================================================

router = APIRouter()


# =========================================================
# CONFIGURARE - ARTICOLE SIMPLE
# =========================================================

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================================================
# API - ARTICOLE SIMPLE
# =========================================================

SIMPLE_IMPORT_URL = (
    "https://diaconu-daniel.ro/api/simple/import/import.php"
)

SIMPLE_API_KEY = "MEDICHUB_SECRET_2026"


# =========================================================
# INJECTARE ARTICOL SIMPLU IN DB
# =========================================================

def publish_simple_article(html):

    data = {
        "continut_html": html
    }

    headers = {
        "X-API-Key": SIMPLE_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(
        SIMPLE_IMPORT_URL,
        json=data,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    
    print("===== SIMPLE API DEBUG =====")
    print("STATUS:", response.status_code)
    print("URL:", response.url)
    print("RESPONSE TEXT:")
    print(response.text)
    print("============================")

    raise Exception(
    f"DEBUG SIMPLE API | "
    f"STATUS={response.status_code} | "
    f"URL={response.url} | "
    f"RESPONSE={response.text[:3000]}"
    )


# =========================================================
# UPLOAD ARTICOL SIMPLU
# =========================================================
#
# Flux:
#
# HTML
# ↓
# simple_parser.py
# ↓
# simple_builder.py
# ↓
# HTML rezultat
# ↓
# api/simple/import/import.php
# ↓
# articole_simple
#
# =========================================================

@router.post("/upload-simple/")
async def upload_simple(file: UploadFile):

    # -----------------------------------------------------
    # 1. Generare ID unic
    # -----------------------------------------------------

    file_id = str(uuid.uuid4())


    # -----------------------------------------------------
    # 2. Salvare HTML original
    # -----------------------------------------------------

    html_path = f"{UPLOAD_DIR}/{file_id}.html"

    content = await file.read()

    with open(
        html_path,
        "wb"
    ) as f:

        f.write(content)


    # -----------------------------------------------------
    # 3. PARSER - ARTICOL SIMPLU
    # -----------------------------------------------------

    data = parse_simple_html(
        html_path
    )


    # -----------------------------------------------------
    # 4. BUILDER - ARTICOL SIMPLU
    # -----------------------------------------------------

    html = build_simple_html(
        data
    )


    # -----------------------------------------------------
    # 5. Salvare HTML rezultat
    # -----------------------------------------------------

    output_path = (
        f"{OUTPUT_DIR}/{file_id}.html"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(html)


    # -----------------------------------------------------
    # 6. INJECTARE IN DB
    # -----------------------------------------------------

    result = publish_simple_article(
        html
    )


    # -----------------------------------------------------
    # 7. Verificare raspuns API
    # -----------------------------------------------------

    if not result.get("success"):

        raise Exception(
            result.get(
                "message",
                "Articolul simplu nu a putut fi salvat."
            )
        )


    # -----------------------------------------------------
    # 8. ID ARTICOL DIN DB
    # -----------------------------------------------------

    article_id = result.get("id")


    # -----------------------------------------------------
    # 9. Redirect
    # -----------------------------------------------------

    return RedirectResponse(
        url=f"/article/{file_id}",
        status_code=302
    )
