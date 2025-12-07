from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from core.schemas import AthleteCreate, Athlete

from routes import data_access
from core.database import get_db
app = FastAPI()


@app.get("/athletes", response_model=List[Athlete], summary="Get all athletes from athlete table")
def get_athletes(db:Session = Depends(get_db), skip: int = 0, limit: int = 100):
    try:
        athletes = data_access.list_athletes(db, skip=skip, limit=limit)
        return athletes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Athlete load error (api.py)"
        )

@app.post("/athletes", response_model=Athlete, summary="Insert new athlete in DB")
def insert_athlete_db(athlete_data: AthleteCreate, db: Session = Depends(get_db)):
    try:
        athlete = data_access.create_athlete(db, athlete_data)
        return athlete
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="phone number or email already exists"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Athlete create error (api.py)"
        )



