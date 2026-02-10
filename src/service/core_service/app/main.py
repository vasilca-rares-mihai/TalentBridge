from fastapi import FastAPI, Depends
from starlette import status

from shared.crud.security import get_current_user
from .routes import admin, athlete, football_club
app = FastAPI(title="API TalentBridge/ CORE SERVICE")

@app.get("/protected-resource", status_code=status.HTTP_200_OK)
def protected_router(current_user: dict = Depends(get_current_user)):
    return {
        "message": "true",
        "email": current_user.get("email"),
        "role": current_user.get("role"),
        "id": current_user.get("sub")
    }

app.include_router(admin.router)
app.include_router(athlete.router)
app.include_router(football_club.router)