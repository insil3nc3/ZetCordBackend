"""JWT and security"""
from datetime import datetime, timedelta, UTC
from jose import jwt

def create_access_token(data: dict, private_key: str, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, private_key, algorithm="RS256")
    return encoded_jwt

def verify_token(token: str, public_key: str):
    payload = jwt.decode(token, public_key, algorithms=["RS256"])
    return payload

