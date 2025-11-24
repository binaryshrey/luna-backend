# app/schemas/plan.py

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class PlanBase(BaseModel):
    organizer_id: UUID
    venue_id: UUID
    start_time: datetime


class PlanCreate(PlanBase):
    pass


class PlanRead(BaseModel):
    id: UUID
    organizer_id: UUID
    venue_id: UUID
    start_time: datetime
    status: str

    class Config:
        from_attributes = True
