from dataclasses import dataclass, field
from typing import Literal, TypedDict


class ErrorDetails(TypedDict):
    api: str
    details: dict


@dataclass
class UserErrors(Exception):
    message: str = "Internal Server Error"
    response_code: int = 500
    type: str = "UserErrors"
    log_level: Literal['ERROR', 'CRITICAL', 'INFO', 'WARNING'] = 'ERROR'
    error_details: ErrorDetails = field(default = None)

    def __str__(self):
        return self.message


@dataclass
class S3Error(UserErrors):
    message: str = 'Error while connecting to S3. Please try again.'
    type: str = 'S3Errors'


@dataclass
class CredentialError(UserErrors):
    message: str = 'Could not validate credentials'
    response_code: int = 401
    type: str = 'CredentialError'
    log_level: Literal['ERROR', 'CRITICAL', 'INFO', 'WARNING'] = 'WARNING'
    
@dataclass
class PermissionDeniedError(UserErrors):
    message: str = "You don't have access to requested resource."
    response_code: int = 403
    type: str = 'PermissionDeniedError'
    log_level: Literal['ERROR', 'CRITICAL', 'INFO', 'WARNING'] = 'WARNING'