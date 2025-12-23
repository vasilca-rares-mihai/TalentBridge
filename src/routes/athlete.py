from fastapi import FastAPI, APIRouter, Depends

from typing import List
from schemas.schemas import AthleteBase
from crud import data_access
from utils.enums import GenderEnum, PositionsEnum, WeakFootEnum
from core.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import Optional

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

#insert a new athlete into db
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

#delete an athlete
@router.delete("/athlete_delete/${athlete_id}", summary="Delete athlete from athlete table")
def delete_athlete(athlete_id: int, db: Session = Depends(get_db)):
    try:
        athlete = data_access.get_athlete_by_id(db, athlete_id)
        if athlete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The athlete to be deleted was not found."
            )
        data_access.delete_from_attribute_table(db, athlete_id)
        data_access.delete_from_challenge_result_table(db, athlete_id)
        data_access.delete_from_athlete_table(db, athlete_id)
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Athlete delete error (api.py)"
        )

#search athlete by filter
@router.get("/athletes/search", response_model=List[AthleteBase], summary= "*FOOTBALL CLUB ONLY* Search athlete by filters")
def search_athletes(db: Session = Depends(get_db), field_position: Optional[PositionsEnum] = None, age: Optional[int] = None, gender: Optional[GenderEnum] = None, weak_foot: Optional[WeakFootEnum] = None, height: Optional[float] = None, weight: Optional[float] = None, country: Optional[str] = None):

    try:
        athletes = data_access.list_athletes_by_filter(db, field_position, age, gender, weak_foot, height, weight, country)
        if athletes is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="athletes not found"
            )
        return athletes
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
