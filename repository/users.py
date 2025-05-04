from typing import Optional, Generic, TypeVar
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi import HTTPException, status

T = TypeVar('T')

#users
class BaseRepository():
    @staticmethod
    def insert(db: Session, model: Generic[T]):
        try:
            db.add(model)
            db.commit()
            db.refresh(model)
            return model
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

class userRepository(BaseRepository):
    @staticmethod
    def get_user_by_username(db: Session, model: Generic[T], username: str):
        return db.query(model).filter(model.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, model: Generic[T], email: str):
        return db.query(model).filter(model.email == email).first()
    
    @staticmethod
    def create_user(db: Session, model: Generic[T], user_data: dict):
        # Check if username or email already exists
        if userRepository.get_user_by_username(db, model, user_data['username']):
            raise HTTPException(status_code=400, detail="Username already registered")
        if userRepository.get_user_by_email(db, model, user_data['email']):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        user = model(**user_data)
        return userRepository.insert(db, user)

#token   
class JWTRepo():
    @staticmethod
    def generate_token(data: dict, expires_delta: Optional[timedelta] = None):
        try:
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            return encoded_jwt
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating token: {str(e)}"
            )
    
    @staticmethod
    def decode_token(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload["exp"] < datetime.utcnow().timestamp():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error decoding token: {str(e)}"
            )
    

