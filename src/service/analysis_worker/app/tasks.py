from fastapi import Depends
from sqlalchemy.orm import Session

from shared.core.database import get_db
from .worker import celery_app

from shared.crud import data_access
from shared.core.database import SessionLocal
from shared.utils.challenge import ANALYZERS
from shared.utils.challenge import videos_dir

import os


@celery_app.task(name="analyze_video_task")
def analyze_video_task(id_athlete: int, id_challenge: int):
    db = SessionLocal()

    try:
        athlete = data_access.get_athlete_by_id(db, id_athlete)
        challenge = data_access.get_challenge_by_id(db, id_challenge)

        if not athlete or not challenge:
            print("Athlete or challenge not found.")
            return

        workout_type = challenge.challenge_name
        video_path = os.path.join(videos_dir, workout_type, str(athlete.user_id), f"{workout_type}.mp4")

        AnalyzerClass = ANALYZERS.get(workout_type)
        analyzer = AnalyzerClass(video_path)
        analysis_result = analyzer.analyze(athlete)

        data_access.create_challenge_result(db, id_challenge, athlete.user_id, analysis_result)

        if os.path.exists(video_path):
            os.remove(video_path)
        print(f"Task successfully completed for the athlete {id_athlete}!")

    except Exception as e:
        print(f"error: {e}")
        raise e
    finally:
        db.close()