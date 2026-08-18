# XML Publisher

## Flow

Upload XML
      │
      ▼
parser.py
(extrage toate câmpurile)
      │
      ▼
build_html()   (generează HTML-ul articolului)
      │
      ▼
INSERT în MySQL
      │
      ▼
primește ID-ul articolului
      │
      ▼
redirect:
/articol/123
      │
      ▼
SELECT * FROM articole WHERE id=123
      │
      ▼
afișează articolul din baza de date

## Run locally

uvicorn app.main:app --reload

## Open

http://127.0.0.1:8000
