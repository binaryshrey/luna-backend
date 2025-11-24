from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class VenueBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    lat: float
    lng: float
    price_level: Optional[int] = None
    rating: Optional[float] = None

class VenueCreate(VenueBase):
    pass

class VenueRead(VenueBase):
    id: UUID

    class Config:
        from_attributes = True
