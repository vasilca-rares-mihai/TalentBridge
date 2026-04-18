from typing import List, Optional

from fastapi import APIRouter, FastAPI, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import current_user
from sqlalchemy.testing.pickleable import User
from starlette import status

from shared.core.database import get_db
from shared.crud import data_access
from shared.crud.security import get_current_user
from shared.schemas.schemas import AthleteBase, AthleteSearched, FavoriteAthlete, Trial, FootballClubBase
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


@router.delete("/delete/football_club/{user_id}", summary="FOOTBALL CLUB & ADMIN: Delete football_club")
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
        data_access.delete_from_users_table(db, user.id_football_club)
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

@router.post("/scouting/watchlist/{athlete_id}", summary="FOOTBALL CLUB: add to watchlist")
def watchlist(athlete_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        athlete = data_access.get_athlete_by_id(db, athlete_id)
        if athlete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="athlete not found"
            )
        data_access.add_to_watchlist(db, int(current_user.get("sub")), athlete_id)

        db.commit()
        db.refresh(athlete)
        return athlete
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
            detail="server error"
        )


@router.delete("/scouting/watchlist/{athlete_id}", summary="FOOTBALL CLUB: delete from watchlist")
def watchlist_delete(athlete_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        athlete = data_access.get_athlete_by_id(db, athlete_id)
        if athlete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="athlete not found"
            )
        delete_state = data_access.delete_from_watchlist(db, int(current_user.get("sub")), athlete_id)

        db.commit()
        if delete_state:
            return f"Athlete {athlete.first_name} removed from watchlist"
        return f"Athlete {athlete.first_name} is in your football club's watchlist"
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
            detail="server error"
        )

@router.post("/publish/trial", summary="FOOTBALL CLUB: add to trial table")
def trial(trials: Trial, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        if current_user.get("role") != "football_club":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to do this action"
            )
        data_access.create_trial(db, trials, int(current_user.get("sub")))
        db.commit()
        return "Trial added successfully"
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
            detail="server error"
        )

@router.delete("/delete/trial", summary="FOOTBALL CLUB: delete from trial table")
def delete_trial(id_trial: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        this_trial = data_access.get_trial_by_id(db, id_trial)
        if this_trial is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="trial application was not found"
            )
        if current_user.get("role") != "football_club" and trial.id_club != current_user.get("sub"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to do this action"
            )
        trial_status = data_access.delete_trial(db, id_trial)
        db.commit()
        return "Trial deleted successfully"
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
            detail="server error"
        )

@router.get("/my_trials", summary="FOOTBALL CLUB: get all trials")
def my_trials(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        if current_user.get("role") not in ["football_club"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to do this action"
            )
        return data_access.get_trials(db, int(current_user.get("sub")))
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
            detail="server error"
        )

@router.get("/trial/applications/{id_trial}", summary="FOOTBALL CLUB: get trial application")
def trial_applications(id_trial: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        this_trial = data_access.get_trial_by_id(db, id_trial)
        if current_user.get("role") not in ["football_club"] or this_trial.id_club != int(current_user.get("sub")):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to do this action"
            )
        rez = data_access.all_applications(db, id_trial)
        return rez
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
            detail="server error"
        )

@router.get("/me", summary = "FOOTBALL CLUB & ADMIN: return football club info")
def me(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    user = data_access.find_user_by_id(db, int(current_user.get("sub")))
    if user.role not in ["admin", "football_club"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You don t have access to get user info."
        )
    try:
        football_club = data_access.get_football_club_by_id(db, int(current_user.get("sub")))
        if football_club is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The football club was not found."
            )
        return {
            "role": current_user.get("role"),
            "email": current_user.get("email"),
            "football_club": football_club
            }
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error"
        )
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="database error"
        )
    except HTTPException as e:
        return e

@router.get("/my_watchlist", summary="FOOTBALL CLUB: return my watchlist athletes")
def my_watchlist(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        if current_user.get("role") not in ["football_club"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to do this action"
            )
        watchlist = data_access.get_my_watchlist(db, current_user.get("sub"))
        return watchlist

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error"
        )
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="database error"
        )
    except HTTPException as e:
        return e

@router.put("/update/me", summary="ATHLETE: Update fc info")
def update_fc(user_updated: FootballClubBase, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        football_club = data_access.get_football_club_by_id(db, current_user.get("sub"))
        data_access.update_fc_info(user_updated, db, current_user.get("sub"))

        return football_club
    except Exception as e:
        db.rollback()
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error"
        )
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="database error"
        )
    except HTTPException as e:
        db.rollback()
        return e
