from typing import List
from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from loguru import logger

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


@app.post('/api/users', response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: Session = Depends(db.get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='Email already registered'
            )
    
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='Username already registered'
            )
    
    return crud.create_user(db, user)


@app.get('/api/users/{id}', response_model=schemas.UserOut, status_code=status.HTTP_200_OK)
async def get_user_by_id(id: int, db: Session = Depends(db.get_db)):
    db_user = crud.get_user(db, id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail='User not found'
            )
    return db_user


@app.get('/api/users', response_model=List[schemas.UserOut], status_code=status.HTTP_200_OK)
async def get_users(skip: int = 0, limit: int = 50, db: Session = Depends(db.get_db)):
    users = crud.get_users(db, skip, limit)
    return users


@app.post('/api/login/oauth/access_token', status_code=status.HTTP_201_CREATED)
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


@app.get('/api/token/current_user', response_model=schemas.UserOut, status_code=status.HTTP_200_OK)
async def get_current_user(current_user: models.User = Depends(security.get_current_active_user)):
    return current_user


@app.post('/api/secrets', response_model=schemas.SecretOut, status_code=status.HTTP_201_CREATED)
async def create_secret(secret: schemas.SecretCreate, current_user: models.User = Depends(security.get_current_active_user), db: Session = Depends(db.get_db)):
    return crud.create_secret(db, secret, current_user.id)


@app.get('/api/secrets', status_code=status.HTTP_200_OK)
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


@app.get('/api/secrets/{id}', status_code=status.HTTP_200_OK)
async def get_secret_by_id(id: int, db: Session = Depends(db.get_db)):
    comments = []
    
    result_row = crud.get_secret(db, id)
    if result_row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Secret not found'
        )
    
    secret = schemas.SecretOut(
        id=result_row['id'],
        creator=result_row['username'],
        content=result_row['content'],
        created_time=result_row['created_time'],
        modified_time=result_row['modified_time'],
        )
    
    result = crud.get_comments_belong_to(db, id, 0, 50)
    for row in result:
        comment = schemas.CommentOut(
            id=row['id'],
            creator=row['username'],
            content=row['content'],
            created_time=row['created_time'],
            modified_time=row['modified_time']
        )
        comments.append(comment)
        
    secret.comments = comments
        
    return secret


@app.patch('/api/secrets/{id}', status_code=status.HTTP_200_OK)
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


@app.delete('/api/secrets/{id}', status_code=status.HTTP_204_NO_CONTENT)
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
    return

    
@app.post('/api/comments', response_model=schemas.CommentOut, status_code=status.HTTP_201_CREATED)
async def create_comment(comment: schemas.CommentBase, current_user: models.User = Depends(security.get_current_active_user), db: Session = Depends(db.get_db)):
    return crud.create_comment(db, comment, current_user.id)


@app.get('/api/comments/{id}', response_model=schemas.CommentOut, status_code=status.HTTP_200_OK)
async def get_comment_by_id(id: int, db: Session = Depends(db.get_db)):
    db_comment = crud.get_comment(db, id)
    if db_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail='Comment not found'
            )
    return db_comment


@app.get('/api/comments/belong/{belong_to}', status_code=status.HTTP_200_OK)
async def get_comments_by_belong_to(belong_to: int, skip: int = 0, limit: int = 50, db: Session = Depends(db.get_db)):
    comments = []
    
    if crud.get_secret_by_id(db, belong_to) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Secret not found'
        )
    
    result = crud.get_comments_belong_to(db, belong_to, skip, limit)
    
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


@app.patch('/api/comments/{id}', status_code=status.HTTP_200_OK)
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


@app.delete('/api/comments/{id}', status_code=status.HTTP_204_NO_CONTENT)
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
    return
