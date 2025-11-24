from sqlalchemy import Column, String, Integer, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base

class UserVenueInteraction(Base):
    __tablename__ = "user_venue_interactions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    venue_id = Column(UUID(as_uuid=True), ForeignKey("venues.id"), nullable=False)
    interaction_type = Column(String, nullable=False)   # 'view', 'like', etc.
    dwell_time_seconds = Column(Integer, default=0)
