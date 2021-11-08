import re
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(raw_password: str, hashed_password):
    return pwd_context.verify(raw_password, hashed_password)

