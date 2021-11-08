from sqlalchemy.orm import Session

from models import User
from schemas import UserCreate
from security import hash_password

def get_user(db: Session, id: int):
    return db.query(User).filter(User.id == id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 50):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    hashed_password = hash_password(user.password)
    db_user = User(email=user.email, username=user.username, hashed_password=hashed_password, avatar_url=user.avatar_url)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
