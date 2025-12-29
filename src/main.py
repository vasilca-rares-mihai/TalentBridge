from fastapi import FastAPI, Depends, status
from routes import athlete, attribute, challenge, video, user
from crud.security import security

app = FastAPI(title="API TalentBridge")

@app.get("/protected-resource", dependencies=[Depends(security)], status_code=status.HTTP_200_OK)
def protected_router():
    return {"message": "true"}


app.include_router(athlete.router)
app.include_router(attribute.router)
app.include_router(video.router)
app.include_router(challenge.router)
app.include_router(user.router)


#uvicorn main:app --reload