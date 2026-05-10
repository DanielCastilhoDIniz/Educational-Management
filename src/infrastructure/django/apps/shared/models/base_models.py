from django.db import models
from django.utils import timezone


class CreatedAtModel(models.Model):
    """
    Base mínima para auditoria técnica de criação.
    - created_at: preenchido automaticamente na criação (UTC, timezone-aware)
    - imutável na prática (não editável via forms/admin)
    """
    created_at = models.DateTimeField(
        db_column="created_at",
        verbose_name="Created At",
        help_text="The date and time when the record was created (UTC).",
        default=timezone.now,
        editable=False,
    )

    class Meta:
        abstract = True


class MutableSnapshotModel(models.Model):
    """
    Base para tabelas de snapshot (mutáveis) que precisam:
    - updated_at: última atualização técnica do snapshot (UTC)
    - version: controle otimista de concorrência (incremento controlado no repository)
    """
    updated_at = models.DateTimeField(
        db_column="updated_at",
        verbose_name="Updated At",
        help_text="The date and time when the record was last updated (UTC).",
        default=timezone.now,
        editable=False,
    )

    version = models.PositiveIntegerField(
        db_column="version",
        verbose_name="Version",
        help_text="Optimistic concurrency version. Increment on each real update.",
        default=1,
        editable=False,
    )

    class Meta:
        abstract = True
