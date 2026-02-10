from typing import List, Optional

from fastapi import APIRouter, FastAPI, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from shared.core.database import get_db
from shared.crud import data_access
from shared.crud.security import get_current_user
from shared.schemas.schemas import AthleteBase, AthleteSearched
from shared.utils.enums import PositionsEnum, GenderEnum, WeakFootEnum

app = FastAPI()
router = APIRouter(prefix="/api/football_club", tags=["FootballClub"])

@router.get("/compare/athletes", summary="FOOTBALL CLUB: Compare 2 athletes")
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

@router.post("/search/athlete", summary= "FOOTBALL CLUB & ADMIN: Search an athlete by filters")
def search_athletes(athlete_searched: AthleteSearched, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin" and current_user.get("role") != "football_club":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don t have access to search athletes"
        )
    try:
        athletes = data_access.list_athletes_by_filter(db, athlete_searched)
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


@router.delete("/delete/football_club/{user_id}", summary="Delete football_club")
def delete_football_club(id_football_club: int,  db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        user = data_access.find_user_by_id(db, id_football_club)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user not found"
            )
        football_club = data_access.get_football_club_by_id(db, id_football_club)
        if current_user.get("role") != "admin" and football_club.user_id != int(current_user.get("sub")):
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
        data_access.delete_from_users_table(db, user.email)
        db.commit()

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


