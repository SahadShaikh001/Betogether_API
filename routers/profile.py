from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from models import User, Category, Language
from schemas import UserResponse, UserProfileUpdate, BaseResponse
from database import get_db
from dependencies import get_current_user

router = APIRouter(tags=["Profile"])


# ===== GET PROFILE =====
@router.get("/profile", response_model=UserResponse)
def get_my_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get the current user's profile with languages & interests.
    """
    db.refresh(current_user)  # ensure relationships are loaded
    return current_user


# ===== UPDATE PROFILE =====
@router.put("/edit_profile", response_model=BaseResponse)
def update_my_profile(
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update profile image, name, bio, languages (by name), and interests (by name).
    """
    updated = False

    # Update basic fields
    if profile_data.profile_image is not None:
        current_user.profile_image = profile_data.profile_image
        updated = True

    if profile_data.name is not None:
        current_user.name = profile_data.name
        updated = True

    if profile_data.bio is not None:
        current_user.bio = profile_data.bio
        updated = True

    # Update Languages by names
    if profile_data.languages is not None:
        db_languages = []
        for lang_name in profile_data.languages:
            lang_obj = db.query(Language).filter(Language.name.ilike(lang_name.strip())).first()
            if not lang_obj:
                # Auto-create language if not found
                lang_obj = Language(name=lang_name.strip())
                db.add(lang_obj)
                db.commit()
                db.refresh(lang_obj)
            db_languages.append(lang_obj)
        current_user.languages = db_languages
        updated = True

    # Update Interests by names
    if profile_data.interests is not None:
        db_categories = []
        for cat_name in profile_data.interests:
            cat_obj = db.query(Category).filter(Category.name.ilike(cat_name.strip())).first()
            if not cat_obj:
                raise HTTPException(status_code=404, detail=f"Category '{cat_name}' not found")
            db_categories.append(cat_obj)
        current_user.interests = db_categories
        updated = True

    if updated:
        db.commit()
        db.refresh(current_user)
        return BaseResponse(IsSucces=True, message="Profile updated successfully", data={"user_id": current_user.id})
    else:
        return BaseResponse(IsSucces=False, message="No changes were made")
