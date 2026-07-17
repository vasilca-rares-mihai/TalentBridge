import os
import time
import socket
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.core.base import Base


SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:Rares545@talent-bridge-db/db_talentbridge")

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def wait_for_db():
    """Verifica daca baza de date e gata pe portul 3306"""
    print("Astept baza de date...")
    while True:
        try:
            with socket.create_connection(("talent-bridge-db", 3306), timeout=5):
                print("Baza de date este online!")
                return
        except (ConnectionRefusedError, socket.timeout, socket.gaierror, OSError):
            print("DB inca nu e gata, astept...")
            time.sleep(5)


def init_db():
    wait_for_db()
    from shared.models.sql_models import (
        Athlete, Attribute, ChallengeResult, Challenge, FootballClub,
        FavoriteAthlete, Trial, TrialApplications, Users, PushUpTest
    )

    with engine.connect() as conn:
        conn.execute(sqlalchemy.text("SET FOREIGN_KEY_CHECKS = 0;"))
        Base.metadata.create_all(bind=engine)
        conn.execute(sqlalchemy.text("SET FOREIGN_KEY_CHECKS = 1;"))
        conn.commit()

    print("Tabelele au fost create cu succes!")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()