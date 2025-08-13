<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Category
from schemas import AuthResponse, UserLogin, TokenRefreshRequest, OTPVerifyRequest
from passlib.context import CryptContext
from utils.jwt_handler import create_access_token, create_refresh_token, decode_token
import shutil, os, uuid, json, random
from database import get_db
from utils.email_utils import send_otp_email
from utils.otp_utils import generate_otp  # ✅ import helper
from datetime import datetime
from email_validator import validate_email, EmailNotValidError

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

# ------------------ REGISTER ------------------
@router.post("/register")
def register(
    name: str = Form(...),
    email: str = Form(...),
    mobile: str = Form(...),
    password: str = Form(None),
    register_type: str = Form(...),
    uid: str = Form(None),
    profile_image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    # Email validation
    try:
        validate_email(email)
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if register_type not in ["manual_login", "social_login"]:
        raise HTTPException(status_code=400, detail="Invalid register_type.")

    if register_type == "manual_login" and not password:
        raise HTTPException(status_code=400, detail="Password required for manual login.")

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered.")

    hashed_password = None
    if register_type == "manual_login":
        hashed_password = pwd_context.hash(password)

    image_path = None
    if profile_image:
        ext = profile_image.filename.split(".")[-1]
        image_name = f"{uuid.uuid4().hex}.{ext}"
        image_path = os.path.join(UPLOAD_DIR, image_name)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(profile_image.file, buffer)

    new_user = User(
        uid=uid,
        name=name,
        email=email,
        mobile=mobile,
        hashed_password=hashed_password,
        profile_image=image_path,
        register_type=register_type
    )
    if register_type == "manual_login":
        otp_code, otp_expiry = generate_otp()  # ✅ get OTP from util
        new_user.otp_code = otp_code
        new_user.otp_expiry = otp_expiry
        send_otp_email(email, otp_code)
    else:
        new_user.otp_verified = True
    
    #if register_type == "manual_login":
     #   new_user.generate_otp()
      #  send_otp_email(email, new_user.otp_code)
    #else:
      #  new_user.otp_verified = True  # Google login skips OTP

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"IsSucces": True, "message": "OTP sent. Please verify." if register_type == "manual_login" else "Registered successfully."}
# ------------------ LOGIN ------------------
@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        return {"IsSucces": False, "message": "Invalid credentials."}

    if user.register_type == "manual_login":
        if not pwd_context.verify(user_data.password, user.hashed_password):
            return {"IsSucces": False, "message": "Invalid credentials."}

        # If OTP not verified → send OTP for login verification
        if not user.otp_verified:
            otp_code, otp_expiry = generate_otp()
            user.otp_code = otp_code
            user.otp_expiry = otp_expiry
            db.commit()
            send_otp_email(user.email, otp_code)
            return {
                "IsSucces": True,
                "message": "OTP sent for login. Please verify to complete login."
            }

    # Already verified → normal login
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})
    user.access_token = access_token
    user.refresh_token = refresh_token
    db.commit()
    db.refresh(user)

    return {
        "IsSucces": True,
        "message": "Login successful.",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "mobile": user.mobile,
            "profile_image": user.profile_image,
            "uid": user.uid
        }
    }


# ------------------ VERIFY OTP (registration + login) ------------------
@router.post("/verify-otp")
def verify_otp(payload: OTPVerifyRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.otp_code:
        raise HTTPException(status_code=400, detail="No OTP generated for this user")

    if user.otp_code != payload.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # OTP verified
    user.otp_verified = True
    user.otp_code = None
    db.commit()
    db.refresh(user)

    # Generate tokens
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})
    user.access_token = access_token
    user.refresh_token = refresh_token
    db.commit()

    # Detect if OTP was for registration or login
    if not user.hashed_password and user.register_type == "social_login":
        message = "Registration completed via social login."
    elif (datetime.utcnow() - user.created_at).total_seconds() < 300:
        message = "OTP verified successfully, registration completed."
    else:
        message = "Login successful."

    return {
        "IsSuccess": True,
        "message": message,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "mobile": user.mobile,
            "profile_image": user.profile_image,
            "uid": user.uid
        }
    }
