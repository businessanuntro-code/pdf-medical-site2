from fastapi import APIRouter, UploadFile
from fastapi.responses import RedirectResponse

import os
import uuid

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
# HTML
#
# =========================================================

@router.post("/upload-simple/")
async def upload_simple(file: UploadFile):

    # -----------------------------------------------------
    # 1. Generare ID unic
    # -----------------------------------------------------

    file_id = str(uuid.uuid4())

    # -----------------------------------------------------
    # 2. Salvare HTML
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
    # 6. Redirect catre articol
    # -----------------------------------------------------

    return RedirectResponse(
        url=f"/article/{file_id}",
        status_code=302
    )
