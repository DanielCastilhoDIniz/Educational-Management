import pytest
from apps.academic.repositories.django_enrollment_repository import DjangoEnrollmentRepository

import uuid


@pytest.mark.django_db
def test_get_by_id_snapshot_is_none_when_enrollment_does_not_exist() -> None:
    repository = DjangoEnrollmentRepository()
    result = repository.get_by_id(str(uuid.uuid4()))
    assert result is None
