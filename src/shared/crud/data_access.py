from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from sqlalchemy.sql.functions import current_user
from sqlalchemy import select

from service.analysis_worker.app.analyzers import StepAnalyzer
from shared.crud.security import security
from shared.crud import security
from shared.models.sql_models import Athlete, Attribute, ChallengeResult, Challenge, FootballClub, FavoriteAthlete, \
    Trial, TrialApplications
from shared.schemas.schemas import AthleteUpdate, AthleteSearched, AttributeUpdate, TrialResponse, CreateAthleteRequest, \
    CountResponse, FootballClubSearched
from typing import Optional
from shared.utils.enums import GenderEnum, PositionsEnum, WeakFootEnum, RolesEnum
from datetime import date, timedelta
from service.auth_service.app.models.sql_models import Users
from shared.utils.challenge import defpassword


#....................................................athletes utils..........................................
def list_athletes(db: Session) -> List[Athlete]:
    stms = select(Athlete)
    return db.scalars(stms).all()

def create_athlete(db: Session, athlete: CreateAthleteRequest, id_u: int):
    new_athlete = Athlete(
        user_id = id_u,
        first_name= athlete.athlete_data.first_name,
        second_name = athlete.athlete_data.second_name,
        field_position = athlete.athlete_data.field_position,
        weak_foot = athlete.athlete_data.weak_foot,
        age = athlete.athlete_data.age,
        gender = athlete.athlete_data.gender,
        height = athlete.athlete_data.height,
        weight = athlete.athlete_data.weight,
        country = athlete.athlete_data.country,
        region = athlete.athlete_data.region,
        city = athlete.athlete_data.city,
        phone_number = athlete.athlete_data.phone_number,
        date_of_birth = athlete.athlete_data.date_of_birth,
    )

    db.add(new_athlete)
    return new_athlete

def get_athlete_by_id(db: Session, id_u: int) -> Athlete:
    stms = select(Athlete).where(Athlete.user_id == id_u)
    return db.scalars(stms).first()


def delete_all(db: Session):
    try:
        models = [ChallengeResult, Attribute, Athlete, FootballClub, Users, Trial, TrialApplications]
        for model in models:
            db.execute(delete(model))

        print("All data has been successfully deleted")
    except Exception as e:
        db.rollback()
        print(f"Error deleting data: {e}")

def all_or_completed_challenges(db, user_id, index):
    all_challenges= []
    stms = select(Challenge) # challenge table
    challenges = db.scalars(stms)
    for challenge in challenges:
        all_challenges.append(challenge)

    limit_date = date.today() - timedelta(days=90)

    completed_challenges = []
    stms2 = select(ChallengeResult).where(ChallengeResult.user_id == user_id) #challenge result table
    challanges2 = db.scalars(stms2)
    for challenge in challanges2:
        if challenge.date_recorded > limit_date:
            stms3 = select(Challenge).where(Challenge.id_challenge == challenge.challenge_id)
            db_challenge = db.scalars(stms3).first()
            if db_challenge:
                completed_challenges.append(db_challenge)

    if index == 0:
        return all_challenges
    elif index == 1:
        rez = list(set(all_challenges) - set(completed_challenges))
        return rez
    elif index == 2:
        return completed_challenges
    return None

def update_user_info(payload: AthleteUpdate, db: Session, id_u: int):
    stms = select(Athlete).where(Athlete.user_id == id_u)
    athlete = db.scalars(stms).first()
    if athlete:
        athlete_updated = payload.model_dump(exclude_unset=True)
        for key, value in athlete_updated.items():
            if value not in [None, "", 0]:
                setattr(athlete, key, value)
        if "date_of_birth" in athlete_updated:
            dob = athlete.date_of_birth
            today = date.today()
            calculated_age = today.year - dob.year - (
                    (today.month, today.day) < (dob.month, dob.day)
            )
            athlete.age = calculated_age

        db.add(athlete)
        db.commit()
        db.refresh(athlete)
    return athlete

