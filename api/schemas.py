from pydantic import BaseModel
from ninja import ModelSchema
from datetime import datetime
from . import models

class LoginSchema(BaseModel):
    username: str
    password: str

class RegistrationSchema(BaseModel):
    username: str
    password: str
    organization_id: int
    
class TaskCreateSchema(BaseModel):
    title: str
    description: str
    completed: bool
    deadline_datetime_with_tz: datetime
    priority: int
    
class TaskUpdateSchema(BaseModel):
    title: str
    description: str
    completed: bool
    deadline_datetime_with_tz: datetime
    priority: int
    assigned_to: str
    
# class TaskSchema(BaseModel):
#     id: int
#     title: str
#     description: str
#     completed: bool
#     assigned_to: str
#     organization: str
#     created_at: datetime
#     deadline_datetime_with_tz: datetime
#     priority: int

class UserSchema(BaseModel):
    username: str