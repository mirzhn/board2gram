import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String)
    name = Column(String)
    dt = Column(DateTime, default=datetime.datetime.now())

    player = relationship('Player', back_populates='user')
