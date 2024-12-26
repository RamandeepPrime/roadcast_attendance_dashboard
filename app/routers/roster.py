

from fastapi import APIRouter, Depends

from app.database import get_db_instance
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import User
from app.database.enums import Role
from app.database.queries.roster import add_member_to_roster_db, create_roster_db, delete_member_from_roster_db, get_roster_db, get_roster_details_db
from app.database.queries.user import get_user_by_email_db
from app.routers.pydantics.roster import RosterMemberRequestModel
from app.utils.dependencies import UserValidator
from app.utils.error_handlers import ErrorHandlingLoggingRoute
from app.utils.jwt_helper import get_current_user


router = APIRouter(
    route_class = ErrorHandlingLoggingRoute,
    dependencies = [
        Depends(UserValidator([Role.MANAGER, Role.ADMIN]))
    ]
)

@router.post('')
async def create_roster(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_instance)
):
    roster_id = await create_roster_db(manager_id = user.id, session = session)
    await session.commit()
    return {
        "success": True,
        "roster_id": roster_id
    }

@router.get('')
async def get_roster(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_instance)
):
    roster_details = await get_roster_db(manager_id = user.id, session = session)
    return {
        "success": True,
        "roster_ids": roster_details
    }

@router.get('/{roster_id}')
async def get_roster_details(
    roster_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_instance)
):
    roster_data = await get_roster_details_db(
        session = session,
        roster_id = roster_id,
        manager_id = user.id
    )
        
    return {
        "success": True,
        "data": roster_data
    }

@router.post("/{roster_id}/members")
async def add_member_to_roster(
    roster_id: int,
    member_details: RosterMemberRequestModel,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_instance)
):
    await member_details.validate_request(session = session, roster_id = roster_id)
    staff = await get_user_by_email_db(session = session, email_id = member_details.email_id)
    await add_member_to_roster_db(
        manager_id = user.id,
        roster_id = roster_id,
        user_id = staff.id,
        off_days = member_details.off_days,
        session = session
    )
    await session.commit()
    return {"success": True,"message": "Member added successfully"}
    

@router.delete("/{roster_id}/members/{email_id}")
async def delete_member_from_roster(
    roster_id: int,
    email_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_instance)
):
    staff = await get_user_by_email_db(session = session, email_id = email_id)
    await delete_member_from_roster_db(
        manager_id = user.id, 
        roster_id = roster_id, 
        user_id = staff.id,
        session = session
    )

    await session.commit()
    return {
        "success": True,
        "message": "Member deleted successfully"
    }
    