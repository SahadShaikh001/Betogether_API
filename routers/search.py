from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Category
from dependencies import get_current_user  # <-- Token dependency
from schemas import UserResponse
from typing import List

router = APIRouter(tags=["Search"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Search users by a single category name
@router.get("/users-by-category/{category_name}")
def get_users_by_category(
    category_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Token required
):
    category = db.query(Category).filter(Category.name.ilike(category_name)).first()
    if not category:
        return {"isSuccess": False, "message": "Category not found"}
    
    users = db.query(User).join(User.interests).filter(Category.id == category.id).all()
    if not users:
        return {"isSuccess": False, "message": "No users found in this category"}
    
    return {"isSuccess": True, "data": users}


# Optional: Search users by multiple categories (OR match)
@router.post("/users-by-categories")
def get_users_by_categories(
    category_names: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Token required
):
    categories = db.query(Category).filter(Category.name.in_(category_names)).all()
    if not categories:
        return {"isSuccess": False, "message": "No matching categories found"}
    
    category_ids = [c.id for c in categories]
    users = db.query(User).join(User.interests).filter(Category.id.in_(category_ids)).all()
    if not users:
        return {"isSuccess": False, "message": "No users found for these categories"}
    
    return {"isSuccess": True, "data": users}
