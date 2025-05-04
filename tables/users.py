from sqlalchemy import Column, Integer, String, Boolean, DateTime
from config import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

