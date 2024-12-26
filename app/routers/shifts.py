from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_instance
from app.database.database import User
from app.database.enums import Role
from app.database.queries.shifts import assign_shift_to_staff_db, create_shift_db, get_allocated_shifts_db, get_shift_details_db, swap_shifts_db
from app.database.queries.user import get_user_by_email_db
from app.routers.pydantics.shifts import AssignShiftsRequestModel, ShiftCreationRequestModel, SwapShiftsRequestModel
from app.utils.dependencies import UserValidator
from app.utils.error_handlers import ErrorHandlingLoggingRoute
from app.utils.jwt_helper import get_current_user


router = APIRouter(route_class = ErrorHandlingLoggingRoute)

@router.get('')
async def get_shits(
    session: AsyncSession = Depends(get_db_instance)
):
    shift_details = await get_shift_details_db(session = session)
    
    return {
        "success": True,
        "shift_ids": shift_details
    }

@router.post('')
async def create_shifts(
    request_data: ShiftCreationRequestModel,
    session: AsyncSession = Depends(get_db_instance)
):
    shift_id = await create_shift_db(
        session = session,
        day = request_data.day,
        start_time = request_data.start_time,
        end_time = request_data.end_time
    )
    await session.commit()
    return {
        "success": True,
        "shift_id": shift_id
    }

@router.get("/assign", dependencies = [Depends(UserValidator([Role.STAFF]))])
async def get_assigned_shifts(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_instance)
):
    
    assigned_shifts = await get_allocated_shifts_db(
        session = session,
        email_id = user.email_id
    )
    
    return {
        "success": True,
        "shifts": assigned_shifts
    }
    

@router.put('/assign', dependencies = [Depends(UserValidator([Role.MANAGER, Role.ADMIN]))])
async def assign_shifts(
    shift_details: AssignShiftsRequestModel,
    session: AsyncSession = Depends(get_db_instance)
):
    staff_member = await get_user_by_email_db(session = session, email_id = shift_details.email_id)
    await shift_details.validate_request(session = session, user = staff_member)

    await assign_shift_to_staff_db(
        session = session,
        roster_id = shift_details.roster_id,
        user_id = staff_member.id,
        shift_id = shift_details.shift_id,
    )
    await session.commit()
    return {
        "success": True,
        "message": "Shift assigned successfully"
    }

@router.put('/swap', dependencies = [Depends(UserValidator([Role.STAFF]))])
async def swap_shifts(
    shift_request: SwapShiftsRequestModel,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_instance)
):
    
    await shift_request.validate_request(session)
    user2 = await get_user_by_email_db(session = session, email_id = shift_request.email_id)
    user1_shifts, user2_shifts = await shift_request.validate_shifts(
        session = session, 
        user1_email_id = user.email_id, 
        user2_email_id = user2.email_id
    )
    

    await swap_shifts_db(
        session = session,
        user1_id = user.id,
        user2_id = user2.id,
        user1_shift_id = user1_shifts.id,
        user2_shift_id = user2_shifts.id,
        roster_id = shift_request.roster_id
    )

    await session.commit()
    
    return {
        "success": True,
        "message": "Shift ids successfully swapped"
    }