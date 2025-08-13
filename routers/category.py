<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Category, User
from schemas import CategoryOut, UserLocation
from dependencies import get_current_user  # token validation
import math

router = APIRouter(tags=["Category"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

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

 # ✅ 3. post category with category AND LIST OF it
@router.post("/category/nearest")
def assign_nearest_category(
    location: UserLocation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    categories = db.query(Category).all()
    if not categories:
        raise HTTPException(status_code=404, detail={"IsSuccess": False, "message": "No categories found"})

    nearby = []
    for cat in categories:
        if cat.latitude is None or cat.longitude is None:
            continue
        dist = haversine(location.latitude, location.longitude, cat.latitude, cat.longitude)
        if location.radius_km is None or dist <= location.radius_km:
            nearby.append({
                "id": cat.id,
                "category": cat.name,
                "image": cat.image,
                "latitude": cat.latitude,
                "longitude": cat.longitude,
                "distance_km": round(dist, 2)
            })

    if not nearby:
        return {"IsSuccess": False, "message": "No categories found within radius"}

    nearest = sorted(nearby, key=lambda x: x["distance_km"])[0]
    return {
        "IsSuccess": True,
        "message": f"Nearest category '{nearest['category']}' assigned",
        "data": nearest,
        "list": nearby
    }
=======
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
>>>>>>> 4f4447a70f4a774e40751869788c5d0086421b94
