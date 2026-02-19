from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import relationship

from shared.core.database import Base

class Users(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)

    athlete_profile = relationship("Athlete", back_populates="user", uselist=False, cascade="all, delete-orphan")
    football_club_profile = relationship("FootballClub", back_populates="user", uselist=False, cascade="all, delete-orphan")