from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Users

base_url = "postgresql://user_user:user@localhost:5432/user_db"
engine = create_engine(base_url)
Session = sessionmaker(engine)
session = Session()

users = session.query(Users).all()
for user in users:
    print(user.id, user.email, user.hashed_password, user.profile, user.refresh_token)