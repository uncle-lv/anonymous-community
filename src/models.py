from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Column, BigInteger, Integer, String, DateTime, Boolean, Text)
from sqlalchemy.sql.schema import ForeignKey

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(32), unique=True, nullable=False)
    avatar_url = Column(Text, nullable=False)
    email = Column(String(32), unique=True, nullable=False)
    hashed_password = Column(String(80), nullable=False)
    created_time = Column(DateTime, nullable=False)
    last_login = Column(DateTime, nullable=True)
    is_super = Column(Boolean, default=False, nullable=False)
    banned = Column(Boolean, default=False, nullable=False)
    

class Secret(Base):
    __tablename__ = 'secret'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    creator = Column(BigInteger, ForeignKey('user.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_time = Column(DateTime, nullable=False)
    modified_time = Column(DateTime)
    like_count = Column(Integer, default=0, nullable=False)
    hug_count = Column(Integer, default=0, nullable=False)
    banned = Column(Boolean, default=False, nullable=False)
    
    
class Comment(Base):
    __tablename__ = 'comment'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    belong_to = Column(BigInteger, ForeignKey('secret.id'), nullable=False)
    creator = Column(BigInteger, ForeignKey('user.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_time = Column(DateTime, nullable=False)
    modified_time = Column(DateTime)
    like_count = Column(Integer, default=0, nullable=False)
    banned = Column(Boolean, default=False, nullable=False)
