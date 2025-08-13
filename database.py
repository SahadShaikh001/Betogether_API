<<<<<<< HEAD
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base  

SQLALCHEMY_DATABASE_URL = "sqlite:///./betogether.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
=======
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base  

SQLALCHEMY_DATABASE_URL = "sqlite:///./betogether.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
>>>>>>> 4f4447a70f4a774e40751869788c5d0086421b94
        db.close()