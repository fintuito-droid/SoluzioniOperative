import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = PROJECT_ROOT / "Python"

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

import server_protocollo


class FakePdfDocumentService:
    def __init__(self, *, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    def save_and_register_protocollo_pdf(
        self,
        id_protocollo,
        pdf_bytes,
        modalita,
        comando,
        numero_protocollo,
        data_protocollo,
    ):
        self.calls.append(
            {
                "id_protocollo": id_protocollo,
                "pdf_bytes": pdf_bytes,
                "modalita": modalita,
                "comando": comando,
                "numero_protocollo": numero_protocollo,
                "data_protocollo": data_protocollo,
            }
        )

        if self.error is not None:
            raise self.error

        return self.result


def test_salva_pdf_protocollo_con_service_success(monkeypatch, tmp_path):
    monkeypatch.setattr(server_protocollo, "FILE_LOG", tmp_path / "log.txt")
    expected = {
        "saved": True,
        "registered": True,
        "id_protocollo": 123,
        "path": "FileServer/2026/05/E_DIR-SIC_18177_20260510.pdf",
        "filename": "E_DIR-SIC_18177_20260510.pdf",
    }
    fake_service = FakePdfDocumentService(result=expected)

    result = server_protocollo.salva_pdf_protocollo_con_service(
        123,
        b"%PDF-test",
        "Entrata",
        "DIR-SIC",
        "18177",
        "10/05/2026",
        pdf_document_service=fake_service,
    )

    assert result == expected
    assert fake_service.calls == [
        {
            "id_protocollo": 123,
            "pdf_bytes": b"%PDF-test",
            "modalita": "Entrata",
            "comando": "DIR-SIC",
            "numero_protocollo": "18177",
            "data_protocollo": "10/05/2026",
        }
    ]
    assert "PDF salvato e path registrato" in (tmp_path / "log.txt").read_text(
        encoding="utf-8"
    )


def test_salva_pdf_protocollo_con_service_handles_exception(monkeypatch, tmp_path):
    monkeypatch.setattr(server_protocollo, "FILE_LOG", tmp_path / "log.txt")
    fake_service = FakePdfDocumentService(error=RuntimeError("errore test"))

    result = server_protocollo.salva_pdf_protocollo_con_service(
        999,
        b"%PDF-test",
        "Uscita",
        "DIR-SIC",
        "18164",
        "10/05/2026",
        pdf_document_service=fake_service,
    )

    assert result == {
        "saved": False,
        "registered": False,
        "id_protocollo": 999,
        "path": None,
        "filename": None,
        "error": "errore test",
    }
    assert "errore nel wrapper preparatorio" in (tmp_path / "log.txt").read_text(
        encoding="utf-8"
    )
