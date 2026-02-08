from domain.academic.enrollment.errors.enrollment_errors import (
    DomainError
)


def test_domain_error_srt_representation():
    domain_error = DomainError(code="any_code", message="any message", details=None)

    text = str(domain_error)

    assert text == "any_code: any message"


def test_domain_error_repr_representation():
    domain_error = DomainError(code="x", message="y", details={"a": 1})

    text = repr(domain_error)

    assert text == "DomainError(code='x', message='y', details={'a': 1})"
