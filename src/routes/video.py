from sqlalchemy.orm import Session
from crud import data_access
from core.database import get_db
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, APIRouter
from routes.challenge import insert_challenge_result_db
from utils.challenge import ANALYZERS
import os
import shutil

app = FastAPI()
router = APIRouter(prefix="/api/video", tags=["Video"])

@router.post("/upload-video/", summary="Upload video")
async def upload_video(athlete_id: int, id_challenge : int, db: Session = Depends(get_db), file: UploadFile = File(...)):
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

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@router.post("/analyze", summary="Run analysis on an uploaded video")
def run_analysis_route(id_athlete: int, id_challenge: int, db: Session = Depends(get_db)):
    athlete = data_access.get_athlete_by_id(db, id_athlete)
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
        insert_challenge_result_db(id_challenge, athlete.id_athlete, analysis_result, db)

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400,
            detail=f"Error analyzing {video_path}: {e}"
        )