def update_fc_info(payload: FootballClub, db: Session, id_u: int):
    stmt = select(FootballClub).where(FootballClub.user_id == id_u)
    fc = db.scalars(stmt).first()
    if fc:
        athlete_updated = payload.model_dump(exclude_unset=True)
        for key, value in athlete_updated.items():
            if value not in [None, "", 0]:
                setattr(fc, key, value)

        db.add(fc)
        db.commit()
        db.refresh(fc)
    return fc


def update_user_attributes(attribute_updated: AttributeUpdate, db: Session, id_u: int):
    stmt = select(Attribute).where(Attribute.user_id == id_u)
    attribute = db.scalars(stmt).first()

    if attribute:
        attributes = attribute_updated.model_dump(exclude_unset=True)
        for key, value in attributes.items():
            if value not in [None, "", 0]:
                setattr(attribute, key, value)


        db.add(attribute)
        db.commit()
        db.refresh(attribute)
    return attribute

def delete_from_users_table(db: Session, user_id: int):
    stms = select(Users).where(Users.id == user_id)
    existing_result = db.scalars(stms).first()
    if existing_result:
        db.delete(existing_result)

def delete_from_football_club_table(db: Session, id: int):
    stms = select(FootballClub).where(FootballClub.user_id == id)
    existing_result = db.scalars(stms).first()
    if existing_result:
        db.delete(existing_result)

def list_athletes_by_filter(db: Session, athlete_searched: AthleteSearched) -> List[Athlete]:
    athletes = select(Athlete)
    search_params = athlete_searched.model_dump(exclude_unset=True)
    valid_columns = Athlete.__table__.columns.keys()

    for key, value in search_params.items():
        if value in [None, "", 0, [0, 0], [None, None]]:
            continue

        if key in valid_columns:
            athletes = athletes.where(getattr(Athlete, key) == value)
        elif key.endswith("_range") and isinstance(value, list) and len(value) == 2:
            column_name = key.replace("_range", "")
            if column_name in valid_columns:
                col = getattr(Athlete, column_name)
                athletes = athletes.where(col.between(value[0], value[1]))

    return db.scalars(athletes).all()


def list_fc_by_filter(db: Session, fc_searched: FootballClubSearched) -> List[FootballClub]:
    fc = select(FootballClub)
    search_params = fc_searched.model_dump(exclude_unset=True)

    valid_columns = FootballClub.__table__.columns.keys()

    for key, value in search_params.items():
        if value in [None, "", 0, [0, 0]]:
            continue

        if key in valid_columns:
            fc = fc.where(getattr(FootballClub, key) == value)

        elif key.endswith("_range") and isinstance(value, list) and len(value) == 2:
            column_name = key.replace("_range", "")
            if column_name in valid_columns:
                col = getattr(FootballClub, column_name)
                fc = fc.where(col.between(value[0], value[1]))

    return db.scalars(fc).all()

def compare_athletes_stats(db: Session, id_athlete1: int, id_athlete2: int):
    athlete1 = get_athlete_by_id(db, id_athlete1)
    athlete2 = get_athlete_by_id(db, id_athlete2)

    if not athlete1 or not athlete2:
        return None
    if not athlete1.attributes or not athlete2.attributes:
        return {"error": "One of the athletes does not have the attributes set"}

    stats_to_compare = [
        "acceleration", "sprint_speed", "finishing", "shot_power", "long_shots", "penalties", "short_pass", "long_pass", "agility", "balance", "ball_control", "dribbling", "heading_acc", "jumping", "stamina", "strength"
    ]
    comparison_result = {}

    attribute1 = get_attribute_by_id(db, id_athlete1)
    attribute2 = get_attribute_by_id(db, id_athlete2)

    for stat in stats_to_compare:
        val1 = getattr(attribute1, stat, 0) or 0
        val2 = getattr(attribute2, stat, 0) or 0
        if val1 > val2:
            mesaj = f"1"
        elif val2 > val1:
            mesaj = f"2"
        else:
            mesaj = "Eq"

        comparison_result[stat] = mesaj


    return comparison_result

