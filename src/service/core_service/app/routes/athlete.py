import os
import shutil

from fastapi import FastAPI, APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from shared.core.database import get_db
from shared.crud import data_access
from shared.crud.security import get_current_user
from shared.utils.challenge import videos_dir
from ..celery_client import celery_app


app = FastAPI()
router = APIRouter(prefix="/api/athlete", tags=["athlete"])




def analyze_video_task(id_athlete, id_challenge):
    pass

@router.post("/upload-video/", summary="*ATHLETE ONLY* Upload video")
async def upload_video(athlete_id: int, id_challenge : int, db: Session = Depends(get_db), file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):

    athlete = data_access.get_athlete_by_id(db, athlete_id)

    if current_user.get("role") != "athlete" or current_user.get("email") != athlete.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don t have access to upload a video."
        )
    athlete = data_access.get_athlete_by_id(db, athlete_id)
    if athlete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The athlete was not found."
        )
    workout_type = data_access.get_challenge_by_id(db, id_challenge).challenge_name
    save_directory = os.path.join(videos_dir, workout_type, str(athlete.id_athlete))
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
        raise e
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
    if athlete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The athlete was not found."
        )
    print(current_user.get("email"), athlete.email)
    if current_user.get("email") != athlete.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don t have access to analyze a video.",
        )
    workout_type = data_access.get_challenge_by_id(db, id_challenge).challenge_name
    save_directory = os.path.join(videos_dir, workout_type, str(athlete.id_athlete))
    os.makedirs(save_directory, exist_ok=True)
    video_name = f"{workout_type}.mp4"
    video_path = os.path.join(save_directory, video_name)
    print(video_path)
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
        celery_app.send_task(
            "analyze_video_task",
            args=[id_athlete, id_challenge]
        )

        return {
            "status": "pending",
            "message": "The analysis has been sent to the processing server. Check the results in a few minutes."
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
        raise e
    except Exception as e:
        db.rollback()
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error"
        )

@router.get("/get/attributes", summary="Get athlete's attributes")
def get_athlete_attributes(id_athlete: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        athlete = data_access.get_athlete_by_id(db, id_athlete)
        if current_user.get("role") != "admin" and athlete.email != current_user.get("email"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don t have accessto see athlete's attribute"
            )
        if athlete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The athlete was not found."
            )
        attributes = athlete.attributes
        return attributes
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="database error"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error"
        )

@router.delete("/delete/athlete", summary="Delete user/athlete/attribute")
def delete_athlete(id_athlete: int,  db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        athlete = data_access.get_athlete_by_id(db, id_athlete)
        if current_user.get("role") != "admin" and athlete.email != current_user.get("email"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don t have access to delete an athlete"
            )
        if athlete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The athlete to be deleted was not found."
            )

        data_access.delete_from_challenge_result_table(db, athlete.id_athlete)
        data_access.delete_from_attribute_table(db, athlete.id_athlete)
        data_access.delete_from_athlete_table(db, athlete.id_athlete)
        data_access.delete_from_users_table(db, athlete.email)

    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="database error"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error"
        )