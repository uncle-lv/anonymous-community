from typing import List
from fastapi import (FastAPI, Depends, status, Request, Body, HTTPException)
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.orm import Session
from fastapi_jwt_auth.auth_jwt import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

import crud
from db import (database, get_db)
from schemas import (SecretCreate, SecretOut, UserCreate, UserLogin, UserOut)
from security import EXPIRES_TIME, authenticate_user, get_active_user, get_current

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
async def get_user_by_id(id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, id)
    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')
    
    return db_user


@app.get('/api/users', response_model=List[UserOut])
async def get_users(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip, limit)
    return users


@app.post('/api/token')
async def obtain_token(login_user: UserLogin, auth: AuthJWT = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(login_user.username, login_user.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password'
        )
        
    access_token = auth.create_access_token(subject=user.username, expires_time=EXPIRES_TIME, fresh=True)
    refresh_token = auth.create_refresh_token(subject=user.username)
    crud.update_last_login(db, user.id)
    
    return {
        'token_type': 'Bearer', 
        'access_token': access_token, 
        'refresh_token': refresh_token
        }


@app.post('/api/token/refresh')
async def refresh_token(auth: AuthJWT = Depends()):
    auth.jwt_refresh_token_required()
    current_user = auth.get_jwt_subject()
    new_access_token = auth.create_access_token(subject=current_user)
    
    return {
        'token_type': 'Bearer',
        'access_token': new_access_token
            }


@app.get('/api/token/current_user', response_model=UserOut)
async def get_current_user(auth: AuthJWT = Depends(), db: Session = Depends(get_db)):
    try:
        user = get_current(auth=auth, db=db)
        
    except HTTPException as e:
        raise e
    
    return user
        
        
@app.post('/api/secrets')
async def create_secret(secret: SecretCreate, auth: AuthJWT = Depends(), db: Session = Depends(get_db)):
    auth.jwt_required()
    
    current_username = auth.get_jwt_subject()
    user = crud.get_user_by_username(db, current_username)
    return crud.create_secret(db, secret, user.id)

@app.get('/api/secrets')
async def get_secrets(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    secrets = crud.get_secrets(db, skip, limit)
    return secrets

@app.patch('/api/secrets/{id}', response_model=SecretOut)
async def update_secret(id: int, content: str = Body(...), db: Session = Depends(get_db)):
    secret = crud.update_secret_content(db, id, content)
    return secret
