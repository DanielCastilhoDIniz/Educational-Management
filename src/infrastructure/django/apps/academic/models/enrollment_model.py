import uuid

from django.db import models

from .base_models import CreatedAtModel, MutableSnapshotModel


class EnrollmentModel(CreatedAtModel, MutableSnapshotModel):
    """
    Data model to represent an enrollment in the academic system. 
    This model is designed to be a faithful representation of the enrollment aggregate,
    allowing for the persistence and retrieval of the enrollment state,
    as well as the tracking of its state transitions over time.
    """

    objects: models.Manager["EnrollmentModel"]  # type: ignore[override]

    class StateChoices(models.TextChoices):
        ACTIVE = "active", "active"
        SUSPENDED = "suspended", "suspended"
        CANCELLED = "cancelled", "cancelled"
        CONCLUDED = "concluded", "concluded"

    id = models.UUIDField(
        primary_key=True,
        editable=False,
        help_text="Domain identifier (UUID).",
        default=uuid.uuid4,
        verbose_name="ID",
    )
    institution_id = models.UUIDField(
        verbose_name="Institution ID",
        help_text="The unique identifier of the institution.",
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

    created_by = models.CharField(
        max_length=255,
        verbose_name="Created By",
        help_text="The user who created the enrollment.",
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

    reactivated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Reactivated At",
        help_text="When the enrollment was reactivated (UTC).",
    )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        db_table = "enrollments"
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"
        constraints = [
            models.UniqueConstraint(
                fields=["institution_id", "student_id", "class_group_id", "academic_period_id"],
                name="unique_enrollment"
            )
        ]
