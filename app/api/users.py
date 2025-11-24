from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead

router = APIRouter()

@router.post("/", response_model=UserRead)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.handle == user_in.handle).first()
    if existing:
        raise HTTPException(status_code=400, detail="Handle already taken")
    user = User(**user_in.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/", response_model=List[UserRead])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()
