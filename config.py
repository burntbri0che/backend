import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "postgresql://postgres:password@localhost:5432/test_api"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#jwt
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-with-at-least-32-characters")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
