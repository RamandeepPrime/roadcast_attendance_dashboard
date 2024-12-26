import asyncio
from typing import List, Literal
from pydantic import BaseModel, EmailStr

from app.database.custom_errors import ItemNotFound
from app.database.database import User
from app.database.enums import Role, Weekday
from app.database.queries.roster import check_roster_exists_db
from app.database.queries.user import get_user_by_email_db
from app.utils.custom_errors import PermissionDeniedError


class RosterMemberRequestModel(BaseModel):
	email_id: EmailStr
	off_days: List[Weekday]

	async def _validate_email_id(self, session, valid_roles: List[Literal[Role.STAFF]], user: User = None):
		if not user:
			user: User = await get_user_by_email_db(session = session, email_id = self.email_id)
		if not user:
			raise ItemNotFound("This email id doesn't exists")
		
		if user.role not in valid_roles:
			raise PermissionDeniedError('You can only assign shift to staff members')
		
	async def _validate_roster_id(self, session, roster_id: int):
		if not await check_roster_exists_db(session = session, roster_id = roster_id):
			raise ItemNotFound("This roster id doesn't exists")
		
	async def validate_request(self, session, roster_id: int, user: User = None):
		
		await self._validate_email_id(session, valid_roles = [Role.STAFF], user = user)
		await self._validate_roster_id(session, roster_id)
	
	