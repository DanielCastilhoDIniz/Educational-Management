import uuid

from django.db import models

from apps.shared.models.base_models import (
    CreatedAtModel,
    MutableSnapshotModel,
)


class UserModel(CreatedAtModel, MutableSnapshotModel):
    """
    Data model to represent a user in the identity system. 
    This model is designed to be a faithful representation of the user aggregate,
    allowing for the persistence and retrieval of the user state.
    """

    class StateChoices(models.TextChoices):
        PENDING = "pending", "pending"
        ACTIVE = "active", "active"
        SUSPENDED = "suspended", "suspended"
        INACTIVE = "inactive", "inactive"

    objects: models.Manager["UserModel"]  # type: ignore[override]

    id = models.UUIDField(
        primary_key=True,
        editable=False,
        help_text="Domain identifier (UUID).",
        default=uuid.uuid4,
        verbose_name="ID",
    )

    identity_type = models.CharField(
        max_length=50,
        verbose_name="Identity Type",
        help_text="The type of identity (e.g., student, teacher, admin).",
    )

    identity_number = models.CharField(
        max_length=50,
        verbose_name="Identity Number",
        help_text="The number of the identity (e.g., student ID, employee ID).",
    )

    identity_issuer = models.CharField(
        max_length=255,
        verbose_name="Identity Issuer",
        help_text="The issuer of the identity (e.g., institution name).",
    )


    full_name = models.CharField(
        max_length=255,
        verbose_name="Full Name",
        help_text="The full name of the user.",
    )

    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        verbose_name="Email",
        help_text="The email address of the user.",
    )

    birth_date = models.DateField(
        verbose_name="Birth Date",
        help_text="The birth date of the user.",
    )

    guardian_id = models.UUIDField(
        null=True,
        blank=True,
        verbose_name="Guardian ID",
        help_text="The unique identifier of the guardian (if applicable).",
    )
    

    state = models.CharField(
        max_length=20,
        choices=StateChoices.choices,
        verbose_name="State",
        help_text="The state of the user.",
    )

    created_by = models.CharField(
        max_length=255,
        verbose_name="Created By",
        help_text="The user who created this user record.",
    )

    activated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Activated At",
        help_text="When this user record was activated (UTC).", 
    )

    suspended_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Suspended At",
        help_text="When this user record was suspended (UTC).",
    )
    inactivated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Inactivated At",
        help_text="When this user record was inactivated (UTC).",
    )
    unlocked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Unlocked At",
        help_text="When this user record was unlocked (UTC).",
    )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        constraints = [
            models.UniqueConstraint(
                fields=["identity_type", "identity_number"],
                name="unique_identity",
            ),
        ]