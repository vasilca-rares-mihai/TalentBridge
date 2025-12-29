from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from crud import data_access
from core.database import get_db
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from schemas.schemas import AttributeUpdate,AttributeBase
from crud.security import get_current_user
app = FastAPI()
router = APIRouter(prefix="/api/attribute", tags=["Attribute"])

@router.put("/attribute/{id_athlete}", summary="*USER ONLY* update an attribute")
def update_attribute(id_athlete: int, data_updated: AttributeBase, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        athlete = data_access.get_athlete_by_id(db, id_athlete)
        if current_user.get("role") != "admin" and athlete.email != current_user.get("email"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don t have access to update an attribute",
            )
        clean_dict = data_updated.model_dump(exclude_unset=True)
        updated_atribute = data_access.update_attribute(db, id_athlete, clean_dict)
        if not updated_atribute:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute or Athlete not found")
        return updated_atribute

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