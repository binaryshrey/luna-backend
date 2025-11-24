from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.api.deps import get_db
from app.schemas.reco import VenueReco, UserReco
from app.services.reco_service import (
    recommend_venues_for_user,
    recommend_people_for_user,
)

router = APIRouter()

@router.get("/venues/{user_id}", response_model=List[VenueReco])
def get_venue_recommendations(
    user_id: UUID,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    return recommend_venues_for_user(db, user_id=user_id, limit=limit)

@router.get("/people/{user_id}", response_model=List[UserReco])
def get_people_recommendations(
    user_id: UUID,
    venue_id: UUID | None = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    return recommend_people_for_user(db, user_id=user_id, venue_id=venue_id, limit=limit)
