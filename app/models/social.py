from sqlalchemy import Column, String, ForeignKey, BigInteger, Numeric
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base

class UserSocialEdge(Base):
    __tablename__ = "user_social_edges"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    other_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    relationship_type = Column(String)
    strength = Column(Numeric(3, 2), default=0.5)   # 0..1
