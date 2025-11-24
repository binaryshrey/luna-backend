from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class InteractionCreate(BaseModel):
    user_id: UUID
    interaction_type: str
    dwell_time_seconds: Optional[int] = 0