"""
# ------------------ VERIFY OTP ------------------
@router.post("/verify-otp")
def verify_otp(payload: OTPVerifyRequest, db: Session = Depends(get_db)):
    # Fetch user
    user = db.query(User).filter(User.email == payload.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.otp_code:
        raise HTTPException(status_code=400, detail="No OTP generated for this user")

    # Compare OTP
    if user.otp_code != payload.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Mark OTP as verified
    user.otp_verified = True
    user.otp_code = None  # clear it after use
    db.commit()
    db.refresh(user)

    # Generate tokens only if needed
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})
    user.access_token = access_token
    user.refresh_token = refresh_token
    db.commit()

    return {
        "IsSuccess": True,
        "message": "OTP verified successfully, registration completed.",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "mobile": user.mobile,
            "profile_image": user.profile_image,
            "uid": user.uid
        }
    }


# ------------------ LOGIN ------------------
@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        return {"IsSucces": False, "message": "Invalid credentials."}

    if user.register_type == "manual_login":
        if not pwd_context.verify(user_data.password, user.hashed_password):
            return {"IsSucces": False, "message": "Invalid credentials."}
        if not user.otp_verified:
            user.generate_otp()
            db.commit()
            send_otp_email(user.email, user.otp_code)
            return {"IsSucces": True, "message": "OTP sent. Please verify to complete login."}

    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})
    user.access_token = access_token
    user.refresh_token = refresh_token
    db.commit()
    db.refresh(user)

    return {
        "IsSucces": True,
        "message": "Login successful.",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user.__dict__
    }
"""
# ------------------ REFRESH TOKEN ------------------
@router.post("/refresh-token")
def refresh_token(payload: TokenRefreshRequest):
    try:
        decoded = decode_token(payload.refresh_token)
        email = decoded.get("sub")
        new_access_token = create_access_token({"sub": email})
        return {"access_token": new_access_token, "token_type": "bearer"}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token.")

"""

# ✅ REGISTER
@router.post("/register", response_model=AuthResponse)
def register(
    name: str = Form(...),
    email: str = Form(...),
    mobile: str = Form(...),
    password: str = Form(None),
    latitude: str = Form(None),
    longitude: str = Form(None),
    user_interest: str = Form(None),
    register_type: str = Form(...),  # ✅ NEW FIELD
    profile_image: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    # Validate register_type
    if register_type not in ["manual_login", "social_login"]:
        return {
            "IsSucces": False,
            "message": "register_type must be either 'manual_login' or 'social_login'.",
            "access_token": None,
            "refresh_token": None,
            "token_type": "bearer",
            "user": None
        }

    # Manual login requires a password
    if register_type == "manual_login" and not password:
        return {
            "IsSucces": False,
            "message": "Password is required for manual login.",
            "access_token": None,
            "refresh_token": None,
            "token_type": "bearer",
            "user": None
        }

    # Check if email already exists
    if db.query(User).filter(User.email == email).first():
        return {
            "IsSucces": False,
            "message": "User with this email already exists.",
            "access_token": None,
            "refresh_token": None,
            "token_type": "bearer",
            "user": None
        }

    hashed_password = None
    if register_type == "manual_login":
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
        register_type=register_type,  # ✅ Store register type
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

    if not db_user:
        return {
            "IsSucces": False,
            "message": "Invalid email or password.",
            "access_token": None,
            "refresh_token": None,
            "token_type": "bearer",
            "user": None
        }

    # ✅ If manual login, verify password
    if db_user.register_type == "manual_login":
        if not pwd_context.verify(user.password, db_user.hashed_password):
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
    db.commit()
    db.refresh(db_user)

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
"""
"""
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



"""
=======
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
>>>>>>> 4f4447a70f4a774e40751869788c5d0086421b94
