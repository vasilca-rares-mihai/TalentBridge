from fastapi import FastAPI, Depends, APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status

from crud import data_access
from core.database import get_db
from sqlalchemy.orm import Session
from schemas.schemas import AthleteBase
from crud.security import *
from routes.athlete import insert_athlete_db
from utils.enums import RolesEnum

app = FastAPI()
router = APIRouter(prefix="/api/users", tags=["Users"])

@router.post("/user", summary="Create a user-athlete account")
def create_user_account(athlete_data: AthleteBase, email: str, password: str, db: Session = Depends(get_db)):
    try:
        role = RolesEnum.athlete
        password_hash = hash_password(password)
        user = data_access.create_user(db, email, password_hash, role)
        insert_athlete_db(athlete_data, email, db)
        return user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists"
        )
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving data to the database"
        )
    except Exception as e:
        print(f"Unexpected Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/admin", summary="Create an admin account")
def create_admin_account(email: str, password: str, db: Session = Depends(get_db)):
    try:
        role = RolesEnum.admin
        password_hash = hash_password(password)
        admin = data_access.create_user(db, email, password_hash, role)
        return admin
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists"
        )
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving data to the database"
        )
    except Exception as e:
        print(f"Unexpected Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/football_club", summary="Create a football club account")
def create_football_club_account(email: str, password: str, db: Session = Depends(get_db)):
    try:
        role = RolesEnum.football_club
        password_hash = hash_password(password)
        football_club = data_access.create_user(db, email, password_hash, role)
        return football_club
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists"
        )
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving data to the database"
        )
    except Exception as e:
        print(f"Unexpected Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )