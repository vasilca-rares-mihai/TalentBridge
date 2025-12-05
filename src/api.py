from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.athlete import Athlete, AthleteCreate, AthleteResponse
from routes import data_access
from core.database import get_db
app = FastAPI()


@app.get("/athletes", response_model=List[AthleteResponse], summary="Get all athletes")
def get_athletes(db:Session = Depends(get_db), skip: int = 0, limit: int = 100):
    try:
        athletes = data_access.list_athletes(db, skip=skip, limit=limit)
        return athletes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Athlete load error (api.py)"
        )

