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

@router.get("/athletes", response_model=List[AthleteBase], summary="*ADMIN OR FOOTBALL CLUB ACCESS* Get all athletes")
def get_athletes(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") not in ["admin", "football_club"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don t have access to list of athletes."
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
def insert_athlete_db(athlete_data: AthleteBase, email: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin" and email != current_user.get("email"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don t have access to create an other athlete",
        )
    try:
        athlete = data_access.create_athlete(db, athlete_data, email)
        return athlete
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig)
        print(error_msg)
        if "foreign key constraint fails" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to create athlete profile. user account does not exist"
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An athlete with this phone number or email already exists"
        )
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )
    except Exception as e:
        db.rollback()
        print(f"error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error: {e}"
        )

#search athlete by filter
@router.get("/athletes/search", response_model=List[AthleteBase], summary= "*ADMIN AND FOOTBALL CLUB ONLY* Search athlete by filters")
def search_athletes(db: Session = Depends(get_db), field_position: Optional[PositionsEnum] = None, age: Optional[int] = None, gender: Optional[GenderEnum] = None, weak_foot: Optional[WeakFootEnum] = None, height: Optional[float] = None, weight: Optional[float] = None, country: Optional[str] = None,  current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin" and current_user.get("role") != "football_club":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don t have access to search athletes"
        )
    try:
        athletes = data_access.list_athletes_by_filter(db, field_position, age, gender, weak_foot, height, weight, country)
        if athletes is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="athletes not found"
            )
        return athletes
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

def delete_athlete(email: str, db: Session = Depends(get_db)):
    try:
        athlete = data_access.find_athlete_by_email(db, email)
        data_access.delete_from_attribute_table(db, athlete.athlete_id)
        data_access.delete_from_challenge_result_table(db, athlete.athlete_id)
        data_access.delete_from_athlete_table(db, athlete.athlete_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Athlete delete error (api.py)"
        )