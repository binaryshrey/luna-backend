from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    handle = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    home_lat = Column(Float)
    home_lng = Column(Float)
    age = Column(Integer)
