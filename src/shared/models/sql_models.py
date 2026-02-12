from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum, BigInteger, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from shared.core.database import Base
from shared.utils.enums import GenderEnum, PositionsEnum, WeakFootEnum
from shared.schemas.schemas import AttributeUpdate


class Athlete(Base):
    __tablename__ = "athlete"
    __table_args__ = {'extend_existing': True}

    user_id = Column(BigInteger, ForeignKey('users.id'), primary_key=True)
    first_name = Column(String(100), nullable=False)
    second_name = Column(String(100), nullable=True)
    field_position = Column(Enum(PositionsEnum), nullable=False)
    weak_foot = Column(Enum(WeakFootEnum), nullable=False)
    age = Column(Integer, nullable=True)

    gender = Column(Enum(GenderEnum), nullable=True)

    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    country = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)

    user = relationship("Users", back_populates="athlete_profile")
    attributes = relationship("Attribute", back_populates="athlete", cascade="all, delete-orphan")
    results = relationship("ChallengeResult", back_populates="athlete", cascade="all, delete-orphan")
    applications = relationship("TrialApplications", back_populates="athlete")

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

    user_id = Column(BigInteger, ForeignKey("athlete.user_id"), nullable=False)
    challenge_id = Column(BigInteger, ForeignKey("challenge.id_challenge"), nullable=False)

    result_value = Column(Float, nullable=False)
    date_recorded = Column(Date, nullable=False)

    athlete = relationship("Athlete", back_populates="results")
    challenge = relationship("Challenge", back_populates="results")


class Attribute(Base):
    __tablename__ = "attribute"
    __table_args__ = {'extend_existing': True}

    user_id = Column(BigInteger, ForeignKey("athlete.user_id"), primary_key=True, nullable=False)

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


class FootballClub(Base):
    __tablename__ = 'football_club'
    __table_args__ = {'extend_existing': True}

    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    country = Column(String(255), nullable=False)

    user = relationship("Users", back_populates="football_club_profile")
    trials = relationship("Trial", back_populates="club")
    favorites = relationship("FavoriteAthlete", back_populates="club")

class FavoriteAthlete(Base):
    __tablename__ = 'favorite_athlete'
    __table_args__ = (UniqueConstraint('club_id', 'athlete_id', name='_club_athlete_uc'),)

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    club_id = Column(BigInteger, ForeignKey('football_club.user_id'), nullable=False)
    athlete_id = Column(BigInteger, ForeignKey('athlete.user_id'), nullable=False)

    club = relationship("FootballClub", back_populates="favorites")
    athlete = relationship("Athlete")


class Trial(Base):
    __tablename__ = 'trial'

    id_trial = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_club = Column(BigInteger, ForeignKey('football_club.user_id'), nullable=False)
    until_date = Column(Date, nullable=False)
    info = Column(String(255), nullable=False)
    requirements = Column(JSON, nullable=False)

    club = relationship("FootballClub", back_populates="trials")
    applications = relationship("TrialApplications", back_populates="trial", cascade="all, delete-orphan")


class TrialApplications(Base):
    __tablename__ = 'trial_applications'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    id_trial = Column(BigInteger, ForeignKey('trial.id_trial'), nullable=False)
    id_athlete = Column(BigInteger, ForeignKey('athlete.user_id'), nullable=False)

    trial = relationship("Trial", back_populates="applications")
    athlete = relationship("Athlete")
