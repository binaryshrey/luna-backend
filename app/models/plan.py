from sqlalchemy import Column, String, ForeignKey, DateTime, BigInteger
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.session import Base

class Plan(Base):
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    venue_id = Column(UUID(as_uuid=True), ForeignKey("venues.id"))
    start_time = Column(DateTime)
    status = Column(String, default="pending")

class PlanParticipant(Base):
    __tablename__ = "plan_participants"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(String, default="invited")
