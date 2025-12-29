from fastapi import FastAPI, Depends, status
from routes import unauthenticated, admin, athlete, football_club
from crud.security import security

app = FastAPI(title="API TalentBridge")

@app.get("/protected-resource", dependencies=[Depends(security)], status_code=status.HTTP_200_OK)
def protected_router():
    return {"message": "true"}


app.include_router(unauthenticated.router)
app.include_router(admin.router)
app.include_router(athlete.router)
app.include_router(football_club.router)


#uvicorn main:app --reload