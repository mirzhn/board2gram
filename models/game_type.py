
from sqlalchemy import Column, Integer, String
from .base import Base

class GameType(Base):
    __tablename__ = 'game_type'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
