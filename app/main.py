from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .routes import router

BASE_DIR = Path(__file__).resolve().parent.parent
app = FastAPI(title="ComicCraft — AI Comic Story Creator", version="2.0.0")
app.mount("/static", StaticFiles(directory=str(BASE_DIR/"static")), name="static")
app.include_router(router)
