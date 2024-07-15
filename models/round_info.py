from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from .base import Base

class RoundInfo(Base):
    __tablename__ = 'round_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    round_id = Column(Integer, ForeignKey('round.id'), nullable=False)
    key = Column(String, nullable=False)
    value = Column(String)

    game = relationship('Round', back_populates='round_info')
