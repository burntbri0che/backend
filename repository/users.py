from typing import Optional, Generic, TypeVar
from sqlalchemy.orm import Session

from datetime import datetime, timedelta
from jose import JWTError, jwt

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPBasicCredentials

T = TypeVar('T')


#users
class BaseRepository():
    @staticmethod
    def insert(db: Session, model: Generic[T]):
        db.add(model)
        db.commit()
        db.refresh(model)

class userRepository(BaseRepository):
    @staticmethod
    def get_user_by_username(db: Session, model: Generic[T], username: str):
        return db.query(model).filter(model.username == username).first()
 #token   
class JWTRepo():
    def generate_token(date: dict, expires_delta: Optional[timedelta] = None):
        to_encode = date.copy()
        if expires_delta:
            expire = datetime.now(datetime.timezone.utc) + expires_delta
        else:
            expire = datetime.now(datetime.timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def decode_token(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload if payload["exp"] >= datetime.now(datetime.timezone.utc) else None
        except JWTError:
            return {"error": "Token is invalid or expired"}
    