def find_athlete_by_email(db: Session, email: str):
    stms = select(Athlete).where(Users.email == email)
    return db.scalars(stms).one_or_none()

#................................attribute.................................................................
def create_attribute(db: Session, id_u: int):
    attributes = Attribute(
        user_id= id_u,
        acceleration = 0,
        sprint_speed = 0,
        finishing = 0,
        shot_power = 0,
        long_shots = 0,
        penalties = 0,
        short_pass = 0,
        long_pass = 0,
        agility = 0,
        balance = 0,
        ball_control = 0,
        dribbling = 0,
        heading_acc = 0,
        jumping = 0,
        stamina = 0,
        strength = 0
    )
    db.add(attributes)

    return attributes

def get_attribute_by_id(db: Session, id_u: int) -> Attribute:
    stms = select(Attribute).where(Attribute.user_id == id_u)
    return db.scalars(stms).one()


def update_attribute(db: Session, id_athlete: int, update_data: dict):
    db_attribute = get_attribute_by_id(db, id_athlete)
    if not db_attribute:
        return None
    for key, value in update_data.items():
        if key != "id" and value is not None:
            setattr(db_attribute, key, value)
    db.commit()
    db.refresh(db_attribute)
    return db_attribute

#.................................challenge result..........................................................

def create_challenge_result(db: Session, id_challenge: int, id_u: int, result: int):
    new_challenge_result = ChallengeResult(
        user_id = id_u,
        challenge_id = id_challenge,
        result_value = result,
        date_recorded = date.today()
    )
    limit_date = date.today() - timedelta(days=90)
    stms = select(ChallengeResult).where(ChallengeResult.user_id == id_u,  ChallengeResult.challenge_id == id_challenge)
    existing_result = db.scalars(stms).first()
    if existing_result:
        if existing_result.date_recorded > limit_date:
            return None
        db.delete(existing_result)
    db.add(new_challenge_result)
    db.commit()
    return new_challenge_result

def get_challenge_result_by_id(db, challenge_id, athlete_id):
    stms = select(ChallengeResult).where(ChallengeResult.user_id == athlete_id, ChallengeResult.challenge_id == challenge_id)
    return db.scalars(stms).first()

def get_challenge_results(db, athlete_id, ):
    stmt = select(ChallengeResult).where(ChallengeResult.user_id == athlete_id, ChallengeResult.status == "completed")
    results = db.scalars(stmt).all()

    return list(results)

def update_result_status(db, result_id, status):
    stmt = select(ChallengeResult).where(ChallengeResult.id_result == result_id)
    result = db.scalars(stmt).first()
    if result:
        result.status = status
        db.commit()
        db.refresh(result)
    return result

def finalize_challenge_result(db, result_id, reps):
    stmt = select(ChallengeResult).where(ChallengeResult.id_result == result_id)
    result = db.scalars(stmt).first()
    if result:
        result.result_value = reps
        result.status = "completed"
        db.commit()
        db.refresh(result)

    return result

