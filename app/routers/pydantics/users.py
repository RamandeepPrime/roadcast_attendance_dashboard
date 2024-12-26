from pydantic import BaseModel, SecretStr

from app.database.database import User
from app.database.enums import Role
from app.utils.custom_errors import PermissionDeniedError


class UserRequestModel(BaseModel):
	name: str
	email_id: str
	password: SecretStr
	role: Role

	def validate_request(self, curr_user: User):
		if curr_user.role not in [Role.MANAGER, Role.ADMIN]:
			print("hello")
			raise PermissionDeniedError
		
		if self.role.value == Role.MANAGER.value and curr_user.role.value == Role.MANAGER.value:
			raise PermissionDeniedError("Manager can't create another manager")
		
		return 


class LoginRequestModel(BaseModel):
	email_id: str 
	password: SecretStr


class TokenData(BaseModel):
	email_id: str
	role: Role