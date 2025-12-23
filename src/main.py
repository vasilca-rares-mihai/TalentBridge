from fastapi import FastAPI
from routes import athlete, attribute, challenge, video

app = FastAPI(title="API TalentBridge")

app.include_router(athlete.router)
app.include_router(attribute.router)
app.include_router(video.router)
app.include_router(challenge.router)