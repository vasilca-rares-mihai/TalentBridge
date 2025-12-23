from schemas.schemas import ChallengeResult, Challenge
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from crud import data_access
from core.database import get_db
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter

app = FastAPI()
router = APIRouter(prefix="/api/challenge", tags=["Challenge"])

@router.post("/challenge_result", response_model=ChallengeResult, summary="Insert a new challenge result for an athlete")
def insert_challenge_result_db(id_challenge: int, id_athlete: int, result: int, db: Session = Depends(get_db)):
    athlete = data_access.get_athlete_by_id(db, id_athlete)
    if athlete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The athlete was not found."
        )
    try:
        challenge = data_access.create_challenge_result(db, id_challenge, id_athlete, result)
        if challenge is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="It hasn't been 3 months since this athlete completed this challenge."
            )
        return challenge

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="challenge_result create error (api.py)"
        )
