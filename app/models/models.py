"""SQLAlchemy models"""
from sqlalchemy import Table, Integer, String, Column, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from datetime import datetime
Base = declarative_base()

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")
    refresh_token = Column(String)

    profile = relationship("UserProfile", back_populates="user", uselist=False)

class UserProfile(Base):
    __tablename__ = "user_profile"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    unique_name = Column(String,unique=True)
    avatar = Column(String)
    nickname = Column(String, default="user")
    online_status = Column(Boolean, default=False)
    last_seen = Column(DateTime, default=func.now())

    user = relationship("Users", back_populates="profile")

