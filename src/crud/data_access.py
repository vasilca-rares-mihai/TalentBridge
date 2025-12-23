from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import select
from models.sql_models import Athlete, Attribute, ChallengeResult

#....................................................athletes utils
def list_athletes(db: Session) -> List[Athlete]:
    stms = select(Athlete)
    return db.scalars(stms).all()

def create_athlete(db: Session, athlete: Athlete):
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
        email = athlete.email,
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

#................................attribute
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


def delete_from_attribute_table(db: Session, id_athlete: int):
    stms = select(Attribute).where(Attribute.athlete_id == id_athlete)
    existing_result = db.scalars(stms).first()
    if existing_result:
        db.delete(existing_result)
        db.commit()



#.................................challenge result
def delete_from_challenge_result_table(db: Session, id_athlete: int):
    stms = select(ChallengeResult).where(ChallengeResult.athlete_id == id_athlete)
    existing_result = db.scalars(stms).first()
    if existing_result:
        db.delete(existing_result)
        db.commit()