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

chat_members = Table(
    "chat_members",
    Base.metadata,
    Column("chat_id", Integer, ForeignKey("group_chats.id"), primary_key=True),
    Column("profile_id", Integer, ForeignKey("user_profile.id"), primary_key=True)
)

class PrivateChat(Base):
    __tablename__ = "private_chats"

    id = Column(Integer, primary_key=True)
    user1_id = Column(Integer, ForeignKey("user_profile.id"), nullable=False)
    user2_id = Column(Integer, ForeignKey("user_profile.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    user1 = relationship("UserProfile", foreign_keys=[user1_id])
    user2 = relationship("UserProfile", foreign_keys=[user2_id])
    messages = relationship("PrivateMessage", back_populates="chat")

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")
    refresh_token = Column(String)

    profile = relationship("UserProfile", back_populates="user", uselist=False)


class GroupChat(Base):
    __tablename__ = "group_chats"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("user_profile.id"), nullable=False)
    chat_avatar = Column(String)
    chat_name = Column(String)

    owner = relationship("UserProfile", back_populates="owned_chats")
    members = relationship("UserProfile", secondary=chat_members, back_populates="chats")
    messages = relationship("GroupMessage", back_populates="chat")


class UserProfile(Base):
    __tablename__ = "user_profile"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    avatar = Column(String)
    nickname = Column(String, default="user")
    online_status = Column(Boolean, default=False)
    last_seen = Column(DateTime, default=func.now())

    user = relationship("Users", back_populates="profile")
    friends = relationship(
        "UserProfile",
        secondary=friends_association,
        primaryjoin=id == friends_association.c.user_id,
        secondaryjoin=id == friends_association.c.friend_id,
        backref="friend_of"
    )

    owned_chats = relationship("GroupChat", back_populates="owner")  # Владелец чатов
    chats = relationship("GroupChat", secondary=chat_members, back_populates="members")  # Участник чатов

class PrivateMessage(Base):
    __tablename__ = "private_messages"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("private_chats.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("user_profile.id"), nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now())

    chat = relationship("PrivateChat")
    sender = relationship("UserProfile")

class GroupMessage(Base):
    __tablename__ = "group_messages"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("group_chats.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("user_profile.id"), nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now())

    chat = relationship("GroupChat")
    sender = relationship("UserProfile")
