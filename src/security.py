from typing import Optional
from datetime import (datetime, timedelta)
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi import (Depends, HTTPException, status)
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from fastapi_jwt_auth import AuthJWT

from db import get_db
from models import User
import crud

EXPIRES_TIME = timedelta(days=1)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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
