import uuid

from django.db import models
from django.utils import timezone

from apps.shared.models.base_models import CreatedAtModel


class UserTransitionModel(CreatedAtModel):
    """Registro imutável de transição de estado do aggregate User.
    - id: PK UUID (decisão arquitetural)
    - state: estado atual (valores controlados)
    - timestamps de ciclo de vida: activated_at/suspended_at/inactivated_at
    """
    objects: models.Manager["UserTransitionModel"]  # type: ignore[override] 

    class StateChoices(models.TextChoices):
        PENDING = "pending", "pending"
        ACTIVE = "active", "active"
        SUSPENDED = "suspended", "suspended"
        INACTIVE = "inactive", "inactive"
    
    class ActionChoices(models.TextChoices):
        ACTIVATE = "activate", "activate"
        SUSPEND = "suspend", "suspend"
        INACTIVATE = "inactivate", "inactivate"
        UNLOCK = "unlock", "unlock"

    transition_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name="Transition ID",
        help_text="Unique identifier for the state transition (UUID).",
    )

    user = models.ForeignKey(
        "UserModel",
        on_delete=models.PROTECT,
        verbose_name="User ID",
        help_text="The user associated with this state transition.",
        related_name="transitions"
    )

    occurred_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Occurred At",
        help_text="When the transition occurred (UTC).",
    )

    action = models.CharField(
        max_length=20,
        choices=ActionChoices.choices,
        verbose_name="Action",
        help_text="The action that triggered the state transition.",
    )

    from_state = models.CharField(
        max_length=20,
        choices=StateChoices.choices,
        verbose_name="From State",
        help_text="The state from which the transition occurred.",
    )
    to_state = models.CharField(
        max_length=20,
        choices=StateChoices.choices,
        verbose_name="To State",
        help_text="The state to which the transition was applied.",
    )
    justification = models.TextField(
        null=True,
        blank=True,
        verbose_name="Justification",
        help_text="Optional justification for the state transition.",
    )
    actor_id = models.UUIDField(
        verbose_name="Actor ID",
        help_text="The unique identifier of the actor (e.g., user) who performed the transition.",
    )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        db_table = "user_transitions"
        indexes = [
            models.Index(fields=["user", "occurred_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(from_state=models.F("to_state")),
                name="ck_user_transition_from_state_diff_to_state",
            ),
        ]