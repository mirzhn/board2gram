from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Round(Base):
    __tablename__ = 'round'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey('game.id'), nullable=False)
    num = Column(Integer)

    game = relationship('Game', back_populates='round')
    round_info = relationship('RoundInfo', back_populates='round')