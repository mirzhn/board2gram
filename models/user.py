import datetime
from sqlalchemy import Column, Integer, String, DateTime
from .base import Base

class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String)
    name = Column(String)
    dt = Column(DateTime, default=datetime.datetime.now())
