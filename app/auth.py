from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from jose import jwt
from datetime import datetime, timedelta


load_dotenv()


PWD_CTX = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = os.getenv('JWT_SECRET', 'replace_me')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
ACCESS_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '60'))


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return PWD_CTX.hash(password)


    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return PWD_CTX.verify(password, hashed)


    @staticmethod
    def create_access_token(data: dict, expires_delta: int = ACCESS_MINUTES):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return encoded_jwt


    @staticmethod
    def decode_token(token: str) -> dict:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload