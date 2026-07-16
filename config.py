import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
EXTRACT_FOLDER = os.path.join(BASE_DIR, "extracted")
PROCESSED_FOLDER = os.path.join(BASE_DIR, "processed")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "output")
DATABASE_FOLDER = os.path.join(BASE_DIR, "database")

ALLOWED_EXTENSIONS = {"zip"}

MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB
