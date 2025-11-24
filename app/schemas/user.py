from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class UserBase(BaseModel):
    handle: str
    name: str
    home_lat: Optional[float] = None
    home_lng: Optional[float] = None
    age: Optional[int] = None

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: UUID

    class Config:
        from_attributes = True
