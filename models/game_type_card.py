
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class GameTypeCard(Base):
    __tablename__ = 'game_type_card'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_type_id = Column(Integer, ForeignKey('game_type.id'), nullable=False)
    key = Column(String, nullable=False)
    value = Column(String)
  
    game_type = relationship('GameTypeCard', back_populates='game_type_card')