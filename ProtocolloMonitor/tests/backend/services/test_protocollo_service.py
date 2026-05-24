from backend.services.protocollo_service import ProtocolloService


class FakeProtocolloRepository:
    def list_protocolli(self):
        return [
            {
                "id_protocollo": 1,
                "numero_protocollo": "123",
                "stato_pratica": "NUOVA",
            }
        ]


def test_list_protocolli_without_repository_returns_empty_list():
    service = ProtocolloService()

    assert service.list_protocolli() == []


def test_list_protocolli_delegates_to_repository():
    service = ProtocolloService(
        protocollo_repository=FakeProtocolloRepository()
    )

    assert service.list_protocolli() == [
        {
            "id_protocollo": 1,
            "numero_protocollo": "123",
            "stato_pratica": "NUOVA",
        }
    ]


def test_get_protocollo_detail_without_repository_returns_safe_fallback():
    service = ProtocolloService()

    assert service.get_protocollo_detail(999) == {
        "protocollo": None,
        "assegnazioni": [],
        "destinatari": [],
        "firmatari": [],
    }
