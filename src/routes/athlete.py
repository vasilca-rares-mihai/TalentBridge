from fastapi import FastAPI, APIRouter, Depends

app = FastAPI()
router = APIRouter(prefix="/api/athlete", tags=["Athlete"])
