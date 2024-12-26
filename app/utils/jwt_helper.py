from functools import lru_cache
from typing import Tuple
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from pydantic import ValidationError
from app.database import get_db_instance
from app.database.database import User
from app.database.queries.user import get_user_by_email_db
from app.routers.pydantics.users import TokenData
from app.utils.custom_errors import CredentialError
from app.utils.logging_config import logger

from app.utils.constants import (
	JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
	JWT_ALGORITHM,
	JWT_SECRET_KEY,
	JWT_SUBJECT
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="")


def create_access_token(data: dict, expires_delta: timedelta=timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)) -> Tuple[str, datetime]:
	
	to_encode = data.copy()
	expire = datetime.now(timezone.utc) + expires_delta
	to_encode.update({
		'exp': expire, 'sub' : JWT_SUBJECT
	})
	return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM), expire


async def get_current_user(
	token: str = Depends(oauth2_scheme), 
	session = Depends(get_db_instance)
) -> User:
	
	try:
		decoded_dict = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
		token: TokenData = TokenData(**decoded_dict)
		
		user = await get_user_by_email_db(session = session, email_id = token.email_id)
		return user
		

	except JWTError:
		logger.warning("Credential Error for User email_id", exc_info = True)
		raise CredentialError()

	except ValidationError:
		email_id = decoded_dict.get('email_id')
		email_id = email_id if email_id else "Can't Access email_id"
		logger.warning(f"\n Credential Error for User email_id: {email_id}")
		raise CredentialError(message = 'Malformed Token.')