def init_challenge_result(db: Session, id_challenge: int, id_athlete: int):
    db_result = ChallengeResult(
        challenge_id=id_challenge,
        user_id=id_athlete,
        status="pending",
        result_value=0,
        date_recorded = date.today()
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

#....................................challenge.....................................
def get_challenge_by_id(db: Session, id_challenge: int) -> str:
    stms = select(Challenge).where(Challenge.id_challenge == id_challenge)
    return db.scalars(stms).first()

def delete_from_challenge_table(db: Session, id_challenge: int):
    stms = select(Challenge).where(Challenge.id_challenge == id_challenge)
    existing_result = db.scalars(stms).first()
    if existing_result:
        db.delete(existing_result)
        db.commit()

def create_challenge(db: Session, challenge: Challenge):
    new_challenge = Challenge(
        challenge_name = challenge.challenge_name,
        unit_of_measure = challenge.unit_of_measure,
        info = challenge.info
    )
    db.add(new_challenge)
    return new_challenge

#..........................user..........................
def create_user(db, email, password, role):
    new_user = Users(
        email= email,
        password_hash = password,
        role = role
    )
    db.add(new_user)
    return new_user

def find_user_by_email(db: Session, email: str):
    stms = select(Users).where(Users.email == email)
    return db.scalars(stms).first()

def find_user_by_id(db: Session, id_u: int):
    stms = select(Users).where(Users.id == id_u)
    return db.scalars(stms).first()

def get_football_club_by_id(db: Session, id_football_club: int):
    stms = select(FootballClub).where(FootballClub.user_id == id_football_club)
    return db.scalars(stms).first()

def create_football_club(db: Session, football_club: FootballClub, id_u: int):
    new_football_club = FootballClub(
        user_id = id_u,
        name =  football_club.name,
        country = football_club.country,
        info = football_club.info
    )
    db.add(new_football_club)
    return new_football_club

def first_admin(db: Session):
    stms = select(Users).where(Users.role == "admin")
    if db.scalars(stms).first() is None:
        new_admin = Users(
            email = "admin@test.ro",
            password_hash = security.hash_password(defpassword),
            role = RolesEnum.admin
        )
    db.add(new_admin)
    return new_admin

def add_to_watchlist(db: Session, club_id: int, athlete_id: int):
    new_fav_athlete = FavoriteAthlete(
        club_id = club_id,
        athlete_id = athlete_id
    )
    db.add(new_fav_athlete)
    return new_fav_athlete

def delete_from_watchlist(db: Session, club_id: int, athlete_id: int):
    stms = select(FavoriteAthlete).where(FavoriteAthlete.club_id == club_id, FavoriteAthlete.athlete_id == athlete_id)
    rez = db.scalars(stms).first()
    if rez:
        db.delete(rez)
        return True
    return False

def get_leaderboard(db: Session, challenge_id: int):
    top = []
    stms = select(ChallengeResult).where(ChallengeResult.challenge_id == challenge_id).order_by(ChallengeResult.result_value.desc())
    results = db.scalars(stms)
    for result in results:
        athlete = get_athlete_by_id(db, result.user_id)
        top.append({"first_name": athlete.first_name, "second_name": athlete.second_name, "result_value": result.result_value, "date_recorded": result.date_recorded})
        if top.count == 10:
            return top
    return top

def create_trial(db, trials, id_club):
    new_trial = Trial(
        id_club = id_club,
        until_date = trials.until_date,
        info = trials.info,
        requirements = trials.requirements.model_dump()
    )
    db.add(new_trial)
    return new_trial

def get_trial_by_id(db, id_trial: int):
    stms = select(Trial).where(Trial.id_trial == id_trial)
    return db.scalars(stms).first()

def delete_trial(db, id_trial: int):
    stms = select(Trial).where(Trial.id_trial == id_trial)
    rez = db.scalars(stms).first()
    if rez:
        db.delete(rez)
    return True

def get_trials(db, club_id: int):
    stms = select(Trial).where(Trial.id_club == club_id)
    return db.scalars(stms).all()

def apply_to_trial(db, id_trial, id_athlete):
    new_application = TrialApplications(
        id_trial = id_trial,
        id_athlete = id_athlete
    )
    db.add(new_application)
    return new_application

def application_permision(db, id_trial, id_athlete):
    stms = select(TrialApplications).where(TrialApplications.id_trial == id_trial).where(TrialApplications.id_athlete == id_athlete)
    rez = db.scalars(stms).first()
    if rez:
        return True
    return False

def my_trial_applications(db, id_athlete):
    stmt = select(TrialApplications).where(TrialApplications.id_athlete == id_athlete)
    result = db.scalars(stmt).all()
    trial_list = []
    for trial in result:
        trial_list.append(trial.id_trial)
    return trial_list

def get_trial_application_by_id(db, id_trial, id_athlete):
    stms = select(TrialApplications).where(TrialApplications.id_trial == id_trial).where(TrialApplications.id_athlete == id_athlete)
    return db.scalars(stms).first()

def delete_trial_application(db, trial_application):
    db.delete(trial_application)
    return True

def get_all_trials(db):
    trials_list = []
    stmt = (select(Trial).order_by(Trial.id_trial))
    result = db.scalars(stmt).all()
    for trial in result:
        stmt2 = select(FootballClub).where(FootballClub.user_id == trial.id_club)
        result2 = db.scalars(stmt2).first()
        trialResponse = TrialResponse(
            id_trial = trial.id_trial,
            until_date = trial.until_date,
            info = trial.info,
            requirements = trial.requirements,
            football_club = result2.name,
            country = result2.country
        )
        trials_list.append(trialResponse)

    return trials_list

def all_applications(db, id_trial):
    athlete_list = []
    stms = select(TrialApplications).where(TrialApplications.id_trial == id_trial)
    result = db.scalars(stms).all()
    for trial_application in result:
        athlete = get_athlete_by_id(db, trial_application.id_athlete)
        athlete_list.append(athlete)
    return athlete_list

def restriction(db, id_athlete, id_challenge):
    index = 0
    stmt = select(ChallengeResult).where(ChallengeResult.challenge_id == id_challenge).where(ChallengeResult.user_id == id_athlete)
    results = db.scalars(stmt).all()
    for result in results:
        if result.status == "failed":
            index = index+1
    if index == len(results):
        return False
    if results:
        return True
    return False


def sort_by_field_position(athlete):
    return athlete.field_position if athlete.field_position else ""


def get_my_watchlist(db: Session, id_football_club: int):
    athletes_list = []

    stmt = select(FavoriteAthlete).where(FavoriteAthlete.club_id == id_football_club)
    results = db.scalars(stmt).all()

    for result in results:
        athlete = get_athlete_by_id(db, result.athlete_id)
        if athlete:
            athletes_list.append(athlete)

    return sorted(athletes_list, key=sort_by_field_position)

def count_athlete(db: Session):
    stmt = select(Athlete)
    result = db.scalars(stmt).all()
    return len(result)

def count_fc(db:Session):
    stmt = select(FootballClub)
    result = db.scalars(stmt).all()
    return len(result)

def count_analysis(db:Session):
    stmt = select(ChallengeResult)
    result = db.scalars(stmt).all()
    return len(result)

def count_challenges(db:Session):
    stmt = select(Challenge)
    result = db.scalars(stmt).all()
    return len(result)

def count_trials(db:Session):
    stmt = select(Trial)
    result = db.scalars(stmt).all()
    return len(result)

def count_fav_athletes(db:Session):
    stmt = select(FavoriteAthlete)
    result = db.scalars(stmt).all()
    return len(result)

def count_trial_applications(db:Session):
    stmt = select(TrialApplications)
    result = db.scalars(stmt).all()
    return len(result)

def infoPannel(db:Session):
    total_athletes = count_athlete(db)
    total_fc = count_fc(db)
    total_analysis = count_analysis(db)
    total_challenges = count_challenges(db)
    total_trials = count_trials(db)
    total_fav_athletes = count_fav_athletes(db)
    total_trial_applications = count_trial_applications(db)

    info = CountResponse(
        athleteCount = total_athletes,
        footballClubCount = total_fc,
        analysisCount = total_analysis,
        challengesCount = total_challenges,
        trialsCount = total_trials,
        favoriteAthCount = total_fav_athletes,
        trialApplicationsCount = total_trial_applications
        )

    return info



"""
def delete_from_attribute_table(db: Session, id_u: int):
    stms = select(Attribute).where(Attribute.user_id == id_u)
    existing_result = db.scalars(stms).first()
    if existing_result:
        db.delete(existing_result)
        
def delete_from_athlete_table(db: Session, id_u: int):
    stms = select(Athlete).where(Athlete.user_id == id_u)
    existing_result = db.scalars(stms).first()
    if existing_result:
        db.delete(existing_result)
        
def delete_from_challenge_result_table(db: Session, id_u: int):
        stms = select(ChallengeResult).where(ChallengeResult.user_id == id_u)
        existing_result = db.scalars(stms).first()
        if existing_result:
            db.delete(existing_result)

"""
