# PDF Table Extractor

Upload a PDF (invoices, receipts, reports) and get structured JSON containing extracted tables.

## Features

- FastAPI backend endpoint: `POST /api/extract`
- Simple frontend for file upload and JSON preview
- Basic document type inference (`invoice`, `receipt`, `report`, `unknown`)
- Page-by-page table extraction with headers and rows

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open: `http://localhost:8000`

## Example API usage

```bash
curl -X POST http://localhost:8000/api/extract \
  -F "file=@sample.pdf"
```

## Run tests

````bash
pytest -q
```# pdf
````
