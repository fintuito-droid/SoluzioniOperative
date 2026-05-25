from datetime import date, datetime

from backend.services.document_storage_service import DocumentStorageService


def test_save_pdf_creates_year_month_directory_and_writes_bytes(tmp_path):
    service = DocumentStorageService(file_server_root=tmp_path)

    saved_path = service.save_pdf(
        b"%PDF-test",
        "Entrata",
        "DIR-SIC",
        "18177",
        "10/05/2026",
    )

    assert saved_path == tmp_path / "2026" / "05" / "E_DIR-SIC_18177_20260510.pdf"
    assert saved_path.read_bytes() == b"%PDF-test"


def test_build_filename_for_entrata_and_uscita(tmp_path):
    service = DocumentStorageService(file_server_root=tmp_path)

    assert (
        service.build_filename("Entrata", "DIR-SIC", "18177", "10/05/2026")
        == "E_DIR-SIC_18177_20260510.pdf"
    )
    assert (
        service.build_filename("Uscita", "DIR-SIC", "18164", "10/05/2026")
        == "U_DIR-SIC_18164_20260510.pdf"
    )


def test_build_filename_fallback_values(tmp_path):
    service = DocumentStorageService(file_server_root=tmp_path)

    assert (
        service.build_filename("Interno", "", "", "")
        == "X_ND_SENZAPROT_00000000.pdf"
    )


def test_build_filename_sanitizes_windows_invalid_characters(tmp_path):
    service = DocumentStorageService(file_server_root=tmp_path)

    assert (
        service.build_filename("Entrata", 'DIR:/SIC*?', '18<177>|"', "10/05/2026")
        == "E_DIR__SIC_18_177_20260510.pdf"
    )


def test_build_filename_accepts_date_and_datetime(tmp_path):
    service = DocumentStorageService(file_server_root=tmp_path)

    assert (
        service.build_filename("Entrata", "DIR-SIC", "1", date(2026, 5, 10))
        == "E_DIR-SIC_1_20260510.pdf"
    )
    assert (
        service.build_filename(
            "Entrata",
            "DIR-SIC",
            "1",
            datetime(2026, 5, 10, 12, 30),
        )
        == "E_DIR-SIC_1_20260510.pdf"
    )


def test_build_storage_dir_uses_zero_folder_for_invalid_date(tmp_path):
    service = DocumentStorageService(file_server_root=tmp_path)

    assert service.build_storage_dir("non valida") == tmp_path / "0000" / "00"


def test_document_exists_supports_absolute_and_relative_paths(tmp_path):
    service = DocumentStorageService(file_server_root=tmp_path)
    saved_path = tmp_path / "2026" / "05" / "sample.pdf"
    saved_path.parent.mkdir(parents=True)
    saved_path.write_bytes(b"pdf")

    assert service.document_exists(saved_path) is True
    assert service.document_exists("2026/05/sample.pdf") is True
    assert service.document_exists("2026/05/missing.pdf") is False
