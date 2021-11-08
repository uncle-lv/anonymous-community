from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import databases

from models import Base

DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/anonymous_community?charset=utf8mb4"
database = databases.Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

