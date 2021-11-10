from datetime import timedelta
from fastapi import (Depends, status, HTTPException)
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from loguru import logger

from fastapi_jwt_auth import AuthJWT

import crud
from db import get_db
from models import User

EXPIRES_TIME = timedelta(days=1)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class Settings(BaseModel):
    authjwt_secret_key: str = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'


@AuthJWT.load_config
def get_config():
    return Settings()
    
    
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(raw_password: str, hashed_password):
    return pwd_context.verify(raw_password, hashed_password)

def authenticate_user(username: str, password: str, db: Session):
    user = crud.get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    
    return user

def get_current(auth: AuthJWT, db: Session):
    current_username = auth.get_jwt_subject() or None
    if current_username:
        user = crud.get_user_by_username(db, current_username)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token'
            )
        else:
            return user
        
def get_active_user(user: User = Depends(get_current)):
    if user.banned:
        raise HTTPException(
            status_code=400,
            detail='Banned user'
        )
    
    return user
