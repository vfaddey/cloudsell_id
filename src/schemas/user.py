from datetime import datetime

from pydantic import BaseModel, EmailStr
from pydantic import UUID4

from src.models.user import AccountType


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    account_type: AccountType

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id: UUID4
    name: str
    email: EmailStr
    account_type: AccountType
    created_at: datetime
    updated_at: datetime
    email_confirmed: bool

    class Config:
        from_attributes = True