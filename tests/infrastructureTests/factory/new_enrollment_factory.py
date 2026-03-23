import uuid
from datetime import UTC, datetime

from apps.academic.models.enrollment_model import EnrollmentModel


def factory_create_new_enrrolment_for_tests(
        enrollment_id: uuid.UUID | None = None,
        student_id: uuid.UUID | None = None,
        class_group_id: uuid.UUID | None = None,
        academic_period_id: uuid.UUID | None = None ,
        created_at: datetime | None = None,
        state: str = "active",
        ):

        if enrollment_id is None:
            enrollment_id = uuid.uuid4()
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
            "student_id": student_id,
            "class_group_id": class_group_id,
            "academic_period_id": academic_period_id,
            "created_at": created_at,
            "state": state,
        }
        
        return EnrollmentModel.objects.create(**enrollment)
 