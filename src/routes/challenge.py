from schemas.schemas import ChallengeResult, Challenge
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from crud import data_access
from core.database import get_db
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from crud.security import get_current_user

app = FastAPI()
router = APIRouter(prefix="/api/challenge", tags=["Challenge"])

@router.post("/challenge_result", response_model=ChallengeResult, summary="*ATHLETE*Insert a new challenge result for an athlete")
def insert_challenge_result_db(id_challenge: int, id_athlete: int, result: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    athlete = data_access.get_athlete_by_id(db, id_athlete)

    if athlete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The athlete was not found."
        )
    if current_user.get("role") != "athlete" or athlete.email != current_user.get("email"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don t have access to insert a new challenge result into db.",
        )
    try:
        challenge = data_access.create_challenge_result(db, id_challenge, id_athlete, result)
        if challenge is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="It hasn't been 3 months since this athlete completed this challenge."
            )
        return challenge
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

@router.post("/challenge", summary="*ADMIN ONLY* Create a new challenge")
def create_challenge(challenge: Challenge, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don t have access to insert a new challenge into db.",
        )
    try:
        new_challenge = data_access.create_challenge(db, challenge)
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

@router.delete("/challenge/{challenge_id}", summary="*ADMIN ONLY* Delete a challenge")
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