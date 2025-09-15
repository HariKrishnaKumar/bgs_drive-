from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Path to your frontend folder
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")

# Serve static files if needed (css, js, images inside frontend/static)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/status")
def status():
    return {"online": True}
