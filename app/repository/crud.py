"""temporarily: file to get some information from DB"""
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.models.models import Users

base_url = "postgresql://user_user:user@localhost:5432/user_db"
engine = create_engine(base_url)
Session = sessionmaker(engine)
session = Session()
users = session.query(Users).all()
for user in users:
    print(f"id: {user.id}")
    print(f"email: {user.email}")
    print(f"password: {user.hashed_password}")
    print(f"role: {user.role}")
    print(f"refresh_token: {user.refresh_token}")
#     session.delete(user)
#
# session.commit()