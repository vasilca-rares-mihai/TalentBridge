from fastapi import FastAPI, Depends
from starlette import status

from shared.core.database import init_db
from shared.crud.security import get_current_user
from .routes import unauthentificated
app = FastAPI(title="API TalentBridge/ AUTH SERVICE")


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/protected-resource", status_code=status.HTTP_200_OK)
def protected_router(current_user: dict = Depends(get_current_user)):
    return {
        "message": "true",
        "email": current_user.get("email"),
        "role": current_user.get("role"),
        "id": current_user.get("sub")
    }


app.include_router(unauthentificated.router)