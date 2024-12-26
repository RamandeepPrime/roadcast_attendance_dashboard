import asyncio
from typing import List, Literal
from pydantic import BaseModel

from app.database.custom_errors import InvalidDataError, ItemNotFound
from app.database.database import Roster, Shift, User
from app.database.enums import Role, Weekday
from app.database.queries.roster import check_roster_exists_db
from app.database.queries.shifts import check_shift_exists_db, get_allocated_shifts_db
from app.database.queries.user import check_user_exists_db, get_user_by_email_db
from app.utils.custom_errors import PermissionDeniedError


class AssignShiftsRequestModel(BaseModel):
	email_id: str
	shift_id: int
	roster_id: int

	async def _validate_shift_id(self, session):
		if not await check_shift_exists_db(session, shift_id = self.shift_id):
			raise ItemNotFound("This shift id doesn't exists")
		
	async def _validate_roster_id(self, session):
		if not await check_roster_exists_db(session = session, roster_id = self.roster_id):
			raise ItemNotFound("This roster id doesn't exists")

	async def _validate_email_id(
		self, 
		session, 
		valid_roles: List[Literal[Role.STAFF]], 
		user: User = None
	):
		if not user:
			user: User = await get_user_by_email_db(session = session, email_id = self.email_id)
		if not user:
			raise ItemNotFound("This email id doesn't exists")
		
		if user.role not in valid_roles:
			raise PermissionDeniedError('You can only assign shift to staff members')
		
	async def validate_request(self, session, user: User = None):
		
		await self._validate_email_id(session, valid_roles = [Role.STAFF], user = user)
		await self._validate_roster_id(session)
		await self._validate_shift_id(session)


class SwapShiftsRequestModel(BaseModel):
	email_id: str
	roster_id: int
	day: Weekday

	"""
		check if they already have same shift_id
		check if they have same roster_id
		check if they have same day shift
		check if this shift id belonngs to email_id
	"""
	async def _validate_roster_id(self, session):
		if not await check_roster_exists_db(session = session, roster_id = self.roster_id):
			raise ItemNotFound("This roster id doesn't exists")
		
	async def validate_shifts(self, session, user1_email_id: str, user2_email_id: str):
		"""
			find allocated shifts for both users for that day
		"""
		user1_shifts = await get_allocated_shifts_db(
			session = session,
			email_id = user1_email_id,
			additional_filters = (
				Shift.day == self.day,
				Roster.id == self.roster_id
			)
		)

		user2_shifts = await get_allocated_shifts_db(
			session = session,
			email_id = user2_email_id,
			additional_filters = (
				Shift.day == self.day,
				Roster.id == self.roster_id
			)
		)

		if not user1_shifts:
			raise InvalidDataError(f"No Shift assigned to {user1_email_id}")
		
		if not user2_shifts:
			raise InvalidDataError(f"No Shift assigned to {user2_email_id}")

		return user1_shifts, user2_shifts
		
	async def validate_request(self, session):
		await self._validate_roster_id(session = session)
