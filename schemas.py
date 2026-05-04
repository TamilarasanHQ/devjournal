from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class EntryCreate(BaseModel):
    title: str | None = None
    content: str

class EntryOut(BaseModel):
    id: int
    user_id: int
    title: str | None
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EntryUpdate(BaseModel):
    title: str | None = None
    content: str | None = None

class TokenData(BaseModel):
    user_id: int | None = None 