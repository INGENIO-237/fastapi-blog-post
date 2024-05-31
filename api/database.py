from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_URL = "postgresql://postgres:postgres@localhost/fastapi_blog"

engine = create_engine(DB_URL)

SessionLocal = sessionmaker(autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
