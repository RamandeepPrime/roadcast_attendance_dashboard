
import os
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.file_upload import save_image
from app.database import get_db_instance
from app.database.custom_errors import InvalidDataError
from app.database.database import Shift, User
from app.database.enums import AttendanceStatus, Role, Weekday
from app.database.queries.attendance import insert_attendance_db
from app.database.queries.shifts import get_allocated_shifts_db
from app.utils.custom_errors import PermissionDeniedError
from app.utils.error_handlers import ErrorHandlingLoggingRoute
from app.utils.jwt_helper import get_current_user

router = APIRouter(route_class = ErrorHandlingLoggingRoute)

@router.post("/mark")
async def mark_attendance(
    day: Weekday = Form(...),
    image: UploadFile = Form(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_instance)
):
    """
        Assumptions:
            User can only take attendance one time and we are storing only timestamp for that

        Potential Solutions    
            Not storing chheckin and checkout time.
            We can run cronjob for every day for marking member absent / present based on shift timing (8-9 hrs)
                Also include half day as a status in attendance
            We can check if image captured is actually belongs to the user or not  

    """
    if user.role != Role.STAFF:
        raise PermissionDeniedError

    shifts = await get_allocated_shifts_db(
        session = session,
        email_id = user.email_id,
        additional_filters = (
            Shift.day == day,
        )
    )

    if not shifts:
        raise InvalidDataError("Shift not found or not assigned to the user.")
    
    shift_data = shifts[0]

    current_time = datetime.now()
    start_time = datetime.combine(current_time.date(), shift_data.start_time)
    if not start_time + timedelta(hours=1) <= current_time <= start_time - timedelta(hours=1):
        raise InvalidDataError("Attendance can only be marked within 1 hour of the shift timing.")
    
    image_path = await save_image(
        image = image, 
        image_base_path = os.path.join(
            "attendance", 
            str(current_time.year), 
            str(current_time.month), 
            str(current_time.day), 
            user.email_id
        )
    )

    "check for 8 hr attendance"
    await insert_attendance_db(
        session = session,
        roster_shift_id = shift_data.roster_shift_id,
        attendance_date = current_time.date(),
        image_path = image_path,
        timestamp = current_time,
        status = AttendanceStatus.PRESENT 
    )
    
    await session.commit()
    # cronjob for marking them as present
    return {
        "success": True,
        "message": "Attendance marked successfully"
    }