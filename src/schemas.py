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
    token_type: str
    access_token: str
    

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []
    

class SecretBase(BaseModel):
    pass


class SecretCreate(BaseModel):
    content: str   


class SecretOut(SecretBase):
    id: str
    creator: str
    created_time: datetime
    modified_time: datetime
    
    
class Comment(BaseModel):
    id: int
    belong_to: int
    creator: int
    content: str
