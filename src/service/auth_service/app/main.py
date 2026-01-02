from fastapi import FastAPI, Depends
from starlette import status

from shared.crud.security import security
from .routes import unauthentificated
app = FastAPI(title="API TalentBridge/ AUTH SERVICE")

@app.get("/protected-resource", dependencies=[Depends(security)], status_code=status.HTTP_200_OK)
def protected_router():
    return {"message": "true"}

app.include_router(unauthentificated.router)