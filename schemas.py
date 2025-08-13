<<<<<<< HEAD
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Union
from datetime import datetime

# ---------- Registration ----------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    mobile: str
    password: str
    profile_image: Optional[str] = None
    register_type: str  # manual_login / social_login
    uid: Optional[str] = None  # Google UID (optional)

# ---------- Login ----------
class UserLogin(BaseModel):
    email: EmailStr
    password: Optional[str] = None  # Optional for social login


# ---------- OTP Verification ----------
class OTPRequest(BaseModel):
    email: EmailStr


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str


# ---------- Tokens ----------
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ---------- Category ----------
class CategoryOut(BaseModel):
    id: int
    name: str
    image: Optional[str] = None

    class Config:
        from_attributes = True


class CategoryIDName(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


# ---------- Language ----------
class LanguageOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# ---------- Profile Update ----------
class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    languages: Optional[List[int]] = None  # language IDs only
    interests: Optional[List[int]] = None  # category IDs only


# ---------- Profile Response ----------
class UserProfileResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    mobile: str
    profile_image: Optional[str]
    bio: Optional[str]
    languages: List[LanguageOut] = []
    interests: List[CategoryOut] = []
    is_verified: bool

    class Config:
        from_attributes = True


# ---------- Minimal User Response ----------
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    mobile: str
    profile_image: Optional[str] = None
    register_type: Optional[str] = None
    languages: Optional[List[LanguageOut]] = None
    interests: Optional[List[CategoryOut]] = None
    is_verified: bool

    class Config:
        from_attributes = True


# ---------- Auth Response ----------
class AuthResponse(BaseModel):
    IsSucces: bool
    message: Optional[str]
    access_token: Optional[str]
    refresh_token: Optional[str]
    token_type: str = "bearer"
    user: Optional[Union[UserResponse, UserProfileResponse]]


# ---------- Base Response ----------
class BaseResponse(BaseModel):
    IsSucces: bool
    message: Optional[str] = None
    data: Optional[dict] = None


# ---------- Token Refresh ----------
class TokenRefreshRequest(BaseModel):
    refresh_token: str


# ---------- User Location ----------
class UserLocation(BaseModel):
    latitude: float
    longitude: float
    radius_km: Optional[float] = None  # optional filtering

"""from pydantic import BaseModel, EmailStr
from typing import Optional, List, Union

# ---------- Registration ----------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    mobile: str
    password: str
    profile_image: Optional[str] = None
    register_type: str  # manual_login / social_login


# ---------- Login ----------
class UserLogin(BaseModel):
    email: EmailStr
    password: Optional[str] = None  # Optional for social login


# ---------- Tokens ----------
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ---------- Category ----------
class CategoryOut(BaseModel):
    id: int
    name: str
    image: Optional[str] = None

    class Config:
        from_attributes = True


class CategoryIDName(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


# ---------- Language ----------
class LanguageOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# ---------- Profile Update ----------
class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    languages: Optional[List[int]] = None  # language IDs only


# ---------- Profile Response ----------
class UserProfileResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    mobile: str
    profile_image: Optional[str]
    bio: Optional[str]
    languages: List[LanguageOut] = []

    class Config:
        from_attributes = True


# ---------- Minimal User Response ----------
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    mobile: str
    profile_image: Optional[str] = None
    register_type: Optional[str] = None
    languages: Optional[List[LanguageOut]] = None

    class Config:
        from_attributes = True


# ---------- Auth Response ----------
class AuthResponse(BaseModel):
    IsSucces: bool
    message: Optional[str]
    access_token: Optional[str]
    refresh_token: Optional[str]
    token_type: str = "bearer"
    user: Optional[Union[UserResponse, UserProfileResponse]]


# ---------- Base Response ----------
class BaseResponse(BaseModel):
    IsSucces: bool
    message: Optional[str] = None
    data: Optional[dict] = None


# ---------- Token Refresh ----------
class TokenRefreshRequest(BaseModel):
    refresh_token: str


# ---------- User Location ----------
class UserLocation(BaseModel):
    latitude: float
    longitude: float
    radius_km: Optional[float] = None  # optional filtering
"""
"""from pydantic import BaseModel, EmailStr
from typing import Optional, List, Union

# ---------- Registration ----------
# ---------- Registration ----------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    mobile: str
    password: str
    profile_image: Optional[str] = None
    register_type: str  # manual / social


# ---------- Login ----------
class UserLogin(BaseModel):
    email: EmailStr
    password: Optional[str] = None  # optional for social login


# ---------- Tokens ----------
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ---------- Category ----------
class CategoryOut(BaseModel):
    id: int
    name: str
    image: str

    class Config:
        from_attributes = True


class CategoryIDName(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


# ---------- Language ----------
class LanguageOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# ---------- Profile Update ----------
class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    interests: Optional[List[str]] = None  # category IDs
    languages: Optional[List[str]] = None  # language IDs


# ---------- Profile Response ----------
class UserProfileResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    mobile: str
    latitude: Optional[float]
    longitude: Optional[float]
    profile_image: Optional[str]
    bio: Optional[str]
    interests: List[CategoryOut] = []
    languages: List[LanguageOut] = []

    class Config:
        from_attributes = True


# ---------- Minimal User Response ----------
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    mobile: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    profile_image: Optional[str] = None
    register_type: Optional[str] = None
    interests: Optional[List[CategoryOut]] = None

    class Config:
        from_attributes = True


# ---------- Auth Response ----------
class AuthResponse(BaseModel):
    IsSucces: bool
    message: Optional[str]
    access_token: Optional[str]
    refresh_token: Optional[str]
    token_type: str = "bearer"
    user: Optional[Union[UserResponse, UserProfileResponse]]


# ---------- Base Response ----------
class BaseResponse(BaseModel):
    IsSucces: bool
    message: Optional[str] = None
    data: Optional[dict] = None


# ---------- Token Refresh ----------
class TokenRefreshRequest(BaseModel):
    refresh_token: str


# ---------- User Location ----------
class UserLocation(BaseModel):
    latitude: float
    longitude: float
    radius_km: Optional[float] = None  # optional filtering
"""
=======
from pydantic import BaseModel, EmailStr
from typing import Optional, List


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    mobile: str
    password: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    profile_image: Optional[str] = None
    interest: List[str]  # Category names instead of IDs


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# Full category output schema: id, name, image
class CategoryOut(BaseModel):
    id: int
    name: str
    image: str

    class Config:
        from_attributes = True  # Enables ORM compatibility


# Category id and name only
class CategoryIDName(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    mobile: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    profile_image: Optional[str] = None
    interests: List[CategoryOut] = []

    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    IsSucces: bool
    message: Optional[str]
    access_token: Optional[str]
    refresh_token: Optional[str]
    token_type: str = "bearer"
    user: Optional[UserResponse]

class BaseResponse(BaseModel):
    IsSucces: bool
    message: Optional[str] = None
    data: Optional[dict] = None

class TokenRefreshRequest(BaseModel):
    refresh_token: str
>>>>>>> 4f4447a70f4a774e40751869788c5d0086421b94
