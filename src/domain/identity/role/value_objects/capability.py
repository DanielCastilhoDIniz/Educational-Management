from enum import StrEnum


class Capability(StrEnum):

    # Identity and access
    USER_CREATE = "user:create"
    USER_ACTIVATE = "user:activate"
    USER_CLOSE = "user:close"
    USER_SUSPEND = "user:suspend"
    USER_UNLOCK = "user:unlock"
  
    # Institutional Affiliations (MEMBERSHIP_*)
    MEMBERSHIP_CREATE = "membership:create"
    MEMBERSHIP_ACTIVATE = "membership:activate"
    MEMBERSHIP_SUSPEND = "membership:suspend"
    MEMBERSHIP_CLOSE = "membership:close"	

    # Organizational Structure (INSTITUTION_*, NETWORK_STRUCTURE_*)
    INSTITUTION_CREATE = "institution:create"
    INSTITUTION_CONFIGURE = "institution:configure"
    NETWORK_STRUCTURE_CREATE = "network_structure:create"

    # People (STUDENT_*, TEACHER_CREATE, GUARDIAN_*)
    STUDENT_CREATE = "student:create"
    TEACHER_CREATE = "teacher:create"
    GUARDIAN_CREATE = "guardian:create"

    # Enrollments (ENROLLMENT_*)
    ENROLLMENT_CREATE = "enrollment:create"
    ENROLLMENT_CANCEL = "enrollment:cancel"
    ENROLLMENT_HISTORY_READ	= "enrollment_history:read"
    ENROLLMENT_READ = "enrollment:read"	
    ENROLLMENT_REACTIVATE =	"enrollment:reactivate"
    ENROLLMENT_SUSPEND = "enrollment:suspend"
  
    # Academic Structure (SCHOOL_YEAR_*, ​​CLASS_GROUP_*, TEACHER_ASSIGN)
    SCHOOL_YEAR_CREATE = "school_year:create"
    CLASS_GROUP_CREATE = "class_group:create"
    TEACHER_ASSIGN = "teacher:assign"

    # Pedagogical Operations (LESSON_*, ATTENDANCE_*, GRADE_*, PERIOD_*)
    LESSON_RECORD =	"lesson:record"
    ATTENDANCE_RECORD =	"attendance:record"
    GRADE_RECORD =	"grade:record"
    PERIOD_CLOSE =	"period:close"

    # Student Experience and Reports (GRADEBOOK_*, DASHBOARD_*, REPORT_*)
    GRADEBOOK_STUDENT_READ = "gradebook_student:read"
    DASHBOARD_STUDENT_READ = "dashboard_student:read"
    REPORT_OFFICIAL_ISSUE =	"report:official_issue"
    REPORT_READ	= "report:read"
    REPORT_EXPORT =	"report:export"




