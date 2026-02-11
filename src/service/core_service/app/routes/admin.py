from distutils.dep_util import newer_pairwise
from typing import List

from fastapi import APIRouter, FastAPI, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql.coercions import expect
from starlette import status

from shared.core.database import get_db
from shared.crud import data_access
from shared.crud.security import get_current_user, hash_password, create_jws_token, security, passwords_match, verify_password
from shared.schemas.schemas import AthleteBase, Challenge
from service.auth_service.app.routes.unauthentificated import logout
from service.auth_service.app.schemas.auth_schemas import UserUpdatePassword
from shared.utils.enums import RolesEnum

app = FastAPI()
router = APIRouter(prefix="/api", tags=["admin"])


@router.put("/user/update/email", summary="ADMIN & ATHLETE & FOOTBALL CLUB: update a user's login email")
def update_email(email: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user), res: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user = data_access.find_user_by_email(db, current_user.get("email"))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        user.email = email
        db.commit()
        db.refresh(user)
        logout(res)
        new_token = create_jws_token(int(current_user.get("sub")), current_user.get("role"), user.email)
        return user, new_token

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists"
        )
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving data to the database"
        )
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        print(f"Unexpected Error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/user/update/password", summary="ADMIN & ATHLETE & FOOTBALL CLUB: update a user's login password")
def update_password(passwords: UserUpdatePassword, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user), res: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user = data_access.find_user_by_email(db, current_user.get("email"))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        if not passwords_match(passwords.new_password, passwords.new_password_confirm):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Passwords don't match"
            )
        is_valid = verify_password(passwords.old_password, user.password_hash)
        if is_valid:
            password_hash = hash_password(passwords.new_password)
            print(user.password_hash, password_hash)

            user.password_hash = password_hash
            db.commit()
            db.refresh(user)
            logout(res)

            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Old password is not correct"
            )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving data to the database"
        )
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        print(f"Unexpected Error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/create/admin", summary="ADMIN: create an admin account")
def create_admin_account(email: str, password: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") not in ["admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don t have access to list of athletes."
        )
    try:
        role = RolesEnum.admin
        password_hash = hash_password(password)

        admin = data_access.create_user(db, email, password_hash, role)

        db.commit()
        db.refresh(admin)
        return admin
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists"
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


@router.get("/athletes", response_model=List[AthleteBase], summary="ADMIN & FOOTBALL CLUB: get all athletes from db")
def get_athletes(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") not in ["admin", "football_club"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don t have access to list of athletes."
        )
    try:
        athletes = data_access.list_athletes(db)
        if not athletes and athletes is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No athletes found."
            )
        return athletes
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )
    except HTTPException as e:
        return e
    except Exception as e:
        print(f"error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error: {e}"
        )


@router.post("/create/challenge", summary="ADMIN: create a new challenge")
def create_challenge(challenge: Challenge, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don t have access to insert a new challenge into db.",
        )
    try:
        new_challenge = data_access.create_challenge(db, challenge)

        db.commit()
        db.refresh(new_challenge)
        return new_challenge

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


@router.delete("/delete/challenge/{challenge_id}", summary="ADMIN: Delete a challenge")
def delete_challenge(challenge_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don t have access to insert a new challenge result into db.",
        )
    try:
        challenge = data_access.get_challenge_by_id(db, challenge_id)
        if challenge is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The challenge to be deleted was not found."
            )
        data_access.delete_from_challenge_table(db, challenge_id)

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


@router.delete("/delete/wipe", summary="ADMIN: Delete db input")
def delete_db_input(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user), res: HTTPAuthorizationCredentials = Depends(security)):
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don t have access to delete db input."
            )
        data_access.delete_all(db)
        logout(res)
        db.commit()
        return "database entries are deleted"
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

