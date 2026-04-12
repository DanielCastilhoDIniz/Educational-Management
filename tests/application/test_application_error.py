from application.academic.enrollment.dto.errors.application_error import ApplicationError
from application.shared.errors.error_codes import SharedErrorCodes


def test_application_error_str_returns_code_and_message():
    error = ApplicationError(
        code=SharedErrorCodes.UNEXPECTED_ERROR,
        message="db down",
        details={"aggregate_id": "enr-1"},
    )

    assert str(error) == "UNEXPECTED_ERROR: db down"
