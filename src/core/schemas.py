from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date
from enum import Enum

class GenderEnum(str, Enum):
    male = 'Male'
    female = 'Female'
    other = 'Other'
##########################################################
class ChallengeBase(BaseModel):
    challenge_name: str
    unit_of_measure: str


class ChallengeCreate(ChallengeBase):
    pass


class Challenge(ChallengeBase):
    id_challenge: int

    class Config:
        from_attributes = True

##########################################

class ChallengeResultBase(BaseModel):
    result_value: float
    date_recorded: date


class ChallengeResultCreate(ChallengeResultBase):
    athlete_id: int
    challenge_id: int


class ChallengeResult(ChallengeResultBase):
    id_result: int
    class Config:
        from_attributes = True

##############################################################################

class AttributeBase(BaseModel):
    date_calculated: date

    acceleration: int
    sprint_speed: int
    finishing: int
    shot_power: int
    long_shots: int
    penalties: int
    short_pass: int
    long_pass: int
    agility: int
    balance: int
    ball_control: int
    dribbling: int
    heading_acc: int
    jumping: int
    stamina: int
    strength: int


class AttributeCreate(AttributeBase):
    pass


class Attribute(AttributeBase):
    id_attribute: int
    athlete_id: int

    class Config:
        from_attributes = True

##################################################

class AthleteBase(BaseModel):
    first_name: str
    second_name: Optional[str] = None

    age: Optional[int] = None

    gender: Optional[GenderEnum] = None

    height: Optional[float] = None
    weight: Optional[float] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None

    email: Optional[str] = None

    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None


class AthleteCreate(AthleteBase):
    first_name: str
    pass


class AthleteUpdate(BaseModel):
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[GenderEnum] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None


class Athlete(AthleteBase):
    id_athlete: int

    attributes: List[Attribute] = []
    results: List[ChallengeResult] = []

    class Config:
        from_attributes = True