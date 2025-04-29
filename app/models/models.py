"""SQLAlchemy models"""
from sqlalchemy import Table, Integer, String, Column, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from datetime import datetime
Base = declarative_base()

friends_association = Table(
    "friends_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user_profile.id"), primary_key=True),
    Column("friend_id", Integer, ForeignKey("user_profile.id"), primary_key=True)
)

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    profile = relationship("UserProfile", back_populates="user", uselist=False)


class UserProfile(Base):
    __tablename__ = "user_profile"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    avatar = Column(String)
    nickname = Column(String, default="user")
    online_status = Column(Boolean, default=func.now())
    last_seen = Column(DateTime, default=datetime.now())

    user = relationship("Users", back_populates="profile")
    friends = relationship("UserProfile",
                           secondary=friends_association,
                           primaryjoin=id == friends_association.c.user_id,
                           secondaryjoin=id == friends_association.c.friend_id,
                           backref="friend_of")
