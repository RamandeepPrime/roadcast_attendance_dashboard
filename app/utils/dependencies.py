from typing import List, Literal
from fastapi import Depends
from app.database import get_db_instance
from app.database.database import User
from app.database.enums import Role
from app.utils.custom_errors import PermissionDeniedError
from app.utils.jwt_helper import get_current_user


class UserValidator:
    def __init__(self, valid_roles: List[Literal[Role.MANAGER, Role.ADMIN, Role.STAFF]]):
        self.valid_roles = valid_roles
    
    async def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.valid_roles:
            raise PermissionDeniedError