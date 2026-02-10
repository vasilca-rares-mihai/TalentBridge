from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from shared.core.database import get_db
from shared.crud import data_access
from shared.crud import security
from shared.schemas.schemas import AthleteBase, FootballClubBase
from shared.utils.enums import RolesEnum

router = APIRouter(prefix="/api/unauthenticated", tags=["unauthenticated"])

@router.post("/create/first_admin", summary="Create a first admin account")
def create_first_admin(db: Session = Depends(get_db)):
    try:
        admin = data_access.first_admin(db)

        db.commit()
        db.refresh(admin)
        return admin
    except (IntegrityError, SQLAlchemyError, Exception) as e:
        db.rollback()
        if isinstance(e, IntegrityError):
            detail = "An account with this email already exists"
            status_code = status.HTTP_409_CONFLICT
        else:
            detail = f"Error: {str(e)}"
            status_code = 500
        print(f"ROLLBACK EXECUTED. Reason: {e}")
        raise HTTPException(status_code=status_code, detail=detail)

@router.post("/create/athlete", summary="Create an user-athlete account")
def create_user_account(athlete_data: AthleteBase, email: str, password: str, db: Session = Depends(get_db)):
    try:
        role = RolesEnum.athlete
        password_hash = security.hash_password(password)

        user = data_access.create_user(db, email, password_hash, role)
        db.flush()

        athlete = data_access.create_athlete(db, athlete_data, user.id)
        db.flush()

        data_access.create_attribute(db, athlete.user_id)

        db.commit()
        db.refresh(user)
        return user.id, user.email, user.role

    except (IntegrityError, SQLAlchemyError, Exception) as e:
        db.rollback()
        if isinstance(e, IntegrityError):
            detail = "An account with this email already exists"
            status_code = status.HTTP_409_CONFLICT
        else:
            detail = f"Error: {str(e)}"
            status_code = 500
        print(f"ROLLBACK EXECUTED. Reason: {e}")
        raise HTTPException(status_code=status_code, detail=detail)

@router.post("/create/football_club", summary="Create an user-football club account")
def create_football_club_account(football_club_data: FootballClubBase, email: str, password: str, db: Session = Depends(get_db)):
    try:
        role = RolesEnum.football_club
        password_hash = security.hash_password(password)

        user = data_access.create_user(db, email, password_hash, role)
        db.flush()

        data_access.create_football_club(db, football_club_data, user.id)

        db.commit()
        db.refresh(user)
        return user

    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig).lower()
        if "email" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists."
            )
        elif "name" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A football club with this name already exists."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Integrity violation: duplicate entry or invalid reference."
            )
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving data to the database"
        )
    except Exception as e:
        print(f"Unexpected Error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/login", summary="LOGIN: Verify password and return jwt")
def login(email: str, password: str, db: Session = Depends(get_db)):
    try:
        user = data_access.find_user_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        try:
            is_valid = security.verify_password(password, user.password_hash)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal error in security processing"
            )
        if is_valid:
            token = security.create_jws_token(user.id, user.role, user.email)
            return {"access_token": token, "token_type": "bearer"}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Login unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/logout", summary="LOGOUT: add to blacklist jwt token")
def logout(res: HTTPAuthorizationCredentials = Depends(security.security)):
    try:
        token = res.credentials
        security.add_to_blacklist(token)
        return {'message': 'Successfully logged out'}
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not log out"
        )
