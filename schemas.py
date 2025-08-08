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
