from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_instance
from app.database.database import User
from app.database.queries.user import create_user_db, get_user_by_email_db
from app.routers.pydantics.users import LoginRequestModel, UserRequestModel
from app.utils.custom_errors import CredentialError, PermissionDeniedError
from app.utils.error_handlers import ErrorHandlingLoggingRoute
from app.utils.jwt_helper import create_access_token, get_current_user
from app.utils.pwd_helper import get_password_hash, verify_password


router = APIRouter(route_class = ErrorHandlingLoggingRoute)

@router.post('')
async def add_new_members(
    user_details: UserRequestModel,
    session: AsyncSession = Depends(get_db_instance),
    user: User = Depends(get_current_user)

):
    user_details.validate_request(curr_user = user)

    user_dict = user_details.model_dump()
    user_dict['hashed_password'] = get_password_hash(user_dict.pop("password").get_secret_value())

    await create_user_db(session, user_dict)
    await session.commit()
    return {"success": True, "message": "User created successfully"}


@router.get('/login')
async def login(
    login_data: LoginRequestModel,
    session: AsyncSession = Depends(get_db_instance)
):

    user: User = await get_user_by_email_db(session, login_data.email_id)
    if not user or not verify_password(login_data.password.get_secret_value(), user.hashed_password):
        raise CredentialError

    access_token = create_access_token(data={"email_id": user.email_id, "role": user.role.value})
    return {"success": True, "access_token": access_token, "token_type": "bearer"}
