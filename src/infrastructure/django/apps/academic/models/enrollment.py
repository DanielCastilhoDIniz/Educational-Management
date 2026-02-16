from django.db import models

from .base_models import CreatedAtModel, MutableSnapshotModel
import uuid


class EnrollmentModel(CreatedAtModel, MutableSnapshotModel):
    """
        Log imutável (append-only) de transições do aggregate Enrollment.

        - transition_id: identificador único para deduplicação
        - occurred_at: timestamp do fato de domínio (UTC / tz-aware)
        - action: comando que disparou a transição (CONCLUDE/CANCEL/SUSPEND)
        - from_state/to_state: estados da transição
        - actor_id: quem executou (obrigatório; pode ser 'system' em jobs via convenção na aplicação)
    """

    class StateChoices(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        SUSPENDED = "SUSPENDED", "Suspended"
        CANCELLED = "CANCELLED", "Cancelled"
        CONCLUDED = "CONCLUDED", "Concluded"

    id = models.UUIDField(
        primary_key=True,
        editable=False,
        help_text="Domain identifier (UUID).",
        default=uuid.uuid4,
        verbose_name="ID",
    )

    student_id = models.UUIDField(
        verbose_name="Student ID",
        help_text="The unique identifier of the student.",
    )

    class_group_id = models.UUIDField(
        verbose_name="Class Group ID",
        help_text="The unique identifier of the class group.",
    )

    academic_period_id = models.UUIDField(
        verbose_name="Academic Period ID",
        help_text="The unique identifier of the academic period.",
    )

    state = models.CharField(
        max_length=20,
        choices=StateChoices.choices,
        verbose_name="State",
        help_text="The state of the enrollment.",
    )

    concluded_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Concluded At",
        help_text="When the enrollment was concluded (UTC).",
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Cancelled At",
        help_text="When the enrollment was cancelled (UTC).",
    )

    suspended_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Suspended At",
        help_text="When the enrollment was suspended (UTC).",
    )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        db_table = "enrollments"
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"
        indexes = [
            models.Index(fields=["student_id"]),
            models.Index(fields=["state"]),
        ]
