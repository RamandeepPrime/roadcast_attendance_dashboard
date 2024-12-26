import datetime
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Date, Time, Enum, TIMESTAMP, ARRAY, Text, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

from app.database.enums import AttendanceStatus, Role, Weekday

Base = declarative_base()

# Tables
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    email_id = Column(String, unique=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    role = Column(Enum(Role), nullable=False)
    # is_verified = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow())
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())


class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    day = Column(Enum(Weekday), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    __table_args__ = (
        UniqueConstraint(
            day, start_time, end_time, name="unique_shifts_constraint"
        ),
    )


class Roster(Base):
    __tablename__ = "rosters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    manager_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow())
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())

    manager = relationship("User")


class RosterMember(Base):
    __tablename__ = "roster_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    roster_id = Column(Integer, ForeignKey("rosters.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique = True)
    # off_days = Column(ARRAY(Enum(Weekday)), nullable=True)

    roster = relationship("Roster")
    user = relationship("User")
    

class RosterMemberOffDay(Base):
    __tablename__ = "roster_member_off_days"

    id = Column(Integer, primary_key=True, autoincrement=True)
    roster_member_id = Column(Integer, ForeignKey("roster_members.id", ondelete="CASCADE"), nullable=False)
    off_day = Column(Enum(Weekday), nullable=False)

class RosterShift(Base):
    __tablename__ = "roster_shifts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    roster_member_id = Column(Integer, ForeignKey("roster_members.id", ondelete="CASCADE"), nullable=False)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)

    roster_member = relationship("RosterMember")
    shift = relationship("Shift")
    
    __table_args__ = (
        UniqueConstraint(
            roster_member_id, shift_id, name="unique_roster_shift"
        ),
    )


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    roster_shift_id = Column(Integer, ForeignKey("roster_shifts.id", ondelete="CASCADE"), nullable=False)
    attendance_date = Column(Date, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=True)
    image_path = Column(Text, nullable=False)
    status = Column(Enum(AttendanceStatus), default=AttendanceStatus.ABSENT)

    shift = relationship("RosterShift")
    
    __table_args__ = (
        UniqueConstraint(
            roster_shift_id, attendance_date, name="unique_roster_shift_attendance"
        ),
    )