from sqlalchemy import Column, String, Integer, Float, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.session import Base

class Venue(Base):
    __tablename__ = "venues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    price_level = Column(Integer)
    rating = Column(Numeric(2, 1))
