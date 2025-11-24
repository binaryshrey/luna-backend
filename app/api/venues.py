from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.api.deps import get_db
from app.models.venue import Venue
from app.models.interactions import UserVenueInteraction
from app.schemas.venue import VenueCreate, VenueRead
from app.schemas.interactions import InteractionCreate

router = APIRouter()

@router.post("/", response_model=VenueRead)
def create_venue(venue_in: VenueCreate, db: Session = Depends(get_db)):
    venue = Venue(**venue_in.model_dump())
    db.add(venue)
    db.commit()
    db.refresh(venue)
    return venue

@router.get("/", response_model=List[VenueRead])
def list_venues(db: Session = Depends(get_db)):
    return db.query(Venue).all()

@router.post("/{venue_id}/interact")
def record_interaction(
    venue_id: UUID,
    interaction: InteractionCreate,
    db: Session = Depends(get_db)
):
    record = UserVenueInteraction(
        user_id=interaction.user_id,
        venue_id=venue_id,
        interaction_type=interaction.interaction_type,
        dwell_time_seconds=interaction.dwell_time_seconds or 0
    )
    db.add(record)
    db.commit()
    return {"status": "ok"}
