from typing import Dict, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import delete, exists, func, select, and_
from app.database.custom_errors import DataExtractionError, DataInjectionError, DatabaseErrors, InvalidDataError, ItemNotFound
from app.database.database import RosterMember, RosterMemberOffDay, RosterShift, Shift, User
from app.database.enums import Weekday
from app.database.queries.roster import get_roster_member_id_db
from app.utils.custom_errors import PermissionDeniedError
from app.utils.logging_config import logger
from sqlalchemy.orm import Bundle


# Function to get all shifts and their details
async def get_shift_details_db(
    session: AsyncSession,
    shift_id: int = None
) -> List[Shift]:
    filters= []
    
    if shift_id:
        filters.append(Shift.id == shift_id)
    
    statement = select(Shift)
    if filters:
        statement = statement.where(*filters)
    try:
        result = await session.execute(statement)
        shifts = result.scalars().all()
        if not shifts:
            logger.warning("No shifts found in the database.")
            return []
        return shifts
    except DatabaseErrors:
        logger.error("Database error occurred while fetching all shifts.", exc_info=True)
        raise
    except Exception:
        logger.error("Unexpected error occurred while fetching all shifts.", exc_info=True)
        raise DataExtractionError(message="Failed to retrieve shifts. Please try again.")

async def get_allocated_shifts_db(
    session: AsyncSession,
    email_id: str,
    additional_filters: Tuple = None
):
    filters = []
    statement = select(
        Shift.id,
        RosterShift.id.label("roster_shift_id"),
        Shift.day,
        Shift.start_time,
        Shift.end_time,
    ).select_from(
        Shift
    ).join(
        RosterShift,
        RosterShift.shift_id == Shift.id
    ).join(
        RosterMember,
        RosterMember.id == RosterShift.roster_member_id
    ).join(
        User,
        User.id == RosterMember.user_id
    ).where(
        User.email_id == email_id
    )

    if additional_filters:
        filters.extend(additional_filters)

    if filters:
        statement = statement.where(*filters)

    try:
        result = await session.execute(statement)
        shifts = result.fetchall()
        if not shifts:
            logger.warning("No shifts found in the database.")
            return []
        return shifts
    except DatabaseErrors:
        logger.error("Database error occurred while fetching assigned shifts.", exc_info=True)
        raise
    except Exception:
        logger.error("Unexpected error occurred while fetching assigned shifts.", exc_info=True)
        raise DataExtractionError(message="Failed to retrieve shifts. Please try again.")
    
async def check_shift_exists_db(
    session: AsyncSession,
    shift_id: int,
):
    statement = select(exists().where(Shift.id == shift_id))
    data = await session.execute(statement)
    return data

async def get_users_off_days_db(
    session: AsyncSession,
    roster_id: int,
    user_id: int,
) -> List[Weekday]:
    statement = select(
        RosterMemberOffDay.off_day.label('off_days')
    ).select_from(
        User
    ).join(
        RosterMember,
        and_(
            RosterMember.user_id == user_id,
            RosterMember.roster_id == roster_id
        )
    ).join(
        RosterMemberOffDay,
        RosterMemberOffDay.roster_member_id == RosterMember.id
    )
    try:
        data = await session.execute(statement)
        return data.scalars().all()
    except DatabaseErrors:
        logger.error("Database error occurred while fetching off days.", exc_info=True)
        raise
    except Exception:
        logger.error("Unexpected error occurred while fetching off days.", exc_info=True)
        raise DataExtractionError(message="Failed to retrieve off days. Please try again.")
    

async def assign_shift_to_staff_db(
    session: AsyncSession,
    roster_id: int,
    user_id: int,
    shift_id: int,
):

    # Check if the roster member exists
    roster_member_id = await get_roster_member_id_db(session = session, roster_id = roster_id, user_id = user_id)
    if roster_member_id is None:
        logger.warning("Roster member with not found.")
        raise ItemNotFound("User is not a part of this roster.")

    # TODO check for user_off_day and try to assign shift 
    off_days = await get_users_off_days_db(session = session, roster_id = roster_id, user_id = user_id)
    shift_details = await get_shift_details_db(session = session, shift_id = shift_id)

    if shift_details[0].day in off_days:
        raise InvalidDataError("You can't assign shift for user off days")

    # Assign the shift
    statement = insert(RosterShift).values(roster_member_id=roster_member_id, shift_id=shift_id)
    statement = statement.on_conflict_do_update(
        constraint="unique_roster_shift",
        set_ = {
            RosterShift.shift_id: statement.excluded.shift_id
        },
    )
    try:
        await session.execute(statement)
        logger.info(f"Shift ID {shift_id} successfully assigned to roster member ID {roster_member_id}.")
    
    except DatabaseErrors:
        logger.error("Database error occurred while assigning a shift.", exc_info=True)
        raise
    except Exception:
        logger.error("Unexpected error occurred while assigning a shift.", exc_info=True)
        raise DataInjectionError(message="Failed to assign shift. Please try again.")
    

async def swap_shifts_db(
    session: AsyncSession,
    user1_id: int,
    user2_id: int,
    user1_shift_id: int,
    user2_shift_id: int,
    roster_id: int
):
    
    await assign_shift_to_staff_db(
        session = session, 
        roster_id = roster_id,
        user_id = user1_id,
        shift_id = user2_shift_id
    )
    
    await assign_shift_to_staff_db(
        session = session, 
        roster_id = roster_id,
        user_id = user2_id,
        shift_id = user1_shift_id
    )
    
