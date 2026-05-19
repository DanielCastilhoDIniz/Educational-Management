from enum import StrEnum


class Capability(StrEnum):

    # Identity and access
    USER_CREATE = "user:create"
    USER_ACTIVATE = "user:activate"
    USER_SUSPEND = "user:suspend"
    USER_UNLOCK = "user:unlock"
    USER_CLOSE = "user:close"
    USER_READ = "user:read"

    MEMBERSHIP_CREATE = "membership:create"
    MEMBERSHIP_ACTIVATE = "membership:activate"
    MEMBERSHIP_SUSPEND = "membership:suspend"
    MEMBERSHIP_CLOSE = "membership:close"
    MEMBERSHIP_READ = "membership:read"
    MEMBERSHIP_ROLE_CHANGE = "membership:role_change"

    ROLE_READ = "role:read"
    ROLE_CREATE = "role:create"
    ROLE_ACTIVATE = "role:activate"
    ROLE_DEACTIVATE = "role:deactivate"

    # Organization
    INSTITUTION_CREATE = "institution:create"
    INSTITUTION_CONFIGURE = "institution:configure"
    INSTITUTION_READ = "institution:read"

    # Enrollment
    ENROLLMENT_CREATE = "enrollment:create"
    ENROLLMENT_READ = "enrollment:read"
    ENROLLMENT_LIST = "enrollment:list"
    ENROLLMENT_SUSPEND = "enrollment:suspend"
    ENROLLMENT_REACTIVATE = "enrollment:reactivate"
    ENROLLMENT_CANCEL = "enrollment:cancel"
    ENROLLMENT_CONCLUDE = "enrollment:conclude"

    # Academic structure and operation
    SCHOOL_YEAR_CREATE = "school_year:create"
    PERIOD_CLOSE = "period:close"
    CLASS_GROUP_CREATE = "class_group:create"
    TEACHER_ASSIGN = "teacher:assign"

    LESSON_RECORD = "lesson:record"
    LESSON_APPROVE = "lesson:approve"

    ATTENDANCE_RECORD = "attendance:record"
    ATTENDANCE_AUDIT = "attendance:audit"

    GRADE_RECORD = "grade:record"
    GRADE_AUDIT = "grade:audit"

    # Reporting and student experience
    REPORT_READ = "report:read"
    REPORT_EXPORT = "report:export"
    REPORT_OFFICIAL_ISSUE = "report:official_issue"

    DASHBOARD_STUDENT_READ = "dashboard_student:read"
    GRADEBOOK_STUDENT_READ = "gradebook_student:read"


