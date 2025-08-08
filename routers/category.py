from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Category, User
from schemas import CategoryOut
from dependencies import get_current_user  # token validation

router = APIRouter(tags=["Category"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ 1. Full list with IsSuccess flag
@router.get("/category")
def get_all_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    categories = db.query(Category).all()
    return {
        "IsSuccess": True,
        "data": categories
    }

# ✅ 2. Get category by ID or name dynamically with IsSuccess flag
@router.get("/category/{id_or_name}")
def get_category(
    id_or_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if id_or_name.isdigit():
        category = db.query(Category).filter(Category.id == int(id_or_name)).first()
    else:
        category = db.query(Category).filter(Category.name.ilike(id_or_name)).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"IsSuccess": False, "message": "Category not found"}
        )
    
    return {
        "IsSuccess": True,
        "data": category
    }
