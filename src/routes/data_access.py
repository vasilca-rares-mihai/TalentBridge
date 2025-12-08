from core.sql_models import *
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from core.schemas import AthleteCreate


def list_athletes(db: Session, skip: int, limit: int) -> List[Athlete]:
    stms = select(Athlete).offset(skip).limit(limit)
    return db.scalars(stms).all()

def get_workout_type(db: Session, id_challenge: int) -> str:
    stms = select(Challenge.challenge_name).where(Challenge.id_challenge == id_challenge)
    return db.scalars(stms).one()

def get_athlete_by_id(db: Session, athlete_id: int) -> Athlete:
    stms = select(Athlete).where(Athlete.id_athlete == athlete_id)
    return db.scalars(stms).first()

def create_athlete(db: Session, athlete: AthleteCreate):
    new_athlete = Athlete(
        first_name= athlete.first_name,
        second_name = athlete.second_name,
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
    return new_athlete
