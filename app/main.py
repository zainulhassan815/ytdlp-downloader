from fastapi import FastAPI
from routes import downloads_router

app = FastAPI()
app.include_router(downloads_router)
