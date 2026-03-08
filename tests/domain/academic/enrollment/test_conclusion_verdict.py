import pytest

from domain.academic.enrollment.errors.enrollment_errors import DomainError
from domain.academic.enrollment.value_objects.conclusion_verdict import ConclusionVerdict


def test_allowed_verdict_is_created_with_default_values():
    verdict = ConclusionVerdict.allowed()

    assert verdict.is_allowed is True
    assert verdict.reasons == ()
    assert verdict.requires_justification is False


def test_allowed_verdict_accepts_requires_justification_true():
    verdict = ConclusionVerdict.allowed(requires_justification=True)

    assert verdict.is_allowed is True
    assert verdict.reasons == ()
    assert verdict.requires_justification is True


def test_allowed_verdict_cannot_contain_reasons():
    with pytest.raises(DomainError) as exc_info:
        ConclusionVerdict(
            is_allowed=True,
            reasons=("insufficient attendance",),
            requires_justification=False,
    )

    assert exc_info.value.code == "invalid_verdict_state"
    assert exc_info.value.message == "Allowed verdict cannot contain reasons."
    details = exc_info.value.details
    assert details is not None
    assert details["reasons"] == ("insufficient attendance",)


def test_denied_verdict_cannot_require_justification():
    with pytest.raises(DomainError) as exc_info:
        ConclusionVerdict(
            is_allowed=False,
            reasons=("academic failure",),
            requires_justification=True,
        )

    assert exc_info.value.code == "invalid_verdict_state"
    assert exc_info.value.message == "Denied verdict cannot require justification."
    details = exc_info.value.details
    assert details is not None
    assert details["requires_justification"] is True


def test_denied_verdict_must_contain_at_least_one_reason():
    with pytest.raises(DomainError) as exc_info:
        ConclusionVerdict.denied([])

    assert exc_info.value.code == "invalid_verdict_state"
    assert exc_info.value.message == "Denied verdict must contain at least one reason."
    details = exc_info.value.details
    assert details is not None
    assert details["reasons"] == ()


def test_denied_verdict_is_created_with_expected_values():
    verdict = ConclusionVerdict.denied(["low performance", "attendance below minimum"])

    assert verdict.is_allowed is False
    assert verdict.reasons == ("low performance", "attendance below minimum")
    assert verdict.requires_justification is False


def test_denied_factory_defensively_copies_reasons():
    reasons = ["low performance"]

    verdict = ConclusionVerdict.denied(reasons)
    reasons.append("attendance below minimum")

    assert verdict.reasons == ("low performance",)


def test_constructor_normalizes_list_reasons_to_tuple():
    verdict = ConclusionVerdict(
        is_allowed=False,
        reasons=["reason 1", "reason 2"],
        requires_justification=False,
    )

    assert isinstance(verdict.reasons, tuple)
    assert verdict.reasons == ("reason 1", "reason 2")
