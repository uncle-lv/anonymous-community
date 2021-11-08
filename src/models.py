from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Column, Integer, String, DateTime, Boolean, Text)

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(32), unique=True)
    avatar_url = Column(Text)
    email = Column(String(32), unique=True)
    hashed_password = Column(String(80), nullable=False)
    last_login = Column(DateTime, nullable=True)
    banned = Column(Boolean, default=False)
