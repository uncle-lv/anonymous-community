from typing import List
from fastapi import (FastAPI, Depends, status, Request, HTTPException)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi_jwt_auth.auth_jwt import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

from loguru import logger

import crud
from db import (database, get_db)
from schemas import (UserCreate, UserLogin, UserOut)
from security import EXPIRES_TIME, authenticate_user


app = FastAPI()

@app.on_event('startup')
async def startup():
    await database.connect()


@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()
    
    
@app.exception_handler(AuthJWTException)
def authjwt_excaption_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={'detail': exc.message}
    )
    

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post('/api/users', response_model=UserOut)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail='Email already registered')
    
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail='Username already registered')
    
    return crud.create_user(db, user)


@app.get('/api/users/{id}', response_model=UserOut)
async def read_user(id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, id)
    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')
    
    return db_user


@app.get('/api/users', response_model=List[UserOut])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip, limit)
    return users


@app.post('/api/token')
async def login_for_access_token(login_user: UserLogin, auth: AuthJWT = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(login_user.username, login_user.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password'
        )
        
    access_token = auth.create_access_token(subject=user.username, expires_time=EXPIRES_TIME, fresh=True)
    refresh_token = auth.create_refresh_token(subject=user.username)
    
    return {
        'token_type': 'Bearer', 
        'access_token': access_token, 
        'refresh_token': refresh_token
        }


@app.post('/api/token/refresh')
def refresh(auth: AuthJWT = Depends()):
    auth.jwt_refresh_token_required()
    current_user = auth.get_jwt_subject()
    new_access_token = auth.create_access_token(subject=current_user)
    
    return {
        'token_type': 'Bearer', 
        'access_token': new_access_token
            }


@app.get('/api/token/users', response_model=UserOut)
def user(auth: AuthJWT = Depends(), db: Session = Depends(get_db)):
    auth.jwt_optional()

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
