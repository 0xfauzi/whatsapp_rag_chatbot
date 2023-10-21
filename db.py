from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from decouple import config

url = URL.create(
    drivername="postgresql",
    username=config("DB_USER"),
    password=config("DB_PASSWORD"),
    host="localhost",
    database="chat_db",
    port=5432
)

engine = create_engine(url)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()