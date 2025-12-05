from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum, BigInteger
from sqlalchemy.orm import relationship
from core.database import Base
import enum


class GenderEnum(str, enum.Enum):
    Male = 'Male'
    Female = 'Female'
    Other = 'Other'


class Athlete(Base):
    __tablename__ = "athlete"
    __table_args__ = {'extend_existing': True}

    id_athlete = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    second_name = Column(String(100), nullable=True)
    age = Column(Integer, nullable=True)

    gender = Column(Enum(GenderEnum), nullable=True)

    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    country = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)

    attributes = relationship("Attribute", back_populates="athlete", cascade="all, delete-orphan")
    results = relationship("ChallengeResult", back_populates="athlete", cascade="all, delete-orphan")


class Challenge(Base):
    __tablename__ = "challenge"
    __table_args__ = {'extend_existing': True}
    id_challenge = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    challenge_name = Column(String(100), nullable=False, unique=True)
    unit_of_measure = Column(String(50), nullable=False)

    results = relationship("ChallengeResult", back_populates="challenge")


class ChallengeResult(Base):
    __tablename__ = "challenge_result"
    __table_args__ = {'extend_existing': True}
    id_result = Column(BigInteger, primary_key=True, index=True, autoincrement=True)

    athlete_id = Column(BigInteger, ForeignKey("athlete.id_athlete"), nullable=False)
    challenge_id = Column(BigInteger, ForeignKey("challenge.id_challenge"), nullable=False)

    result_value = Column(Float, nullable=False)
    date_recorded = Column(Date, nullable=False)

    athlete = relationship("Athlete", back_populates="results")
    challenge = relationship("Challenge", back_populates="results")


class Attribute(Base):
    __tablename__ = "attribute"
    __table_args__ = {'extend_existing': True}
    id_attribute = Column(BigInteger, primary_key=True, index=True, autoincrement=True)

    athlete_id = Column(BigInteger, ForeignKey("athlete.id_athlete"), nullable=False)

    date_calculated = Column(Date, nullable=False)

    acceleration = Column(Integer, nullable=True)
    sprint_speed = Column(Integer, nullable=True)
    finishing = Column(Integer, nullable=True)
    shot_power = Column(Integer, nullable=True)
    long_shots = Column(Integer, nullable=True)
    penalties = Column(Integer, nullable=True)
    short_pass = Column(Integer, nullable=True)
    long_pass = Column(Integer, nullable=True)
    agility = Column(Integer, nullable=True)
    balance = Column(Integer, nullable=True)
    ball_control = Column(Integer, nullable=True)
    dribbling = Column(Integer, nullable=True)
    heading_acc = Column(Integer, nullable=True)
    jumping = Column(Integer, nullable=True)
    stamina = Column(Integer, nullable=True)
    strength = Column(Integer, nullable=True)

    athlete = relationship("Athlete", back_populates="attributes")