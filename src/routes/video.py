from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from crud import data_access
from core.database import get_db
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, APIRouter
from routes.challenge import insert_challenge_result_db
from utils.challenge import ANALYZERS
import os
import shutil
from crud.security import get_current_user

app = FastAPI()
router = APIRouter(prefix="/api/video", tags=["Video"])

@router.post("/upload-video/", summary="*ATHLETE ONLY* Upload video")
async def upload_video(athlete_id: int, id_challenge : int, db: Session = Depends(get_db), file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):

    athlete = data_access.get_athlete_by_id(db, athlete_id)
    if current_user.get("role") != "athlete" and current_user.get("email") != athlete.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don t have access to upload a video."
        )
    athlete = data_access.get_athlete_by_id(db, athlete_id)
    workout_type = data_access.get_challenge_by_id(db, id_challenge).challenge_name
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

@router.post("/analyze", summary="*ATHLETE ONLY* Run analysis on an uploaded video")
def run_analysis_route(id_athlete: int, id_challenge: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    athlete = data_access.get_athlete_by_id(db, id_athlete)
    print(current_user.get("email"), athlete.email)
    if current_user.get("email") != athlete.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don t have access to analyze a video.",
        )
    workout_type = data_access.get_challenge_by_id(db, id_challenge).challenge_name
    save_directory = os.path.join("videos", workout_type, str(athlete.id_athlete))
    os.makedirs(save_directory, exist_ok=True)
    video_name = f"{workout_type}.mp4"
    video_path = os.path.join(save_directory, video_name)

    if not os.path.exists(video_path):
        raise HTTPException(
            status_code=404,
            detail=f"folder '{video_name}' does not exist"
        )

    if not workout_type:
        raise HTTPException(
            status_code=400,
            detail=f"Type '{workout_type}' does not exist."
        )

    if not athlete:
        raise HTTPException(
            status_code=404,
            detail=f"Id athlete {id_athlete} does not  exist."
        )

    try:
        AnalyzerClass = ANALYZERS[workout_type]
        analyzer = AnalyzerClass(video_path)
        analysis_result = analyzer.analyze(athlete)
        print(analysis_result)
        if os.path.exists(video_path):
            os.remove(video_path)
        #def insert_challenge_result_db(id_challenge: int, id_athlete: int, result: int, db: Session = Depends(get_db)):
        insert_challenge_result_db(id_challenge, athlete.id_athlete, analysis_result, db, current_user)

    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="database error"
        )
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error"
        )