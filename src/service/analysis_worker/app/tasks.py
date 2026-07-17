from fastapi import Depends
from sqlalchemy.orm import Session

from shared.core.database import get_db
from .worker import celery_app

from shared.crud import data_access
from shared.core.database import SessionLocal
from service.analysis_worker.app.worker import ANALYZERS
from shared.utils.challenge import videos_dir
from shared.utils.attribute_scoring import compute_attributes

import os
import json


@celery_app.task(name="analyze_video_task")
def analyze_video_task(id_athlete: int, id_challenge: int, result_id: int):
    db = SessionLocal()

    try:
        data_access.update_result_status(db, result_id, "processing")
        db.commit()
        athlete = data_access.get_athlete_by_id(db, id_athlete)
        challenge = data_access.get_challenge_by_id(db, id_challenge)

        if not athlete or not challenge:
            print("Athlete or challenge not found.")
            return

        workout_type = challenge.challenge_name
        video_path = os.path.join(videos_dir, "raw", workout_type, str(athlete.user_id), f"{workout_type}.mp4")
        processed_dir = os.path.join(videos_dir, "processed", workout_type, str(athlete.user_id))
        os.makedirs(processed_dir, exist_ok=True)
        output_video_path = os.path.join(processed_dir, f"{workout_type}_analyzed.mp4")

        AnalyzerClass = ANALYZERS.get(workout_type)
        analyzer = AnalyzerClass(video_path, output_path=output_video_path)
        analysis_result = analyzer.analyze(athlete)

        try:
            summary = analyzer.build_summary()
            summary_path = os.path.join(processed_dir, f"{workout_type}_summary.json")
            with open(summary_path, "w") as sf:
                json.dump(summary, sf)
        except Exception as se:
            print(f"summary write error: {se}")

        data_access.finalize_challenge_result(db, result_id, analyzer.getScore())
        my_challenge_results = data_access.get_challenge_results(db, id_athlete)
        updated_attributes = compute_attributes(my_challenge_results)
        data_access.overwrite_attributes(updated_attributes, db, id_athlete)

        print(f"Task successfully completed for the athlete {id_athlete}!")

    except Exception as e:
        print(f"error: {e}")
        try:
            db.rollback()
        except Exception:
            pass
        try:
            data_access.update_result_status(db, result_id, "failed")
            db.commit()
        except Exception as e2:
            print(f"could not set failed status: {e2}")
        raise e
    finally:
        db.close()