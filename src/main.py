from typing import List
from fastapi import (FastAPI, Depends, HTTPException)
from sqlalchemy.orm import Session

import crud
from db import (database, get_db)
from schemas import (UserCreate, UserOut)


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


@app.get('/users/', response_model=List[UserOut])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip, limit)
    return users
