
class EnrollmentNotFoundError(Exception):
    """
    Raised when an Enrollment aggregate cannot be found
    during application service execution.
    """

    def __init__(self, enrollment_id: str):
        self.enrollment_id = enrollment_id
        super().__init__(f"Enrollment not found: {enrollment_id}")
