from pydantic import BaseModel
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
    id: int
    title: str
    description: str
    completed: bool
    deadline_datetime_with_tz: datetime
    priority: int
    
class TaskSchema(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    assigned_to: str
    organization: str
    created_at: datetime
    deadline_datetime_with_tz: datetime
    priority: int