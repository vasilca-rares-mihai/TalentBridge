from sqlalchemy.orm import Session
from crud import data_access
from core.database import get_db
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from schemas.schemas import AttributeUpdate,AttributeBase

app = FastAPI()
router = APIRouter(prefix="/api/attribute", tags=["Attribute"])

@router.put("/attribute/{id_athlete}", summary="update an attribute")
def update_attribute(id_athlete: int, data_updated: AttributeBase, db: Session = Depends(get_db)):
    clean_dict = data_updated.model_dump(exclude_unset=True)

    updated_atribute = data_access.update_attribute(db, id_athlete, clean_dict)
    if not updated_atribute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="error 404")
    return updated_atribute