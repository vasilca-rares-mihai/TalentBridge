from fastapi import FastAPI, APIRouter, Depends

from typing import List
from schemas.schemas import AthleteBase
from crud import data_access
from utils.enums import GenderEnum, PositionsEnum, WeakFootEnum
from core.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, status
from typing import Optional
from crud.security import get_current_user

app = FastAPI()
router = APIRouter(prefix="/api/athlete", tags=["Athlete"])

@router.get("/athletes", response_model=List[AthleteBase], summary="*ADMIN ONLY* Get all athletes")
def get_athletes(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") not in ["admin", "football_club"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don t have acces to list of athletes."
        )
    try:
        athletes = data_access.list_athletes(db)
        if not athletes and athletes is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No athletes found."
            )
        return athletes
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )
    except HTTPException as e:
        return e
    except Exception as e:
        print(f"error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error: {e}"
        )

#insert a new athlete into db
@router.post("/athletes", response_model=AthleteBase, summary="Create a new athlete")
def insert_athlete_db(athlete_data: AthleteBase, email: str, db: Session = Depends(get_db)):
    try:
        athlete = data_access.create_athlete(db, athlete_data, email)
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
