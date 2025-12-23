from fastapi import FastAPI, APIRouter, Depends

from typing import List
from schemas.schemas import AthleteBase
from crud import data_access
from core.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

app = FastAPI()
router = APIRouter(prefix="/api/athlete", tags=["Athlete"])

@router.get("/athletes", response_model=List[AthleteBase], summary="*ADMIN ONLY* Get all athletes")
def get_athletes(db: Session = Depends(get_db)):
    try:
        athletes = data_access.list_athletes(db)
        return athletes
    except Exception as e:
        print(f"error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eroare server: {e}"
        )


@router.post("/athletes", response_model=AthleteBase, summary="Create a new athlete")
def insert_athlete_db(athlete_data: AthleteBase, db: Session = Depends(get_db)):
    try:
        athlete = data_access.create_athlete(db, athlete_data)
        return athlete
    except IntegrityError as e:
        db.rollback()
        print(f"error: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="phone number or email already exists"
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Athlete create error (api.py)"
        )
