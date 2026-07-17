import os
import json
import shutil
from typing import List

from fastapi.responses import FileResponse
from fastapi import FastAPI, APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from shared.core.database import get_db
from shared.crud import data_access
from shared.crud.security import get_current_user
from shared.schemas.schemas import AthleteUpdate, AttributeUpdate
from shared.utils.challenge import videos_dir
from ..celery_client import celery_app

app = FastAPI()
router = APIRouter(prefix="/api/athlete", tags=["athlete"])

def analyze_video_task(id_athlete, id_challenge, id_result):
    pass

@router.get("/me", summary="ATHLETE & FOOTBALL CLUB: Return user info")
def me(id_athlete: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user = data_access.find_user_by_id(db, id_athlete)
    if user.role not in ["athlete", "football_club"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You don t have access to get user info."
        )
    try:
        athlete = data_access.get_athlete_by_id(db, id_athlete)
        if athlete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The athlete was not found."
            )
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


@router.get("/attributes/me", summary="ATHLETE & FOOTBALL CLUB: return my attributes")
def get_athlete_attributes(id_athlete: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        user = data_access.find_user_by_id(db, id_athlete)
        if user.role not in ["athlete", "football_club"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User with id:{user.id} is not an athlete"
            )
        athlete = data_access.get_athlete_by_id(db, id_athlete)
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
async def upload_video(id_challenge: int, db: Session = Depends(get_db), file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):

    if not file.filename.lower().endswith(".mp4"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only MP4 files are allowed."
        )

    if file.content_type != "video/mp4":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload an MP4 video."
        )

    athlete = data_access.get_athlete_by_id(db, current_user.get("sub"))
    if athlete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The athlete was not found."
        )

    challenge = data_access.get_challenge_by_id(db, id_challenge)
    if challenge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Challenge {id_challenge} does not exist."
        )

    workout_type = challenge.challenge_name

    save_directory = os.path.join(videos_dir, "raw", workout_type, str(athlete.user_id))
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
            "athlete_id": athlete.user_id,
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

@router.get("/video/display/{challenge_id}", summary="ATHLETE: returns processed video (analysed video)")
def get_analyzed_video(challenge_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    challenge = data_access.get_challenge_by_id(db, challenge_id)
    result = data_access.get_challenge_result_by_id(db, challenge_id, int(current_user.get("sub")))

    analyzed_video_path = os.path.join(videos_dir, "processed", challenge.challenge_name, str(current_user.get("sub")), f"{challenge.challenge_name}_analyzed.mp4")
    if not result or not analyzed_video_path:
        raise HTTPException(
            status_code=404,
            detail="Result for this challenge was not found."
        )

    if not os.path.exists(analyzed_video_path):
        raise HTTPException(
            status_code=404,
            detail="Analyzed video not found."
        )

    return FileResponse(analyzed_video_path, media_type="video/mp4")


@router.get("/video/summary/{challenge_id}", summary="ATHLETE: returns analysis summary (verdicts/counts/distance)")
def get_analysis_summary(challenge_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    challenge = data_access.get_challenge_by_id(db, challenge_id)
    if challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found.")

    summary_path = os.path.join(
        videos_dir, "processed", challenge.challenge_name,
        str(current_user.get("sub")), f"{challenge.challenge_name}_summary.json"
    )
    if not os.path.exists(summary_path):
        raise HTTPException(status_code=404, detail="Summary not found.")

    with open(summary_path, "r") as f:
        return json.load(f)


@router.get("/video/status/{challenge_id}", summary="Check if analysis is complete")
def check_video_status(challenge_id: int, db: Session = Depends(get_db),
                       current_user: dict = Depends(get_current_user)):
    result = data_access.get_challenge_result_by_id(db, challenge_id, int(current_user.get("sub")))

    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    return {"status": result.status}


@router.get("/video/raw_exists/{challenge_id}", summary="ATHLETE: are un clip incarcat (gata de analiza)?")
def raw_video_exists(challenge_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    challenge = data_access.get_challenge_by_id(db, challenge_id)
    if challenge is None:
        return False
    raw_path = os.path.join(
        videos_dir, "raw", challenge.challenge_name,
        str(current_user.get("sub")), f"{challenge.challenge_name}.mp4"
    )
    return os.path.exists(raw_path)


@router.get("/completed_challenges", summary="ATHLETE: ids of completed challenges")
def get_completed_challenges(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # get_challenge_results intoarce doar rezultatele cu status 'completed'
    results = data_access.get_challenge_results(db, int(current_user.get("sub")))
    return list({r.challenge_id for r in results})


@router.post("/video/analyze", summary="ATHLETE: Run analysis", status_code=status.HTTP_202_ACCEPTED)
def run_analysis_route( id_challenge: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    athlete = data_access.get_athlete_by_id(db, current_user.get("sub"))

    if athlete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The athlete was not found."
        )

    challenge_obj = data_access.get_challenge_by_id(db, id_challenge)

    if challenge_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Challenge {id_challenge} does not exist."
        )

    access = data_access.restriction(
        db,
        int(current_user.get("sub")),
        id_challenge
    )

    if access:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You cannot try this challenge again (3 month restriction)"
        )

    workout_type = challenge_obj.challenge_name

    if not workout_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Type '{workout_type}' does not exist."
        )

    save_directory = os.path.join(
        videos_dir,
        "raw",
        workout_type,
        str(athlete.user_id)
    )

    video_name = f"{workout_type}.mp4"
    video_path = os.path.join(save_directory, video_name)

    if not os.path.exists(video_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video '{video_name}' does not exist."
        )

    try:
        new_result = data_access.init_challenge_result(
            db,
            id_challenge,
            athlete.user_id
        )

        db.commit()
        db.refresh(new_result)

        task = celery_app.send_task(
            "analyze_video_task",
            args=[athlete.user_id, id_challenge, new_result.id_result]
        )

        return {
            "status": "accepted",
            "status_code": 202,
            "task_id": task.id,
            "id_result": new_result.id_result,
            "message": "The analysis has been accepted and sent to the processing server."
        }

    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )

    except Exception as e:
        db.rollback()
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error"
        )

