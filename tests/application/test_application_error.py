from application.academic.enrollment.dto.errors.application_error import ApplicationError
from application.academic.enrollment.dto.errors.error_codes import ErrorCodes


def test_application_error_str_returns_code_and_message():
    error = ApplicationError(
        code=ErrorCodes.UNEXPECTED_ERROR,
        message="db down",
        details={"aggregate_id": "enr-1"},
    )

    assert str(error) == "ErrorCodes.UNEXPECTED_ERROR: db down"
