from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from db import engine

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String)
    message = Column(String)
    response = Column(String)

Base.metadata.create_all(engine)