import uuid
from datetime import UTC, datetime

from apps.academic.models.enrollment_model import EnrollmentModel


def factory_create_new_enrollment_for_tests(
        enrollment_id: uuid.UUID | None = None,
        institution_id: uuid.UUID | None = None,
        student_id: uuid.UUID | None = None,
        class_group_id: uuid.UUID | None = None,
        academic_period_id: uuid.UUID | None = None,
        created_by: str = "test_factory",
        created_at: datetime | None = None,
        cancelled_at: datetime | None = None,
        concluded_at: datetime | None = None,
        suspended_at: datetime | None = None,
        state: str = "active",
        ):

        if enrollment_id is None:
            enrollment_id = uuid.uuid4()
        if institution_id is None:
            institution_id = uuid.uuid4()
        if student_id is None:
            student_id = uuid.uuid4()
        if class_group_id is None:
            class_group_id = uuid.uuid4()
        if academic_period_id is None:
            academic_period_id = uuid.uuid4()
        if created_at is None:
            created_at = datetime.now(UTC)
        
        enrollment = {
            "id": enrollment_id,
            "institution_id": institution_id,
            "student_id": student_id,
            "class_group_id": class_group_id,
            "academic_period_id": academic_period_id,
            "created_by": created_by,
            "created_at": created_at,
            "cancelled_at": cancelled_at,
            "concluded_at": concluded_at,
            "suspended_at": suspended_at,
            "state": state,
        }
        
        return EnrollmentModel.objects.create(**enrollment)
 