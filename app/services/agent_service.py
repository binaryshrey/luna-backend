from sqlalchemy.orm import Session
from uuid import uuid4
from app.models.plan import Plan
from app.models.booking import Booking

def create_booking_for_plan(db: Session, plan: Plan) -> Booking:
    # In production: we can call OpenTable / TicketMaster or partner APIs here - but for now we can simulate an external booking reference.
    external_id = f"mock-{uuid4()}"

    booking = Booking(
        plan_id=plan.id,
        provider="mock",
        external_ref=external_id,
        status="created",
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking
