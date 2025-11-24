from pydantic import BaseModel
from uuid import UUID

class VenueReco(BaseModel):
    venue_id: UUID
    score: float
    distance_km: float

class UserReco(BaseModel):
    user_id: UUID
    score: float
