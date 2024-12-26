# User Defined Error used in Database
from dataclasses import dataclass
from typing import Literal
from app.utils.custom_errors import UserErrors

@dataclass
class DatabaseErrors(UserErrors):
    pass

@dataclass
class DataDeletionError(DatabaseErrors):
    message: str = "Can't Delete in Data in Database. Try Again"
    response_code: int = 503
    type: str = "DataDeletionError"

@dataclass
class DataInjectionError(DatabaseErrors):
    message: str = "Can't Insert Data in Database. Try Again"
    response_code: int = 503
    type: str = "DataInjectionError"

@dataclass
class DatabaseTypeErrors(DatabaseErrors):
    message: str = "Wrong Data Type. Can't create Database class Object"
    response_code: int = 422
    type: str = "DatabaseTypeErrors"

@dataclass
class DatabaseConnectionError(DatabaseErrors):
    message: str = "Can't Connect to Database .Try Again"
    response_code: int = 503
    type: str = "DatabaseConnectionError"

@dataclass
class ItemNotFound(DatabaseErrors):
    message: str = "Item doesn't exist"
    response_code: int = 404
    type: str = "ItemNotFound"
    
    
@dataclass
class IntegrityError(DatabaseErrors):
    message: str = "Assignment ID already exist"
    response_code: int = 422
    type: str = "IntegrityError"

@dataclass
class DataExtractionError(DatabaseErrors):
    message: str =  "Can't Extract Data from Database.Try Again"
    response_code: int = 503
    type: str = "DataExtractionError"

@dataclass
class DataUpdationError(DatabaseErrors):
    message: str =  "Can't Update Data. Try Again"
    response_code: int = 503
    type: str = "DataUpdationError"


@dataclass
class InvalidDataError(UserErrors):
    message: str = "Can't process the request with the given data. Please provide correct data."
    response_code: int = 400
    type: str = 'InvalidDataError'
    log_level: Literal['ERROR', 'CRITICAL', 'INFO', 'WARNING'] = 'WARNING'