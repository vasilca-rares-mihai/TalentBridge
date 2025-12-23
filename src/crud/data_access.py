from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.sql_models import Athlete

#athletes utils
def list_athletes(db: Session) -> List[Athlete]:
    stms = select(Athlete)
    return db.scalars(stms).all()



