from pydantic import BaseModel, EmailStr, Field
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


class TagCreate(BaseModel):
    name: str

class TagOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class EntryOut(BaseModel):
    id: int
    user_id: int
    title: str | None
    content: str
    created_at: datetime
    updated_at: datetime
    tags: list[TagOut] = []
    understanding_rating: int | None = None
    last_reviewed_at: datetime | None = None
    review_count: int = 0
    next_review_date: datetime | None = None
    class Config:
        from_attributes = True

class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)  # rating between 1 and 5

class EntryCreate(BaseModel):
    title: str | None = None
    content: str
    tags: list[str] = []  # list of tag names

class EntryUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    tags: list[str] | None = None
    understanding_rating: int | None = Field(None, ge=1, le=5)
    review_count: int | None = Field(None, ge=0)
class TokenData(BaseModel):
    user_id: int | None = None 

