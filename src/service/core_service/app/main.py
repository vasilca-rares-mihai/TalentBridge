from fastapi import FastAPI, Depends
from starlette import status

from shared.crud.security import security
from .routes import admin, athlete, football_club
app = FastAPI(title="API TalentBridge/ CORE SERVICE")

@app.get("/protected-resource", dependencies=[Depends(security)], status_code=status.HTTP_200_OK)
def protected_router():
    return {"message": "true"}

app.include_router(admin.router)
app.include_router(athlete.router)
app.include_router(football_club.router)