from datetime import datetime
from sqlalchemy.orm import Session

from models import Comment, Secret, User
from schemas import SecretCreate, UserCreate
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
    db_user = User(email=user.email, username=user.username, hashed_password=hashed_password, avatar_url=user.avatar_url, created_time=datetime.now())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_last_login(db: Session, id: int):
    db.query(User).filter(User.id == id).update(dict(last_login=datetime.now()))
    db.commit()
    
def create_secret(db: Session, secret: SecretCreate, user_id: int):
    db_secret = Secret(creator=user_id, content=secret.content, created_time=datetime.now())
    db.add(db_secret)
    db.commit()
    db.refresh(db_secret)
    return db_secret

def get_secrets(db: Session, skip: int = 0, limit: int = 50):
    return db.query(Secret).offset(skip).limit(limit).all()

def get_secret(db: Session, id: int):
    return db.query(Secret).filter(Secret.id == id).first()

def update_secret_content(db: Session, id: int, new_content: str):
    db.query(Secret).filter(Secret.id == id).update(dict(content=new_content, modified_time=datetime.now()))
    db.commit()
