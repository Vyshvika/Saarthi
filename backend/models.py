from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # base_level is set once at onboarding: "foundation" | "growth" | "mastery"
    base_level = Column(String, nullable=False, default="growth")
    subject_focus = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, default="New chat")
    created_at = Column(DateTime, default=datetime.utcnow)

    # effective_level can drift away from the user's base_level during a session
    effective_level = Column(String, nullable=False, default="growth")
    confusion_streak = Column(Integer, default=0)
    mastery_streak = Column(Integer, default=0)

    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" | "guide"
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # level the response was generated at (for evaluation / audit trail)
    level_at_response = Column(String, nullable=True)
    confusion_signal = Column(Boolean, default=False)
    mastery_signal = Column(Boolean, default=False)
    response_latency_ms = Column(Float, nullable=True)

    session = relationship("ChatSession", back_populates="messages")
