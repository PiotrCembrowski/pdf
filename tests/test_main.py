from fastapi.testclient import TestClient

from app.main import _clean_cell, app, infer_document_type

client = TestClient(app)


def test_index_page_available():
    response = client.get("/")
    assert response.status_code == 200
    assert "PDF Table Extractor" in response.text


def test_index_html_page_available():
    response = client.get("/index.html")
    assert response.status_code == 200
    assert "Extract JSON" in response.text


def test_clean_cell():
    assert _clean_cell(None) == ""
    assert _clean_cell("  hello ") == "hello"


def test_infer_document_type_variants():
    assert infer_document_type("INVOICE #123\nBill To: ACME") == "invoice"
    assert infer_document_type("Store RECEIPT\nSubtotal") == "receipt"
    assert infer_document_type("Quarterly KPI Report") == "report"
<<<<<<< ours
<<<<<<< HEAD
    assert infer_document_type("random text") == "unknown"
=======
    assert infer_document_type("random text") == "unknown"
>>>>>>> origin/codex/add-pdf-table-extractor-feature
=======
    assert infer_document_type("random text") == "unknown"
>>>>>>> theirs
