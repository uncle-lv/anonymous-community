from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    avatar_url: str
    email: EmailStr
    
    
class UserCreate(UserBase):
    password: str
    

class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(UserBase):
    id: int
    
    class Config:
        orm_mode = True
        
        
class SecretBase(BaseModel):
    content: str
    

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []
    

class SecretBase(BaseModel):
    pass


class SecretCreate(BaseModel):
    content: str
    

class SecretUpdate(SecretBase):
    content: str


class SecretOut(SecretBase):
    id: int
    creator: str
    content: str
    created_time: datetime
    modified_time: Optional[datetime] = None
    
    
class CommentBase(BaseModel):
    belong_to: int
    content: str
    
    
class CommentOut(CommentBase):
    id: int
    creator: str
    created_time: datetime
    modified_time: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        

class CommentUpdate(BaseModel):
    content: str
