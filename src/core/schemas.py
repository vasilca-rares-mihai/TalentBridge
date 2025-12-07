from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional, List
from datetime import date
from enum import Enum
import re

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
    first_name: str = Field(..., min_length=1)
    second_name: str = Field(..., min_length=1)

    age: int

    gender: GenderEnum

    height: float
    weight: float
    country: str = Field(..., min_length=1)
    region: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)

    email: str

    phone_number: str = Field(..., min_length=1)
    date_of_birth: date



    @field_validator('height')
    @classmethod
    def height_validator(cls, v):
        if v < 0 or v > 3:
            raise ValueError("Height incorrect format")
        return v

    @field_validator('email')
    @classmethod
    def email_validator(cls, v):
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, v):
            raise ValueError("Email incorrect format (ex: nume@domeniu.com)")
        return v



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

