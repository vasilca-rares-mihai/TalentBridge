from datetime import date
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, BigInteger, String, Integer, Float, Date, Enum
from database import Base


class Athlete(Base):
    __tablename__ = 'athlete'

    id_athlete = Column(BigInteger, primary_key=True, autoincrement=True)

    first_name = Column(String(100), nullable=False)
    second_name = Column(String(100))
    age = Column(Integer)
    gender = Column(Enum('Male', 'Female', 'Other'))
    height = Column(Float)
    weight = Column(Float)
    country = Column(String(100))
    region = Column(String(100))
    city = Column(String(100))
    email = Column(String(100))
    phone_number = Column(String(20))
    date_of_birth = Column(Date)


class AthleteBase(BaseModel):
    first_name: str
    second_name: Optional[str] = None
    age: int
    gender: str
    height: float
    weight: float
    country: str
    region: Optional[str] = None
    city: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: date


class AthleteCreate(AthleteBase):
    pass


class AthleteResponse(AthleteBase):
    id_athlete: int
    class Config:
        from_attributes = True