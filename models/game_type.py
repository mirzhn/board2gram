
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class GameType(Base):
    __tablename__ = 'game_type'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

    game_type_card = relationship('GameTypeCard', back_populates='game_type')
    game = relationship('Game', back_populates='game_type')