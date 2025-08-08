from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Category
from schemas import AuthResponse, UserLogin, TokenRefreshRequest
from passlib.context import CryptContext
from utils.jwt_handler import create_access_token, create_refresh_token, decode_token
import shutil, os, uuid, json

router = APIRouter(tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

UPLOAD_DIR = "static/profile_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ REGISTER
@router.post("/register", response_model=AuthResponse)
def register(
    name: str = Form(...),
    email: str = Form(...),
    mobile: str = Form(...),
    password: str = Form(...),
    latitude: str = Form(None),
    longitude: str = Form(None),
    user_interest: str = Form(None),
    profile_image: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.email == email).first():
        return {
            "IsSucces": False,
            "message": "User with this email already exists.",
            "access_token": None,
            "refresh_token": None,
            "token_type": "bearer",
            "user": None
        }

    hashed_password = pwd_context.hash(password)
    image_path = None

    if profile_image:
        ext = profile_image.filename.split(".")[-1]
        image_name = f"{uuid.uuid4().hex}.{ext}"
        image_path = os.path.join(UPLOAD_DIR, image_name)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(profile_image.file, buffer)

    interest_names = []
    if user_interest:
        try:
            interest_names = json.loads(user_interest) if isinstance(user_interest, str) else user_interest
            if not isinstance(interest_names, list):
                raise ValueError("Interests must be a list.")
        except Exception:
            return {
                "IsSucces": False,
                "message": "Invalid interest format.",
                "access_token": None,
                "refresh_token": None,
                "token_type": "bearer",
                "user": None
            }

    categories = db.query(Category).filter(Category.name.in_(interest_names)).all()

    new_user = User(
        name=name,
        email=email,
        mobile=mobile,
        hashed_password=hashed_password,
        latitude=latitude,
        longitude=longitude,
        profile_image=image_path if profile_image else None,
        interests=categories
    )
    access_token = create_access_token({"sub": new_user.email})
    refresh_token = create_refresh_token({"sub": new_user.email})
    # ✅ Save tokens to DB
    new_user.access_token = access_token
    new_user.refresh_token = refresh_token
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

#    access_token = create_access_token({"sub": new_user.email})
 #   refresh_token = create_refresh_token({"sub": new_user.email})

    return {
        "IsSucces": True,
        "message": "Registration successful.",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": new_user
    }

# ✅ LOGIN
@router.post("/login", response_model=AuthResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        return {
            "IsSucces": False,
            "message": "Invalid email or password.",
            "access_token": None,
            "refresh_token": None,
            "token_type": "bearer",
            "user": None
        }

    access_token = create_access_token({"sub": db_user.email})
    refresh_token = create_refresh_token({"sub": db_user.email})

     # ✅ Update tokens in DB
    db_user.access_token = access_token
    db_user.refresh_token = refresh_token

    return {
        "IsSucces": True,
        "message": "Login successful.",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": db_user
    }

# ✅ REFRESH TOKEN
@router.post("/refresh-token")
def refresh_token(payload: TokenRefreshRequest):
    try:
        decoded = decode_token(payload.refresh_token)
        email = decoded.get("sub")
        new_access_token = create_access_token({"sub": email})
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
