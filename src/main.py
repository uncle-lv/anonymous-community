from datetime import timedelta
from typing import List
from fastapi import (FastAPI, Depends, status, HTTPException)
from sqlalchemy.orm import Session

import crud
from db import (database, get_db)
from models import User
from schemas import (UserCreate, UserLogin, UserOut)
from security import ACCESS_TOKEN_EXPIRE_MINUTES, Token, authenticate_user, create_access_token, get_current_active_user


app = FastAPI()

@app.on_event('startup')
async def startup():
    await database.connect()


@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post('/api/users/', response_model=UserOut)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail='Email already registered')
    
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail='Username already registered')
    
    return crud.create_user(db, user)


@app.get('/api/users/{id}/', response_model=UserOut)
async def read_user(id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, id)
    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')
    
    return db_user


@app.get('/api/users/', response_model=List[UserOut])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip, limit)
    return users


@app.post('/api/token/', response_model=Token)
async def login_for_access_token(login_user: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(login_user.username, login_user.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate: Bearer'}
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username},
        expires_delta=access_token_expires
    )
    
    return {'access_token': access_token, 'token_type': 'bearer'}


@app.get('/users/me/', response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

