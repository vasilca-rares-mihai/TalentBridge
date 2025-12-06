from core.sql_models import *
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete


def list_athletes(db: Session, skip: int, limit: int) -> List[Athlete]:
    stms = select(Athlete).offset(skip).limit(limit)
    return db.scalars(stms).all()