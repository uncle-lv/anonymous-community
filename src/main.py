from typing import List
from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from loguru import logger
from starlette.status import HTTP_404_NOT_FOUND

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
    secrets = []
    result = crud.get_secrets(db, skip, limit)
    
    for row in result:
        secret = schemas.SecretOut(
            id=row['id'],
            creator=row['username'],
            content=row['content'],
            created_time=row['created_time'],
            modified_time=row['modified_time']
        )
        secrets.append(secret)
    
    return secrets


@app.get('/api/secrets/{id}')
async def get_secret_by_id(id: int, db: Session = Depends(db.get_db)):
    comments = []
    
    result = crud.get_comments(db, id, 0, 50)
    for row in result:
        comment = schemas.CommentOut(
            id=row['id'],
            creator=row['username'],
            content=row['content'],
            created_time=row['created_time'],
            modified_time=row['modified_time']
        )
        comments.append(comment)
        
    result_row = crud.get_secret(db, id)
    secret = schemas.SecretOut(
        id=result_row['id'],
        creator=result_row['username'],
        content=result_row['content'],
        created_time=result_row['created_time'],
        modified_time=result_row['modified_time'],
        comments=comments
        )
        
    return secret


@app.put('/api/secrets/{id}')
async def update_secret(secret: schemas.SecretUpdate, id: int, current_user: models.User = Depends(security.get_current_active_user), db: Session = Depends(db.get_db)):
    db_secret = crud.get_secret_by_id(db, id)
    creator = crud.get_user(db, db_secret.id)
    if creator.username != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials'
        )
    
    crud.update_secret_content(db, id, secret.content)
    return crud.get_secret(db, id)


@app.delete('/api/secrets/{id}')
async def del_secret(id: int, current_user: models.User = Depends(security.get_current_active_user), db: Session = Depends(db.get_db)):
    db_secret = crud.get_secret_by_id(db, id)
    
    if db_secret is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Secret not found'
        )
    
    creator = crud.get_user(db, db_secret.id)
    if creator.username != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials'
        )
        
    crud.del_secret(db, id)
    return {
        'msg': 'succeed'
    }
    
@app.post('/api/comments', response_model=schemas.CommentOut)
async def create_comment(comment: schemas.CommentBase, current_user: models.User = Depends(security.get_current_active_user), db: Session = Depends(db.get_db)):
    return crud.create_comment(db, comment, current_user.id)

@app.get('/api/comments/{belong_to}')
async def get_comments(belong_to: int, skip: int = 0, limit: int = 50, db: Session = Depends(db.get_db)):
    comments = []
    result = crud.get_comments(db, belong_to, skip, limit)
    
    for row in result:
        comment = schemas.SecretOut(
            id=row['id'],
            creator=row['username'],
            content=row['content'],
            created_time=row['created_time'],
            modified_time=row['modified_time']
        )
        comments.append(comment)
    
    return comments

@app.put('/api/comments/{id}')
async def update_comment(comment: schemas.CommentUpdate, id: int, current_user: models.User = Depends(security.get_current_active_user), db: Session = Depends(db.get_db)):
    db_comment = crud.get_comment(db, id)
    
    if db_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Comment not found'
        )
        
    creator = crud.get_user(db, db_comment.creator)
    if creator.username != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials'
        )
    
    crud.update_comment_content(db, id, comment.content)
    return crud.get_comment(db, id)

@app.delete('/api/comments/{id}')
async def del_comment(id: int, current_user: models.User = Depends(security.get_current_active_user), db: Session = Depends(db.get_db)):
    db_comment = crud.get_comment(db, id)
    
    if db_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Comment not found'
        )
    
    creator = crud.get_user(db, db_comment.creator)
    if creator.username != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials'
        )
        
    crud.del_comment(db, id)
    return {
        'msg': 'succeed'
    }
