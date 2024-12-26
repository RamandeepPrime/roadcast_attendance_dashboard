from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.database.enums import AttendanceStatus
from app.utils.logging_config import logger

from app.database.custom_errors import DataInjectionError, DatabaseErrors
from app.database.database import Attendance


async def insert_attendance_db(
    session: AsyncSession,
    roster_shift_id: int,
    attendance_date: date,
    image_path: str,
    timestamp: datetime,
    status: AttendanceStatus = AttendanceStatus.ABSENT
):
    
    new_attendance = {
        "roster_shift_id": roster_shift_id,
        "attendance_date": attendance_date,
        "image_path": image_path,
        "timestamp": timestamp,
        "status": status
    }

    try:
        statement = insert(Attendance).values(**new_attendance)

        # statement = statement.on_conflict_do_update(
        #     constraint="unique_assignment_editor_update",
        #     set_ = {
        #         Attendance.checkout_time: statement.excluded.checkout_time,
        #         Attendance.status: AttendanceStatus.PRESENT
        #     },
        # ).returning(Attendance)
        statement = statement.on_conflict_do_nothing()
        await session.execute(statement)
        
    
    except DatabaseErrors:
        logger.error(
            "Failed to insert attendance record for shift ID: %s", roster_shift_id, exc_info=True
        )
        raise DatabaseErrors(message="Database operation failed")
    
    except Exception:
        logger.error(
            "Unexpected error while inserting attendance record for shift ID: %s", roster_shift_id, exc_info=True
        )
        raise DataInjectionError(message="Failed to insert attendance. Please try again.")