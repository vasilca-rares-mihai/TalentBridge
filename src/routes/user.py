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

@router.post("/user/admin", summary="Create an admin account")
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
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/user/football_club", summary="Create a football club account")
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
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/login", summary="Verify password and return jwt")
def login(email: str, password: str, db: Session = Depends(get_db)):
    try:
        user = data_access.find_user(db, email)
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

@router.delete("/delete/user", summary="Delete user/athlete/attribute")
def delete_user(email: str,  db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        user = data_access.find_user(db, email)
        if current_user.get("role") != "admin" and user.email != current_user.get("email"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don t have access to delete an athlete"
            )
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The athlete to be deleted was not found."
            )

    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Athlete delete error (api.py)"
        )