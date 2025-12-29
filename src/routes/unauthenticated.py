from sqlite3 import IntegrityError

from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from core.database import get_db
from crud import data_access
from crud.security import hash_password, verify_password, create_jws_token
from schemas.schemas import AthleteBase, FootballClubBase
from utils.enums import RolesEnum

app = FastAPI()
router = APIRouter(prefix="/api/unauthenticated", tags=["unauthenticated"])

@router.post("/user/athlete", summary="Create a user-athlete account")
def create_user_account(athlete_data: AthleteBase, email: str, password: str, db: Session = Depends(get_db)):
    try:
        role = RolesEnum.athlete
        password_hash = hash_password(password)
        user = data_access.create_user(db, email, password_hash, role)

        athlete = data_access.create_athlete(db, athlete_data, email)
        attribute = data_access.create_attribute(db, athlete.id_athlete)

        db.commit()
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
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/user/football_club", summary="Create a football club account")
def create_football_club_account(football_club_data: FootballClubBase, email: str, password: str, db: Session = Depends(get_db)):
    try:
        role = RolesEnum.football_club
        password_hash = hash_password(password)
        user = data_access.create_user(db, email, password_hash, role)

        football_club = data_access.create_football_club(db, football_club_data, email)

        db.commit()
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
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/login", summary="Verify password and return jwt")
def login(email: str, password: str, db: Session = Depends(get_db)):
    try:
        user = data_access.find_user_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        try:
            is_valid = verify_password(password, user.password_hash)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal error in security processing"
            )
        if is_valid:
            token = create_jws_token(user.id, user.role, user.email)
            return {"access_token": token, "token_type": "bearer"}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )