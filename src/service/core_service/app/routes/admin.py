from typing import List

from fastapi import APIRouter, FastAPI, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from shared.core.database import get_db
from shared.crud import data_access
from shared.crud.security import get_current_user, hash_password
from shared.schemas.schemas import AthleteBase, Challenge
from shared.utils.enums import RolesEnum

app = FastAPI()
router = APIRouter(prefix="/api", tags=["admin"])


@router.post("/create/admin", summary="ADMIN: create an admin account")
def create_admin_account(email: str, password: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") not in ["admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don t have access to list of athletes."
        )
    try:
        role = RolesEnum.admin
        password_hash = hash_password(password)

        admin = data_access.create_user(db, email, password_hash, role)

        db.commit()
        db.refresh(admin)
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


@router.get("/athletes", response_model=List[AthleteBase], summary="ADMIN & FOOTBALL CLUB: get all athletes from db")
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



@router.post("/create/challenge", summary="ADMIN: create a new challenge")
def create_challenge(challenge: Challenge, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don t have access to insert a new challenge into db.",
        )
    try:
        new_challenge = data_access.create_challenge(db, challenge)

        db.commit()
        db.refresh(new_challenge)
        return new_challenge

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
    except Exception as e:
        db.rollback()
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error"
        )


@router.delete("/delete/challenge/{challenge_id}", summary="ADMIN: Delete a challenge")
def delete_challenge(challenge_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don t have access to insert a new challenge result into db.",
        )
    try:
        challenge = data_access.get_challenge_by_id(db, challenge_id)
        if challenge is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The challenge to be deleted was not found."
            )
        data_access.delete_from_challenge_table(db, challenge_id)

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
    except Exception as e:
        db.rollback()
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error"
        )

