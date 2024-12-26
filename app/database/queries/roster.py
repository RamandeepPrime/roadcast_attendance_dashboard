from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, exists, func, insert, select, and_
from app.utils.custom_errors import PermissionDeniedError
from app.utils.logging_config import logger
from sqlalchemy.orm import Bundle
from sqlalchemy.exc import IntegrityError as SqlIntegrityError

from app.database.custom_errors import DataDeletionError, DataExtractionError, DataInjectionError, DatabaseErrors, ItemNotFound, IntegrityError
from app.database.database import Roster, RosterMember, RosterMemberOffDay, RosterShift, Shift, User

async def create_roster_db(
    manager_id: int,
    session: AsyncSession,
) -> List[int]:
    
    statement = insert(Roster).values(
        manager_id = manager_id    
    ).returning(
        Roster.id
    )

    try:
        data = await session.execute(statement)
        return data.scalar_one_or_none()
    except DatabaseErrors:
        raise
    except Exception:
        logger.error(f'Failed to get roster by manager_id: %s', manager_id, exc_info = True)
        raise DataExtractionError(message = 'Failed to get roster. Please try again')
    

async def get_roster_db(
    manager_id: int,
    session: AsyncSession,
) -> List[int]:
    
    statement = select(
        Roster.id
    ).where(Roster.manager_id == manager_id)

    try:
        data = await session.execute(statement)
        return data.scalars().all()
    except DatabaseErrors:
        raise
    except Exception:
        logger.error(f'Failed to get roster by manager_id: %s', manager_id, exc_info = True)
        raise DataExtractionError(message = 'Failed to get roster. Please try again')
    


async def get_roster_details_db(
    manager_id: int,
    roster_id: int,
    session: AsyncSession,
):
    # TODO need to improve 
    
    manager_roster_ids = await get_roster_db(manager_id = manager_id, session = session)
    if roster_id not in manager_roster_ids:
        raise PermissionDeniedError
    
    # shift_details = func.json_build_object(
    #     "day",
    #     Shift.day,
    #     'start_time',
    #     Shift.start_time,
    #     "end_time",
    #     Shift.end_time
    # )

    # statement = select(
    #     User.id,
    #     User.email_id,
    #     func.array_agg(RosterMemberOffDay.off_day).label("off_days"),
    #     func.array_agg(shift_details).label("shift_details")
    # ).select_from(
    #     User
    # ).join(
    #     RosterMember,
    #     RosterMember.user_id == User.id
    # ).outerjoin(
    #     RosterShift,
    #     RosterShift.roster_member_id == RosterMember.id
    # ).outerjoin(
    #     Shift,
    #     Shift.id == RosterShift.shift_id
    # ).outerjoin(
    #     RosterMemberOffDay,
    #     RosterMemberOffDay.roster_member_id == RosterMember.id
    # ).group_by(
    #     User.id,
    #     User.email_id
    # )
    shift_details = func.json_build_object(
        "day",
        Shift.day,
        'start_time',
        Shift.start_time,
        "end_time",
        Shift.end_time
    )

    off_days = select(
        RosterMember.id,
        func.array_agg(RosterMemberOffDay.off_day).label('off_days')
    ).select_from(
        User
    ).join(
        RosterMember,
        RosterMember.user_id == User.id
    ).join(
        RosterMemberOffDay,
        RosterMemberOffDay.roster_member_id == RosterMember.id
    ).group_by(RosterMember.id).cte("off_days")

    shift_days = select(
        RosterMember.id,
        func.array_agg(shift_details).label("shift_details")
    ).select_from(
        User
    ).join(
        RosterMember,
        RosterMember.user_id == User.id
    ).join(
        RosterShift,
        RosterShift.roster_member_id == RosterMember.id
    ).join(
        Shift,
        RosterShift.shift_id == Shift.id
    ).group_by(RosterMember.id).cte("shift_days")

    statement = select(
        User.id,
        User.email_id,
        func.coalesce(off_days.c.off_days, []).label("off_days"),
        func.coalesce(shift_days.c.shift_details, []).label('shift_details')
    ).select_from(
        User        
    ).join(
        RosterMember,
        and_(
            RosterMember.roster_id == roster_id,
            RosterMember.user_id == User.id
        )

    ).outerjoin(
        shift_days,
        RosterMember.id == shift_days.c.id
    ).outerjoin(
        off_days,
        RosterMember.id == off_days.c.id
    )

    try:
        data = await session.execute(statement)
        return data.mappings().all()
    except DatabaseErrors:
        raise
    except Exception:
        logger.error(f'Failed to get roster details by manager_id: %s', manager_id, exc_info = True)
        raise DataExtractionError(message = 'Failed to get roster. Please try again')
    

async def add_member_to_roster_db(
    manager_id: int,
    roster_id: int,
    user_id: int,
    off_days: list,
    session: AsyncSession
):
    # Ensure the manager has access to the given roster
    manager_roster_ids = await get_roster_db(manager_id=manager_id, session=session)
    if roster_id not in manager_roster_ids:
        raise PermissionDeniedError

    # Add the user to the roster
    statement = insert(RosterMember).values(roster_id=roster_id, user_id=user_id).returning(RosterMember.id)
    try:
        data = await session.execute(statement)
        roster_member_id = data.scalar_one_or_none()
        statement = insert(RosterMemberOffDay).values(
            [{
                RosterMemberOffDay.roster_member_id: roster_member_id, 
                RosterMemberOffDay.off_day: off_day
            } for off_day in off_days]
        )
        
        await session.execute(statement)
    except DatabaseErrors:
        raise

    except SqlIntegrityError:
        raise IntegrityError("User already exists in this roster")
    except Exception as e:
        logger.error(f'Failed to insert member in roster details by manager_id: %s', manager_id, exc_info = True)
        raise DataInjectionError(message = 'Failed to add member in roster. Please try again')
    

async def get_roster_member_id_db(
    roster_id: int,
    user_id: int,
    session: AsyncSession
):
    statement = select(RosterMember.id).where(RosterMember.roster_id == roster_id, RosterMember.user_id == user_id)
    try:
        data = await session.execute(statement)
        data = data.scalar_one_or_none()
        return data
    except DatabaseErrors:
        raise
    except Exception:
        logger.error(f'Failed to get member from roster', exc_info = True)
        raise DataExtractionError(message = 'Failed to get member from roster. Please try again')

async def delete_member_from_roster_db(
    manager_id: int,
    roster_id: int,
    user_id: int,
    session: AsyncSession
):
    # Ensure the manager has access to the given roster
    manager_roster_ids = await get_roster_db(manager_id=manager_id, session=session)
    if roster_id not in manager_roster_ids:
        raise PermissionDeniedError

    # Delete the user from the roster
    statement = delete(RosterMember).where(
        RosterMember.roster_id == roster_id,
        RosterMember.user_id == user_id
    ).returning(RosterMember)

    try:
        data = await session.execute(statement)
        if not data:
            raise ItemNotFound("This user is not assosiated to this roster_id")
        
    except DatabaseErrors:
        raise
    except Exception:
        logger.error(f'Failed to delete member from roster by manager_id: %s', manager_id, exc_info = True)
        raise DataDeletionError(message = 'Failed to delete member from roster. Please try again')


async def check_roster_exists_db(
    session: AsyncSession,
    roster_id: int,
):
    statement = select(exists().where(Roster.id == roster_id))
    data = await session.execute(statement)
    return data