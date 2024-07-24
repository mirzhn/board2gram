from sqlalchemy import Column, Integer, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base

class Player(Base):
    __tablename__ = 'player'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id =  Column(Integer, ForeignKey('user.id'), nullable=False)
    game_id = Column(Integer, ForeignKey('game.id'), nullable=False)
    is_captain = Column(Boolean, nullable=False, default=False)

    game = relationship('Game', back_populates='player')
    user = relationship('User', back_populates='player')

    __table_args__ = (UniqueConstraint('game_id', 'user_id', name='player_game_user_uc'),) 
