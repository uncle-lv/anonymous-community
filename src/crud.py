from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.sql.expression import bindparam
from sqlalchemy.sql.sqltypes import Integer

import schemas
import models
import security

def get_user(db: Session, id: int):
    return db.query(models.User).filter(models.User.id==id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email==email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username==username).first()

def get_users(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.hash_password(user.password)
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password, avatar_url=user.avatar_url, created_time=datetime.utcnow())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_last_login(db: Session, id: int):
    db.query(models.User).filter(models.User.id==id).update(dict(last_login=datetime.utcnow()))
    db.commit()
    
def create_secret(db: Session, secret: schemas.SecretCreate, user_id: int):
    db_secret = models.Secret(creator=user_id, content=secret.content, created_time=datetime.utcnow())
    db.add(db_secret)
    db.commit()
    db.refresh(db_secret)
    return db_secret

def get_secrets(db: Session, skip: int = 0, limit: int = 50):
    raw_sql = 'SELECT s.id, u.username, s.content, s.created_time, s.modified_time FROM secret s INNER JOIN user u ON s.creator = u.id LIMIT :limit OFFSET :offset'
    stat = text(raw_sql).bindparams(
        bindparam('offset', type_=Integer),
        bindparam('limit', type_=Integer)
    )
    return db.execute(stat, {'offset': skip, 'limit': limit}).fetchall()

def get_secret(db: Session, id: int):
    raw_sql = 'SELECT s.id, u.username, s.content, s.created_time, s.modified_time FROM secret s INNER JOIN user u ON s.creator = u.id WHERE s.id = :id'
    stat = text(raw_sql).bindparams(
        bindparam('id', type_=Integer)
    )
    return db.execute(stat, {'id': id}).first()
    
def get_secret_by_id(db: Session, id: int):
    return db.query(models.Secret).filter(models.Secret.id==id).first()

def update_secret_content(db: Session, id: int, content: str):
    db.query(models.Secret).filter(models.Secret.id==id).update(dict(content=content, modified_time=datetime.utcnow()))
    db.commit()
    
def del_secret(db: Session, id: int):
    db.query(models.Secret).filter(models.Secret.id==id).delete()
    db.commit()
    
def create_comment(db: Session, comment: schemas.CommentBase, user_id: int):
    db_comment = models.Comment(belong_to=comment.belong_to, creator=user_id, content=comment.content, created_time=datetime.utcnow())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_comments(db: Session, belong_to: int, skip: int = 0, limit: int = 50):
    raw_sql = 'SELECT c.id, u.username, c.content, c.created_time, c.modified_time FROM comment c INNER JOIN user u ON c.creator = u.id WHERE c.belong_to = :belong_to LIMIT :limit OFFSET :offset'
    stat = text(raw_sql).bindparams(
        bindparam('belong_to', type_=Integer),
        bindparam('offset', type_=Integer),
        bindparam('limit', type_=Integer)
    )
    return db.execute(stat, {'belong_to': belong_to, 'offset': skip, 'limit': limit}).fetchall()

def get_comment(db: Session, id: int):
    db_comment = db.query(models.Comment).filter(models.Comment.id==id).first()
    return db_comment

def update_comment_content(db: Session, id: int, content: str):
    db.query(models.Comment).filter(models.Comment.id==id).update(dict(content=content, modified_time=datetime.utcnow()))
    db.commit()
    
def del_comment(db: Session, id: int):
    db.query(models.Comment).filter(models.Comment.id==id).delete()
    db.commit()
