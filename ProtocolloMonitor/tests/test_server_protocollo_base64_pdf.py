import base64
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = PROJECT_ROOT / "Python"

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

import server_protocollo


class FakeStorageService:
    def __init__(self, root):
        self.root = Path(root)
        self.saved_files = []

    def build_storage_dir(self, data_protocollo):
        return self.root / data_protocollo.strftime("%Y") / data_protocollo.strftime("%m")

    def build_filename(self, modalita, comando, numero_protocollo, data_protocollo):
        tipo = "E" if "ENTRATA" in str(modalita).upper() else "U"
        return (
            f"{tipo}_{comando}_{numero_protocollo}_"
            f"{data_protocollo.strftime('%Y%m%d')}.pdf"
        )

    def save_pdf(self, pdf_bytes, modalita, comando, numero_protocollo, data_protocollo):
        storage_dir = self.build_storage_dir(data_protocollo)
        filename = self.build_filename(
            modalita,
            comando,
            numero_protocollo,
            data_protocollo,
        )
        target = storage_dir / filename
        storage_dir.mkdir(parents=True, exist_ok=True)
        target.write_bytes(pdf_bytes)
        self.saved_files.append(target)
        return target


def test_estrai_pdf_protocollato_base64_returns_valid_bytes():
    payload = {
        "DocumentoProtocollatoBase64": base64.b64encode(b"%PDF-test").decode(
            "ascii"
        )
    }

    result = server_protocollo.estrai_pdf_protocollato_base64(payload)

    assert result == b"%PDF-test"


def test_estrai_pdf_protocollato_base64_returns_none_when_missing():
    assert server_protocollo.estrai_pdf_protocollato_base64({}) is None


def test_costruisci_metadati_pdf_protocollo_returns_expected_values():
    dati = {
        "modalita": "Entrata",
        "numero_protocollo": "18177",
        "data_protocollo": "10/05/2026",
    }

    result = server_protocollo.costruisci_metadati_pdf_protocollo(dati)

    assert result["modalita"] == "Entrata"
    assert result["comando"] == "DIR-SIC"
    assert result["numero_protocollo"] == "18177"
    assert result["data_protocollo"] == "10/05/2026"
    assert result["data_protocollo_storage"].strftime("%Y%m%d") == "20260510"


def test_costruisci_metadati_pdf_protocollo_uses_comando_mittente():
    dati = {
        "modalita": "Entrata",
        "comando_mittente": "COM-PA",
        "ComandoMittente": "COM-TP",
        "comando": "COM-NA",
        "numero_protocollo": "18177",
        "data_protocollo": "10/05/2026",
    }

    result = server_protocollo.costruisci_metadati_pdf_protocollo(dati)

    assert result["comando"] == "COM-PA"


def test_costruisci_metadati_pdf_protocollo_uses_ComandoMittente_second():
    dati = {
        "modalita": "Entrata",
        "ComandoMittente": "COM-TP",
        "comando": "COM-NA",
        "numero_protocollo": "18177",
        "data_protocollo": "10/05/2026",
    }

    result = server_protocollo.costruisci_metadati_pdf_protocollo(dati)

    assert result["comando"] == "COM-TP"


def test_costruisci_metadati_pdf_protocollo_uses_comando_third():
    dati = {
        "modalita": "Entrata",
        "comando": "COM-NA",
        "numero_protocollo": "18177",
        "data_protocollo": "10/05/2026",
    }

    result = server_protocollo.costruisci_metadati_pdf_protocollo(dati)

    assert result["comando"] == "COM-NA"


def test_costruisci_metadati_pdf_protocollo_uses_default_comando():
    dati = {
        "modalita": "Entrata",
        "numero_protocollo": "18177",
        "data_protocollo": "10/05/2026",
    }

    result = server_protocollo.costruisci_metadati_pdf_protocollo(dati)

    assert result["comando"] == "DIR-SIC"


def test_costruisci_metadati_pdf_protocollo_sanitizes_comando():
    dati = {
        "modalita": "Entrata",
        "comando_mittente": "COM:PA",
        "numero_protocollo": "18177",
        "data_protocollo": "10/05/2026",
    }

    result = server_protocollo.costruisci_metadati_pdf_protocollo(dati)

    assert result["comando"] == "COM_PA"


def test_salva_documento_protocollato_base64_saves_once_and_updates_data(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(server_protocollo, "FILE_LOG", tmp_path / "log.txt")
    storage_service = FakeStorageService(tmp_path)
    payload = {
        "DocumentoProtocollatoBase64": base64.b64encode(b"%PDF-test").decode(
            "ascii"
        )
    }
    dati = {
        "modalita": "Entrata",
        "numero_protocollo": "18177",
        "data_protocollo": "10/05/2026",
    }

    first_path = server_protocollo.salva_documento_protocollato_base64(
        payload,
        dati,
        storage_service=storage_service,
    )
    second_path = server_protocollo.salva_documento_protocollato_base64(
        payload,
        dati,
        storage_service=storage_service,
    )

    expected_path = tmp_path / "2026" / "05" / "E_DIR-SIC_18177_20260510.pdf"

    assert first_path == str(expected_path)
    assert second_path == str(expected_path)
    assert expected_path.read_bytes() == b"%PDF-test"
    assert dati["percorsoDocumentoProtocollato"] == str(expected_path)
    assert storage_service.saved_files == [expected_path]


def test_salva_documento_protocollato_base64_returns_none_when_base64_missing(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(server_protocollo, "FILE_LOG", tmp_path / "log.txt")
    storage_service = FakeStorageService(tmp_path)
    dati = {
        "modalita": "Entrata",
        "numero_protocollo": "18177",
        "data_protocollo": "10/05/2026",
    }

    result = server_protocollo.salva_documento_protocollato_base64(
        {},
        dati,
        storage_service=storage_service,
    )

    assert result is None
    assert "percorsoDocumentoProtocollato" not in dati
    assert storage_service.saved_files == []
