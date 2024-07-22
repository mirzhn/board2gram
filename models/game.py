import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base

class Game(Base):
    __tablename__ = 'game'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False)
    game_type_id = Column(Integer, ForeignKey('game_type.id'), nullable=False)
    start_dt = Column(DateTime, default=datetime.datetime.now())
    finish_dt = Column(DateTime)
  

    game_type = relationship('GameType', back_populates='game')
    player = relationship('Player', back_populates='game')
    round = relationship('Round', back_populates='game')

    __table_args__ = (UniqueConstraint('code', name='game_code_uc'),)