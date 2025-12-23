from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from database import get_db
from models.athlete import Athlete, AthleteCreate, AthleteResponse

app = FastAPI()



@app.post("/athletes", response_model=AthleteResponse, status_code=status.HTTP_201_CREATED)
def create_athlete(athlete: AthleteCreate, db: Session = Depends(get_db)):
    db_athlete = Athlete(**athlete.model_dump())

    try:
        db.add(db_athlete)
        db.commit()

        db.refresh(db_athlete)

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eroare SQL la salvare: {e}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eroare necunoscuta: {e}"
        )

    return db_athlete