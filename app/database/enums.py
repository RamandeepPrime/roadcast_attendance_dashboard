import enum

class Role(enum.Enum):
    MANAGER = "Manager"
    STAFF = "Staff"
    ADMIN = "Admin"

class Weekday(enum.Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"

class AttendanceStatus(enum.Enum):
    PRESENT = "Present"
    ABSENT = "Absent"