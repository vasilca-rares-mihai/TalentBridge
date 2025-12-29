from fastapi import FastAPI, Depends, APIRouter
from crud import data_access
from core.database import get_db
from sqlalchemy.orm import Session
from schemas.schemas import AthleteBase
from crud.security import *
from routes.athlete import insert_athlete_db
from utils.enums import RolesEnum

app = FastAPI()
router = APIRouter(prefix="/api/users", tags=["Users"])

@router.post("/user", summary="Create a user-athlete account")
def create_user_account(athlete_data: AthleteBase, email: str, password: str, db: Session = Depends(get_db)):
    role = RolesEnum.athlete
    password_hash = hash_password(password)
    user = data_access.create_user(db, email, password_hash, role)
    insert_athlete_db(athlete_data, email, db)
    return user

@router.post("/admin", summary="Create an admin account")
def create_admin_account(email: str, password: str, db: Session = Depends(get_db)):
    role = RolesEnum.admin
    password_hash = hash_password(password)
    admin = data_access.create_user(db, email, password_hash, role)
    return admin

@router.post("/football_club", summary="Create a football club account")
def create_football_club_account(email: str, password: str, db: Session = Depends(get_db)):
    role = RolesEnum.football_club
    password_hash = hash_password(password)
    football_club = data_access.create_user(db, email, password_hash, role)
    return football_club