@router.get("/challenge_result/{challenge_id}", summary="ATHLETE: Get challenge result")
def challenge_result(challenge_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        if current_user.get("role") != "athlete":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not allowed to do this action"
            )
        athlete_challenge_result = data_access.get_challenge_result_by_id(db, challenge_id, int(current_user.get("sub")))
        if athlete_challenge_result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The athlete does not complete this challenge"
            )
        return athlete_challenge_result
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

@router.get("/challenge_results", summary="ATHLETE: Get all challenges results")
def my_challenges_results(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        if current_user.get("role") != "athlete":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not allowed to do this action"
            )
        athlete_challenge_result = data_access.get_challenge_results(db, int(current_user.get("sub")))
        if athlete_challenge_result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The athlete does not complete this challenge"
            )
        return athlete_challenge_result
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


@router.delete("/delete/{user_id}", summary="ATHLETE: Delete user/athlete/attribute")
def delete_athlete(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        user = data_access.find_user_by_id(db, int(current_user.get("sub")))
        athlete = data_access.get_athlete_by_id(db, int(current_user.get("sub")))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The user to be deleted was not found."
            )
        if athlete is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not an athlete"
            )
        data_access.delete_from_users_table(db, user.id)
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

@router.get("/challenges", summary="ATHLETE: returns challenges. index = 0 for all challenges. index = 1 for uncompleted challenges. index = 2 fro completed challenges")
def get_locked_challenges(index: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        locked_challenges = []
        user = data_access.find_user_by_id(db, current_user.get("sub"))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user was not found."
            )
        challenges = data_access.all_or_completed_challenges(db, user.id, index)
        for challenge in challenges:
            rez = data_access.get_challenge_by_id(db, challenge.id_challenge) #challenge table
            locked_challenges.append(rez)
        return locked_challenges

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


@router.get("/challenges/{challenment_id}/leaderboard", summary="ATHLETE & ADMIN: Leaderboard")
def leaderboard(challenge_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        return data_access.get_leaderboard(db, challenge_id)
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


@router.post("/trial/apply/{id_trial}", summary="ATHLETE: Apply for a trial")
def apply_trial(id_trial, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        if current_user.get("role") != "athlete":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to do this action"
            )
        application_status = data_access.application_permision(db, id_trial, int(current_user.get("sub")))
        if application_status:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You applied for this trial."
            )
        this_trial = data_access.get_trial_by_id(db, id_trial)
        if this_trial is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="trial not found",
            )
        data_access.apply_to_trial(db, id_trial, int(current_user.get("sub")))
        db.commit()
        return "Trial application successfully done"
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
            detail="server error"
        )


@router.delete("/delete/trial/application/{id_trial}", summary="ATHLETE: Delete a trial application")
def delete_trial_application(id_trial: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        trial_application = data_access.get_trial_application_by_id(db, id_trial, int(current_user.get("sub")))
        if trial_application is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="trial not found"
            )
        if current_user.get("role") != "athlete" and trial_application.id_athlete != int(current_user.get("sub")):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to do this action"
            )
        trial_status = data_access.delete_trial_application(db, trial_application)
        db.commit()
        return "Trial application was successfully deleted"
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
            detail="server error"
        )


@router.get("/all_trials", summary="ATHLETE & FOOTBALL CLUB: get all trials")
def all_trials(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        if current_user.get("role") not in ["athlete", "football_club"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to do this action"
            )
        trials = data_access.get_all_trials(db)
        return trials
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
            detail="server error"
        )


@router.put("/update/attributes", summary="ATHLETE: Update user attributes")
def update_attribute(attribute_updated: AttributeUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        result = data_access.update_user_attributes(attribute_updated, db, int(current_user.get("sub")))

        return result
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


@router.get("/trial/my_applications", summary="ATHLETE: Get all your trial applications")
def my_applications(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        user = data_access.find_user_by_id(db, int(current_user.get("sub")))
        athlete = data_access.get_athlete_by_id(db, int(current_user.get("sub")))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The user to be deleted was not found."
            )
        if athlete is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not an athlete"
            )
        trial_applications = data_access.my_trial_applications(db, int(current_user.get("sub")))
        return trial_applications
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
            detail="server error"
        )

