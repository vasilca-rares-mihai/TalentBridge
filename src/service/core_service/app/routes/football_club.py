from typing import List, Optional

from fastapi import APIRouter, FastAPI, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from shared.core.database import get_db
from shared.crud import data_access
from shared.crud.security import get_current_user
from shared.schemas.schemas import AthleteBase
from shared.utils.enums import PositionsEnum, GenderEnum, WeakFootEnum

app = FastAPI()
router = APIRouter(prefix="/api/football_club", tags=["FootballClub"])

@router.get("/athlete/compare", summary="*FOOTBALL CLUB ONLY* Compare 2 athletes")
def compare_athletes(id_athlete1: int, id_athlete2: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "football_club":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don t have access to compare 2 athletes"
        )
    try:
        stats = data_access.compare_athletes_stats(db, id_athlete1, id_athlete2)
        if stats is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="datele n au fost gasite"
            )
        return stats

    except SQLAlchemyError as e:
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
            detail="Server error"
        )

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


@router.delete("/delete/football_club", summary="Delete football_club")
def delete_football_club(id_football_club: int,  db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        football_club = data_access.get_football_club_by_id(db, id_football_club)
        if current_user.get("role") != "admin" and football_club.email != current_user.get("email"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don t have access to delete an football_club"
            )
        if football_club is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The football_club to be deleted was not found."
            )

        data_access.delete_from_football_club_table(db, id_football_club)
        data_access.delete_from_users_table(db, football_club.email)


    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="database error"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error"
        )


