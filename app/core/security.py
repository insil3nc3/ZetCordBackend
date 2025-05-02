"""JWT and security"""
from datetime import datetime, timedelta, UTC

from fastapi import HTTPException
from jose import jwt
from passlib.context import CryptContext
# token
def create_token(data: dict, private_key_path: str, expires_delta: timedelta):
    to_encode = data.copy()  # Копируем входные данные
    expire = datetime.now(UTC) + expires_delta  # Устанавливаем срок действия токена
    to_encode.update({"exp": expire.timestamp()})  # Добавляем срок действия в payload
    with open(private_key_path, "r") as f:
        private_key = f.read()
    encoded_jwt = jwt.encode(to_encode, private_key, algorithm="RS256")  # Создаём JWT
    return encoded_jwt


def verify_token(token: str, public_key_path: str):
    with open(public_key_path, "r") as f:
        public_key = f.read()
    payload = jwt.decode(token, public_key, algorithms=["RS256"])
    expire_time = payload.get("exp")
    if datetime.now(UTC).timestamp() > expire_time:
        raise HTTPException(status_code=401, detail="Access token expired")
    # Декодируем токен
    return payload  # Возвращаем payload (данные) из токена


# password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """hashing password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """checks password on match with hash"""
    return pwd_context.verify(plain_password, hashed_password)

