import os
import shutil

from fastapi import FastAPI, APIRouter, Depends, UploadFile, File, HTTPException
from matplotlib.pyplot import summer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from shared.core.database import get_db
from shared.crud import data_access
from shared.crud.security import get_current_user
from shared.schemas.schemas import AthleteUpdate
from shared.utils.challenge import videos_dir
from ..celery_client import celery_app

app = FastAPI()
router = APIRouter(prefix="/api/athlete", tags=["athlete"])

def analyze_video_task(id_athlete, id_challenge):
    pass

@router.get("/me", summary="ATHLETE: Return user info")
def me(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "athlete":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You don t have access to get user info."
        )
    try:
        athlete = data_access.get_athlete_by_id(db, current_user.get("sub"))
        return {
            "role": current_user.get("role"),
            "email": current_user.get("email"),
            "athlete": athlete
        }
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error"
        )
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="database error"
        )
    except HTTPException as e:
        return e


@router.get("/attributes/me", summary="ATHLETE: return my attributes")
def get_athlete_attributes(id_athlete: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        user = data_access.find_user_by_id(db, id_athlete)
        if user.role != "athlete":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User with id:{user.id} is not an athlete"
            )
        athlete = data_access.get_athlete_by_id(db, id_athlete)
        if current_user.get("role") not in ["admin", "football_club"] and athlete.user_id != int(current_user.get("sub")):

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don t have access to see athlete's attribute"
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


@router.put("/update/me", summary="ATHLETE: Update user info")
def update_user(user_updated: AthleteUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        athlete = data_access.get_athlete_by_id(db, current_user.get("sub"))
        data_access.update_user_info(user_updated, db, athlete.user_id)

        return athlete
    except Exception as e:
        db.rollback()
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error"
        )
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


@router.post("/video/upload", summary="ATHLETE: Upload video")
async def upload_video(id_challenge : int, db: Session = Depends(get_db), file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):

    athlete = data_access.get_athlete_by_id(db, current_user.get("sub"))
    if athlete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The athlete was not found."
        )

    workout_type = data_access.get_challenge_by_id(db, id_challenge).challenge_name
    save_directory = os.path.join(videos_dir, workout_type, str(athlete.user_id))
    os.makedirs(save_directory, exist_ok=True)
    video_name = f"{workout_type}.mp4"
    video_path = os.path.join(save_directory, video_name)

    try:
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "message": "Video successfully received",
            "saved_path": video_path,
            "filename": file.filename,
            "athlete id:" : athlete.user_id,
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


@router.post("/video/analyze", summary="ATHLETE: Run analysis")
def run_analysis_route(id_challenge: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    athlete = data_access.get_athlete_by_id(db, current_user.get("sub"))
    if athlete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The athlete was not found."
        )

    challenge_obj = data_access.get_challenge_by_id(db, id_challenge)
    if challenge_obj is None:
        raise HTTPException(
            status_code=404,
            detail= f"Challenge {challenge_obj} does not exist."
        )
    workout_type = challenge_obj.challenge_name
    save_directory = os.path.join(videos_dir, workout_type, str(athlete.user_id))
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
            detail=f"Id athlete {athlete.user_id} does not exist."
        )

    try:
        celery_app.send_task(
            "analyze_video_task",
            args=[athlete.user_id, id_challenge]
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


@router.post("/insert/challenge_result", summary="ATHLETE: insert challenge_result into table")
def insert_challenge_result_db(id_challenge: int, result: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    athlete = data_access.get_athlete_by_id(db, current_user.get("sub"))

    if athlete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The athlete was not found."
        )

    try:
        challenge = data_access.create_challenge_result(db, id_challenge, athlete.user_id, result)
        if challenge is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="It hasn't been 3 months since this athlete completed this challenge."
            )
        db.commit()

        db.refresh(challenge)
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


@router.delete("/delete/athlete/{user_id}", summary="ATHLETE & ADMIN: Delete user/athlete/attribute")
def delete_athlete(id_athlete: int,  db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        user = data_access.find_user_by_id(db, id_athlete)
        athlete = data_access.get_athlete_by_id(db, id_athlete)
        if athlete is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not an athlete"
            )
        if current_user.get("role") != "admin" and user.email != current_user.get("email"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don t have access to delete an athlete"
            )
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The athlete to be deleted was not found."
            )

        data_access.delete_from_challenge_result_table(db, athlete.user_id)
        data_access.delete_from_attribute_table(db, athlete.user_id)
        data_access.delete_from_athlete_table(db, athlete.user_id)
        data_access.delete_from_users_table(db, user.email)
        db.commit()
        return {"message": "user was deleted"}
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
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error"
        )