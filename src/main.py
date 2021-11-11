from typing import List
from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

import crud
import db
import schemas
import security
import models


app = FastAPI()

@app.on_event('startup')
async def startup():
    await db.database.connect()

@app.on_event('shutdown')
async def shutdown():
    await db.database.disconnect()

@app.post('/api/users', response_model=schemas.UserOut)
async def create_user(user: schemas.UserCreate, db: Session = Depends(db.get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail='Email already registered')
    
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail='Username already registered')
    
    return crud.create_user(db, user)


@app.get('/api/users/{id}', response_model=schemas.UserOut)
async def get_user_by_id(id: int, db: Session = Depends(db.get_db)):
    db_user = crud.get_user(db, id)
    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return db_user


@app.get('/api/users', response_model=List[schemas.UserOut])
async def get_users(skip: int = 0, limit: int = 50, db: Session = Depends(db.get_db)):
    users = crud.get_users(db, skip, limit)
    return users


@app.post('/api/token')
async def create_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db.get_db)):
    user = security.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
             headers={"WWW-Authenticate": "Bearer"}
        )
        
    access_token = security.create_access_token(
        data={
            'username': user.username
            }
    )
    
    crud.update_last_login(db, user.id)
    return {
        'token_type': 'Bearer', 
        'access_token': access_token
        }


@app.get('/api/token/current_user', response_model=schemas.UserOut)
async def get_current_user(current_user: models.User = Depends(security.get_current_active_user)):
    return current_user


@app.post('/api/secrets')
async def create_secret(secret: schemas.SecretCreate, current_user: models.User = Depends(security.get_current_active_user), db: Session = Depends(db.get_db)):
    return crud.create_secret(db, secret, current_user.id)

@app.get('/api/secrets')
async def get_secrets(skip: int = 0, limit: int = 50, db: Session = Depends(db.get_db)):
    secrets = crud.get_secrets(db, skip, limit)
    return secrets


@app.patch('/api/secrets')
async def update_secret(secret: schemas.SecretUpdate, current_user: models.User = Depends(security.get_current_active_user), db: Session = Depends(db.get_db)):
    pass