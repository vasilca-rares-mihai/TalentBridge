from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import select
from models.sql_models import Athlete, Attribute, ChallengeResult, Challenge, Users
from typing import Optional
from utils.enums import GenderEnum, PositionsEnum, WeakFootEnum
from datetime import date, timedelta

#....................................................athletes utils..........................................
def list_athletes(db: Session) -> List[Athlete]:
    stms = select(Athlete)
    return db.scalars(stms).all()

def create_athlete(db: Session, athlete: Athlete, email: str):
    new_athlete = Athlete(
        first_name= athlete.first_name,
        second_name = athlete.second_name,
        field_position = athlete.field_position,
        weak_foot = athlete.weak_foot,
        age = athlete.age,
        gender = athlete.gender,
        height = athlete.height,
        weight = athlete.weight,
        country = athlete.country,
        region = athlete.region,
        city = athlete.city,
        email = email,
        phone_number = athlete.phone_number,
        date_of_birth = athlete.date_of_birth,
    )

    db.add(new_athlete)
    db.commit()
    db.refresh(new_athlete)
    create_attribute(db, new_athlete.id_athlete)

    return new_athlete

def get_athlete_by_id(db: Session, athlete_id: int) -> Athlete:
    stms = select(Athlete).where(Athlete.id_athlete == athlete_id)
    return db.scalars(stms).first()


def delete_from_athlete_table(db: Session, id_athlete: int):
    stms = select(Athlete).where(Athlete.id_athlete == id_athlete)
    existing_result = db.scalars(stms).first()
    if existing_result:
        db.delete(existing_result)
        db.commit()


def list_athletes_by_filter(db: Session, field_position: Optional[PositionsEnum], max_age: Optional[int], gender: Optional[GenderEnum], weak_foot: Optional[WeakFootEnum], height: Optional[float], weight: Optional[float], country: Optional[str]) -> List[Athlete]:
    stms = select(Athlete)
    if weak_foot is not None:
        stms = stms.where(Athlete.weak_foot == weak_foot)
    if gender is not None:
        stms = stms.where(Athlete.gender == gender)
    if field_position is not None:
        stms = stms.where(Athlete.field_position == field_position)
    if max_age is not None:
        stms = stms.where(Athlete.age < max_age)
    if height:
        stms = stms.where(Athlete.height < height)
    if weight:
        stms = stms.where(Athlete.weight < weight)
    if country:
        stms = stms.where(Athlete.country == country)

    return db.scalars(stms).all()

def compare_athletes_stats(db: Session, id_athlete1: int, id_athlete2: int):
    athlete1 = get_athlete_by_id(db, id_athlete1)
    athlete2 = get_athlete_by_id(db, id_athlete2)

    if not athlete1 or not athlete2:
        return None
    if not athlete1.attributes or not athlete2.attributes:
        return {"error": "One of the athletes does not have the attributes set"}

    stats_to_compare = [
        "acceleration", "sprint_speed", "finishing", "shot_power", "long_shots", "penalties", "short_pass", "long_pass", "agility", "balance", "ball_control", "dribbling", "heading_acc", "jumping", "stamina", "strength"
    ]
    comparison_result = {}

    attribute1 = get_attribute_by_id(db, id_athlete1)
    attribute2 = get_attribute_by_id(db, id_athlete2)

    for stat in stats_to_compare:
        val1 = getattr(attribute1, stat, 0) or 0
        val2 = getattr(attribute2, stat, 0) or 0
        if val1 > val2:
            mesaj = f"{athlete1.first_name} e mai bun (+{val1 - val2})"
        elif val2 > val1:
            mesaj = f"{athlete2.first_name} e mai bun (+{val2 - val1})"
        else:
            mesaj = "Eq"

        comparison_result[stat] = mesaj

    comparison_result["athletes"] = {
        "athlete_1_name": athlete1.first_name,
        "athlete_2_name": athlete2.first_name
    }

    return comparison_result


#................................attribute.................................................................
def create_attribute(db: Session, id_athlete: int):
    attributes = Attribute(
        athlete_id= id_athlete,
        acceleration = 0,
        sprint_speed = 0,
        finishing = 0,
        shot_power = 0,
        long_shots = 0,
        penalties = 0,
        short_pass = 0,
        long_pass = 0,
        agility = 0,
        balance = 0,
        ball_control = 0,
        dribbling = 0,
        heading_acc = 0,
        jumping = 0,
        stamina = 0,
        strength = 0
    )
    db.add(attributes)
    db.commit()
    db.refresh(attributes)


def get_attribute_by_id(db: Session, athlete_id: int) -> Attribute:
    stms = select(Attribute).where(Attribute.athlete_id == athlete_id)
    return db.scalars(stms).one()


def delete_from_attribute_table(db: Session, id_athlete: int):
    stms = select(Attribute).where(Attribute.athlete_id == id_athlete)
    existing_result = db.scalars(stms).first()
    if existing_result:
        db.delete(existing_result)
        db.commit()

def update_attribute(db: Session, id_athlete: int, update_data: dict):
    db_attribute = get_attribute_by_id(db, id_athlete)
    if not db_attribute:
        return None
    for key, value in update_data.items():
        if key != "id" and value is not None:
            setattr(db_attribute, key, value)
    db.commit()
    db.refresh(db_attribute)
    return db_attribute



#.................................challenge result..........................................................
def delete_from_challenge_result_table(db: Session, id_athlete: int):
    stms = select(ChallengeResult).where(ChallengeResult.athlete_id == id_athlete)
    existing_result = db.scalars(stms).first()
    if existing_result:
        db.delete(existing_result)
        db.commit()

def create_challenge_result(db: Session, id_challenge: int, id_athlete: int, result: int):
    new_challenge_result = ChallengeResult(
        athlete_id = id_athlete,
        challenge_id = id_challenge,
        result_value = result,
        date_recorded = date.today()
    )
    limit_date = date.today() - timedelta(days=90)
    stms = select(ChallengeResult).where(ChallengeResult.athlete_id == id_athlete,  ChallengeResult.challenge_id == id_challenge)
    existing_result = db.scalars(stms).first()
    if existing_result:
        if existing_result.date_recorded > limit_date:
            return None
        db.delete(existing_result)
    db.add(new_challenge_result)
    db.commit()
    db.refresh(new_challenge_result)
    return new_challenge_result

#....................................challenge.....................................

def get_challenge_by_id(db: Session, id_challenge: int) -> str:
    stms = select(Challenge).where(Challenge.id_challenge == id_challenge)
    return db.scalars(stms).one()

def delete_from_challenge_table(db: Session, id_challenge: int):
    stms = select(Challenge).where(Challenge.id_challenge == id_challenge)
    existing_result = db.scalars(stms).first()
    if existing_result:
        db.delete(existing_result)
        db.commit()


def create_challenge(db: Session, challenge: Challenge):
    new_challenge = Challenge(
        challenge_name = challenge.challenge_name,
        unit_of_measure = challenge.unit_of_measure
    )
    db.add(new_challenge)
    db.commit()
    db.refresh(new_challenge)

#..........................user..........................
def create_user(db, email, password, role):
    new_user = Users(
        email= email,
        password_hash = password,
        role = role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
