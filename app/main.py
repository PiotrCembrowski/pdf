from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any

import pdfplumber
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="PDF Table Extractor")
STATIC_DIR = Path(__file__).parent / "static"
STATIC_INDEX = STATIC_DIR / "index.html"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
@app.get("/index.html", include_in_schema=False)
def index() -> Response:
    if STATIC_INDEX.exists():
        return FileResponse(STATIC_INDEX)
    return HTMLResponse("<h1>PDF Table Extractor</h1><p>Frontend asset missing.</p>", status_code=500)


def _clean_cell(cell: Any) -> str:
    if cell is None:
        return ""
    return str(cell).strip()


def infer_document_type(text: str) -> str:
    normalized = text.lower()
    if any(token in normalized for token in ("invoice", "bill to", "invoice #", "due date")):
        return "invoice"
    if any(token in normalized for token in ("receipt", "subtotal", "cash", "change")):
        return "receipt"
    if any(token in normalized for token in ("report", "summary", "quarter", "kpi", "statement")):
        return "report"
    return "unknown"


@app.post("/api/extract")
async def extract_tables(file: UploadFile = File(...)) -> dict[str, Any]:
    if file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    pages_payload: list[dict[str, Any]] = []
    full_text: list[str] = []

    try:
        with pdfplumber.open(BytesIO(raw)) as pdf:
            for page_idx, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text() or ""
                full_text.append(page_text)
                raw_tables = page.extract_tables() or []

                parsed_tables: list[dict[str, Any]] = []
                for table_idx, table in enumerate(raw_tables, start=1):
                    clean_rows = [[_clean_cell(cell) for cell in row] for row in table if row]
                    if not clean_rows:
                        continue

                    headers = clean_rows[0]
                    rows = clean_rows[1:] if len(clean_rows) > 1 else []
                    parsed_tables.append(
                        {
                            "table_index": table_idx,
                            "headers": headers,
                            "rows": rows,
                            "row_count": len(rows),
                            "column_count": len(headers),
                        }
                    )

                pages_payload.append(
                    {
                        "page_number": page_idx,
                        "table_count": len(parsed_tables),
                        "tables": parsed_tables,
                    }
                )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Could not parse PDF: {exc}") from exc

    combined_text = "\n".join(full_text)
    total_tables = sum(page["table_count"] for page in pages_payload)

    return {
        "file_name": file.filename,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "document_type": infer_document_type(combined_text),
        "page_count": len(pages_payload),
        "table_count": total_tables,
        "pages": pages_payload,
    }