import pytest

from backend.services.metadata_service import MetadataService


def test_feature_enabled_without_repository_returns_false():
    service = MetadataService()

    assert service.feature_enabled() is False


def test_get_metadata_without_repository_returns_empty_list():
    service = MetadataService()

    assert service.get_metadata("documento", 1) == []


def test_get_tags_without_repository_returns_empty_list():
    service = MetadataService()

    assert service.get_tags("documento", 1) == []


def test_validate_entity_accepts_valid_input():
    service = MetadataService()

    assert service.validate_entity("documento", 1) is True


@pytest.mark.parametrize(
    ("entity_type", "entity_id"),
    [
        ("", 1),
        ("documento", ""),
        (None, 1),
        ("documento", None),
    ],
)
def test_validate_entity_rejects_invalid_input(entity_type, entity_id):
    service = MetadataService()

    with pytest.raises(ValueError):
        service.validate_entity(entity_type, entity_id)
