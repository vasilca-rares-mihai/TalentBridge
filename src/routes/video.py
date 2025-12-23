from sqlalchemy.orm import Session
from crud import data_access
from core.database import get_db
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, APIRouter
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
