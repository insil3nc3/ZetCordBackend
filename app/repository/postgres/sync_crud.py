from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Users, UserProfile

base_url = "postgresql://user_user:user@localhost:5432/user_db"
engine = create_engine(base_url)
Session = sessionmaker(engine)
session = Session()

users = session.query(Users).all()
for user in users:
    print(user.id, user.email, user.hashed_password, user.refresh_token)
user_profiles = session.query(UserProfile).all()
for user_profile in user_profiles:
    print(user_profile.id, user_profile.user_id, user_profile.nickname, user_profile.unique_name, user_profile.avatar)