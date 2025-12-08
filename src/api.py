import shutil
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from core.schemas import AthleteCreate, Athlete, ChallengeCreate
import os
from routes import data_access
from core.database import get_db
app = FastAPI()


@app.get("/athletes", response_model=List[Athlete], summary="Get all athletes from athlete table")
def get_athletes(db:Session = Depends(get_db), skip: int = 0, limit: int = 100):
    try:
        athletes = data_access.list_athletes(db, skip=skip, limit=limit)
        return athletes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Athlete load error (api.py)"
        )

@app.post("/athletes", response_model=Athlete, summary="Insert new athlete in DB")
def insert_athlete_db(athlete_data: AthleteCreate, db: Session = Depends(get_db)):
    try:
        athlete = data_access.create_athlete(db, athlete_data)
        return athlete
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="phone number or email already exists"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Athlete create error (api.py)"
        )

@app.get("/athletes/{id}", response_model=Athlete, summary="Get athlete id from athlete table")
def get_athlete_by_id(athlete_id: int, db: Session = Depends(get_db)):
    try:
        athlete = data_access.get_athlete_by_id(db, athlete_id)
        if athlete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="athlete not found"
            )
        return athlete
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@app.post("/upload-video/")
async def upload_video(athlete_id: int, id_challenge : int, db: Session = Depends(get_db), file: UploadFile = File(...)):
    athlete = data_access.get_athlete_by_id(db, athlete_id)
    workout_type = data_access.get_workout_type(db, id_challenge)
    save_directory = os.path.join("videos", workout_type, str(athlete.id_athlete))
    os.makedirs(save_directory, exist_ok=True)
    video_name = f"{workout_type}.mp4"
    video_path = os.path.join(save_directory, video_name)

    try:
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "message": "Video successfully received",
            "saved_path": video_path,
            "filename": file.filename
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )