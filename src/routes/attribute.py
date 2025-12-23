from fastapi import FastAPI, APIRouter

app = FastAPI()
router = APIRouter(prefix="/api/attribute", tags=["Attribute"])
