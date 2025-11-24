from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.api.deps import get_db
from app.models.plan import Plan, PlanParticipant
from app.schemas.plan import PlanCreate, PlanRead
from app.services.agent_service import create_booking_for_plan

router = APIRouter()

@router.post("/", response_model=PlanRead)
def create_plan(plan_in: PlanCreate, db: Session = Depends(get_db)):
    plan = Plan(
        organizer_id=plan_in.organizer_id,
        venue_id=plan_in.venue_id,
        start_time=plan_in.start_time,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)

    # Optional: add organizer as accepted participant
    participant = PlanParticipant(
        plan_id=plan.id,
        user_id=plan_in.organizer_id,
        status="accepted",
    )
    db.add(participant)
    db.commit()

    return PlanRead.from_orm(plan)

@router.post("/{plan_id}/confirm")
def confirm_plan(plan_id: UUID, db: Session = Depends(get_db)):
    plan = db.query(Plan).get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    plan.status = "confirmed"
    db.commit()
    db.refresh(plan)

    booking = create_booking_for_plan(db, plan)
    return {"plan_id": str(plan.id), "booking_id": str(booking.id)}
