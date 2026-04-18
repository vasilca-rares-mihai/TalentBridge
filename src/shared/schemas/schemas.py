from pydantic import BaseModel, EmailStr, field_validator, Field, model_validator
from typing import Optional, List, Any, Dict
from datetime import date
from shared.utils.enums import GenderEnum, PositionsEnum, WeakFootEnum, RolesEnum
import re



############################
class ChallengeBase(BaseModel):
    challenge_name: str
    unit_of_measure: str
    info: str


class ChallengeCreate(ChallengeBase):
    pass


class Challenge(ChallengeBase):

    class Config:
        from_attributes = True

##########################################

class ChallengeResultBase(BaseModel):
    result_value: float
    date_recorded: date
    status: str



class ChallengeResultCreate(ChallengeResultBase):
    user_id: int
    challenge_id: int


class ChallengeResult(ChallengeResultBase):
    id_result: int
    class Config:
        from_attributes = True

##############################################################################

class AttributeBase(BaseModel):
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

class AttributeUpdate(BaseModel):
    acceleration: Optional[int] = None
    sprint_speed: Optional[int] = None
    finishing: Optional[int] = None
    shot_power: Optional[int] = None
    long_shots: Optional[int] = None
    penalties: Optional[int] = None
    short_pass: Optional[int] = None
    long_pass: Optional[int] = None
    agility: Optional[int] = None
    balance: Optional[int] = None
    ball_control: Optional[int] = None
    dribbling: Optional[int] = None
    heading_acc: Optional[int] = None
    jumping: Optional[int] = None
    stamina: Optional[int] = None
    strength: Optional[int] = None

class Attribute(AttributeBase):
    user_id: int

    class Config:
        from_attributes = True

##################################################

class AthleteBase(BaseModel):
    first_name: str = Field(..., min_length=1)
    second_name: str = Field(..., min_length=1)
    age: int
    field_position: PositionsEnum
    weak_foot: WeakFootEnum
    gender: GenderEnum
    height: float
    weight: float
    country: str = Field(..., min_length=1)
    region: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    phone_number: str = Field(..., min_length=1)
    date_of_birth: date

    @model_validator(mode='after')
    def verify_age_match(self) -> 'Athlete':
        dob = self.date_of_birth
        today = date.today()
        calculated_age = today.year - dob.year - (
                (today.month, today.day) < (dob.month, dob.day)
        )
        if self.age != calculated_age:
            raise ValueError(
                f"age ({self.age}) does not match birthdate (should be {calculated_age}))"
            )
        return self

    @field_validator('height')
    @classmethod
    def height_validator(cls, v):
        if v < 0 or v > 3:
            raise ValueError("Height incorrect format, Value must be between 0 and 3")
        return v
    @field_validator('weight')
    @classmethod
    def weight_validator(cls, v):
        if v < 0 or v > 180:
            raise ValueError("Weight incorrect format, Value must be between 0 and 180)")
        return v

class AthleteUpdate(BaseModel):
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    field_position: Optional[PositionsEnum] = None
    weak_foot: Optional[WeakFootEnum] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    @field_validator('field_position', 'weak_foot', 'date_of_birth', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

class AthleteSearched(BaseModel):
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    gender: Optional[GenderEnum] = None
    field_position: Optional[PositionsEnum] = None
    weak_foot: Optional[WeakFootEnum] = None
    country: Optional[str] = None

    age_range: Optional[List[Optional[int]]] = Field(default=None, min_items=2, max_items=2)
    height_range: Optional[List[Optional[float]]] = Field(default=None, min_items=2, max_items=2)
    weight_range: Optional[List[Optional[float]]] = Field(default=None, min_items=2, max_items=2)
    @field_validator('field_position', 'weak_foot', 'gender', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v


class FootballClubSearched(BaseModel):
    name: str
    country: str

class Athlete(AthleteBase):
    user_id: int

    attributes: List[Attribute] = []
    results: List[ChallengeResult] = []

    class Config:
        from_attributes = True

########################################
class FootballClubBase(BaseModel):
    name: str
    country: Optional[str] = None
    info: str

###############################

class FavoriteAthlete(BaseModel):
    club_id: int
    athlete_id: int



class Trial(BaseModel):
    until_date: date
    info: str
    requirements: AttributeUpdate

class TrialResponse(Trial):
    id_trial: int
    football_club: str
    country: str

    class Config:
        from_attributes = True

class TrialApplications(BaseModel):
    id_trial: int
    id_athlete: int

class Challenges(BaseModel):
    pullup: int
    squat: int
    pushup: int
    treadmill: int
    vjump: int

class CreateAthleteRequest(BaseModel):
    email: str
    password: str
    athlete_data: AthleteBase

class CreateFootballClubRequest(BaseModel):
    email: str
    password: str
    club_data: FootballClubBase

class LoginData(BaseModel):
    email: str
    password: str


class CountResponse(BaseModel):
    athleteCount: int
    footballClubCount: int
    analysisCount: int
    challengesCount: int
    trialsCount: int
    favoriteAthCount: int
    trialApplicationsCount: int

