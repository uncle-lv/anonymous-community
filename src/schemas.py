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
    