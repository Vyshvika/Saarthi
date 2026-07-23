from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    base_level: str  # "foundation" | "growth" | "mastery"
    subject_focus: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    name: str
    base_level: str


class SessionOut(BaseModel):
    id: int
    title: str
    effective_level: str
    created_at: datetime

    class Config:
        from_attributes = True


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    level_at_response: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SendMessageRequest(BaseModel):
    session_id: int
    content: str
