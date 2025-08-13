from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from schemas import UserResponse
from dependencies import get_current_user

router = APIRouter(tags=["Users"])


# ✅ DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ Helper to check OTP verification
def ensure_verified_user(user: User):
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your OTP before accessing this feature."
        )


# ✅ Get a specific user by ID
@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ensure_verified_user(current_user)  # OTP check

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# ✅ Get all users
@router.get("/users", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ensure_verified_user(current_user)  # OTP check

    users = db.query(User).all()
    return users

"""from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from database import SessionLocal
from models import User
from schemas import UserResponse
from typing import List
from dependencies import get_current_user  # <-- token validator

router = APIRouter(tags=["Users"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Get a specific user by ID with full interest category data
@router.get("/users/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)  # token required
):
    user = (
        db.query(User)
        .options(joinedload(User.interests))  # eager load interests
        .filter(User.id == user_id)
        .first()
    )
    if not user:
        return {"isSuccess": False, "message": "User not found"}
    
    return {
        "isSuccess": True,
        "data": UserResponse.from_orm(user)
    }

# ✅ Get all users with full interest category data
@router.get("/users")
def get_all_users(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)  # token required
):
    users = db.query(User).options(joinedload(User.interests)).all()
    return {
        "isSuccess": True,
        "data": [UserResponse.from_orm(user) for user in users]
    }


""""""
# ❌ Optional: Delete a user
@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return
"""