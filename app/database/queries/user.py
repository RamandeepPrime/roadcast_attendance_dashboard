import email
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exists, insert, select
from app.utils.logging_config import logger
from app.database.custom_errors import DataExtractionError, DataInjectionError, DatabaseErrors, ItemNotFound
from app.database.database import User

async def create_user_db(
    session: AsyncSession,
    data: Dict,
):
    statement = insert(User).values(data)

    try:
        await session.execute(statement)
    except DatabaseErrors:
        raise
    except Exception:
        logger.error(f'Failed to create user with data: %s', data, exc_info = True)
        raise DataInjectionError(message = 'Failed to create user. Please try again')
    
async def get_user_by_email_db(
    session: AsyncSession,
    email_id: str
) -> User:
    
    statement = select(User).where(User.email_id == email_id)
    try:
        data = await session.execute(statement)
        data = data.scalar_one_or_none()
        if not data:
            ItemNotFound("User with this email doesn't exist")
        return data
    except (DatabaseErrors,ItemNotFound):
        raise
    except Exception:
        logger.error(f'Failed to get user by email: %s', email_id, exc_info = True)
        raise DataExtractionError(message = 'Failed to get user. Please try again')
    

async def check_user_exists_db(
	session: AsyncSession,
    email_id: str
):
    statement = select(exists().where(User.email_id == email_id))
    data = await session.execute(statement)
    return data